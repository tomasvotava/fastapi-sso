"""SSO login base dependency
"""
# pylint: disable=too-few-public-methods

import json

from typing import Dict, List, Optional
from uuid import uuid4
from oauthlib.oauth2 import WebApplicationClient
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
import httpx
import pydantic


class SSOLoginError(HTTPException):
    """Raised when any login-related error ocurrs
    (such as when user is not verified or if there was an attempt for fake login)
    """


class OpenID(pydantic.BaseModel):  # pylint: disable=no-member
    """Class (schema) to represent information got from sso provider in a common form."""

    id: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    picture: Optional[str]
    provider: Optional[str]


class SSOBase:
    """Base class (mixin) for all SSO providers"""

    provider = NotImplemented
    client_id: str = NotImplemented
    client_secret: str = NotImplemented
    redirect_uri: str = NotImplemented
    scope: List[str] = NotImplemented
    _oauth_client: Optional[WebApplicationClient] = None
    state: Optional[str] = None

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        allow_insecure_http: bool = False,
        use_state: bool = True,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.allow_insecure_http = allow_insecure_http
        self.use_state = use_state

    @property
    def oauth_client(self) -> WebApplicationClient:
        """OAuth Client to help us generate requests and parse responses"""
        if self.client_id == NotImplemented:
            raise NotImplementedError(f"Provider {self.provider} not supported")
        if self._oauth_client is None:
            self._oauth_client = WebApplicationClient(self.client_id)
        return self._oauth_client

    @property
    def access_token(self) -> Optional[str]:
        """Access token from token endpoint"""
        return self._oauth_client.access_token

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        """Return {OpenID} object from provider's user info endpoint response"""
        raise NotImplementedError(f"Provider {cls.provider} not supported")

    @classmethod
    async def get_discovery_document(cls) -> Dict[str, str]:
        """Get discovery document containing handy urls"""
        raise NotImplementedError(f"Provider {cls.provider} not supported")

    @property
    async def authorization_endpoint(self) -> Optional[str]:
        """Return `authorization_endpoint` from discovery document"""
        discovery = await self.get_discovery_document()
        return discovery.get("authorization_endpoint")

    @property
    async def token_endpoint(self) -> Optional[str]:
        """Return `token_endpoint` from discovery document"""
        discovery = await self.get_discovery_document()
        return discovery.get("token_endpoint")

    @property
    async def userinfo_endpoint(self) -> Optional[str]:
        """Return `userinfo_endpoint` from discovery document"""
        discovery = await self.get_discovery_document()
        return discovery.get("userinfo_endpoint")

    async def get_login_url(self) -> str:
        """Return prepared login url. This is low-level, see {get_login_redirect} instead."""
        if self.use_state:
            self.state = str(uuid4())
        request_uri = self.oauth_client.prepare_request_uri(
            await self.authorization_endpoint, redirect_uri=self.redirect_uri, state=self.state, scope=self.scope
        )
        return request_uri

    async def get_login_redirect(self) -> RedirectResponse:
        """Return redirect response by Stalette to login page of Oauth SSO provider

        Returns:
            RedirectResponse -- Starlette response (may directly be returned from FastAPI)
        """
        login_uri = await self.get_login_url()
        response = RedirectResponse(login_uri, 303)
        if self.state is not None and self.use_state:
            response.set_cookie("ssostate", self.state, expires=600)
        return response

    async def verify_and_process(self, request: Request) -> Optional[OpenID]:
        """Get FastAPI (Starlette) Request object and process login.
        This handler should be used for your /callback path.

        Arguments:
            request {Request} -- FastAPI request object (or Starlette)

        Returns:
            Optional[OpenID] -- OpenID if the login was successfull
        """
        code = request.query_params.get("code")
        if code is None:
            raise SSOLoginError(400, "'code' parameter was not found in callback request")
        if self.state is not None and self.use_state:
            ssostate = request.cookies.get("ssostate")
            if ssostate is None or ssostate != self.state:
                raise SSOLoginError(
                    401,
                    "'state' parameter in callback request does not match our internal 'state', "
                    "someone may be trying to do something bad.",
                )
        return await self.process_login(code, request)

    async def process_login(self, code: str, request: Request) -> Optional[OpenID]:
        """This method should be called from callback endpoint to verify the user and request user info endpoint.
        This is low level, you should use {verify_and_process} instead.
        """
        url = request.url
        scheme = url.scheme
        if not self.allow_insecure_http and scheme != "https":
            current_url = str(url).replace("http://", "https://")
            scheme = "https"
        else:
            current_url = str(url)
        current_path = f"{scheme}://{url.netloc}{url.path}"

        token_url, headers, body = self.oauth_client.prepare_token_request(
            await self.token_endpoint, authorization_response=current_url, redirect_url=current_path, code=code
        )  # type: ignore

        if token_url is None:
            return None

        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with httpx.AsyncClient() as session:
            response = await session.post(token_url, headers=headers, content=body, auth=auth)
            content = response.json()
            self.oauth_client.parse_request_body_response(json.dumps(content))

            uri, headers, _ = self.oauth_client.add_token(await self.userinfo_endpoint)
            response = await session.get(uri, headers=headers)
            content = response.json()

        return await self.openid_from_response(content)

"""SSO login base dependency
"""
# pylint: disable=too-few-public-methods

import json
import os
import sys
import warnings
from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union

import httpx
import pydantic
from oauthlib.oauth2 import WebApplicationClient
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict  # pragma: no cover

DiscoveryDocument = TypedDict(
    "DiscoveryDocument", {"authorization_endpoint": str, "token_endpoint": str, "userinfo_endpoint": str}
)


class UnsetStateWarning(UserWarning):
    """Warning about unset state parameter"""


class ReusedOauthClientWarning(UserWarning):
    """Warning about reused oauth client instance"""


class SSOLoginError(HTTPException):
    """Raised when any login-related error ocurrs
    (such as when user is not verified or if there was an attempt for fake login)
    """


class OpenID(pydantic.BaseModel):  # pylint: disable=no-member
    """Class (schema) to represent information got from sso provider in a common form."""

    id: Optional[str] = None
    email: Optional[pydantic.EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    picture: Optional[str] = None
    provider: Optional[str] = None


# pylint: disable=too-many-instance-attributes
class SSOBase:
    """Base class (mixin) for all SSO providers"""

    provider: str = NotImplemented
    client_id: str = NotImplemented
    client_secret: str = NotImplemented
    redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = NotImplemented
    scope: List[str] = NotImplemented
    additional_headers: Optional[Dict[str, Any]] = None

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = None,
        allow_insecure_http: bool = False,
        use_state: bool = False,
        scope: Optional[List[str]] = None,
    ):
        # pylint: disable=too-many-arguments
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = redirect_uri
        self.allow_insecure_http: bool = allow_insecure_http
        self._oauth_client: Optional[WebApplicationClient] = None

        if self.allow_insecure_http:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # TODO: Remove use_state argument and attribute
        if use_state:
            warnings.warn(
                (
                    "Argument 'use_state' of SSOBase's constructor is deprecated and will be removed in "
                    "future releases. Use 'state' argument of individual methods instead."
                ),
                DeprecationWarning,
            )
        self.scope = scope or self.scope
        self._refresh_token: Optional[str] = None
        self._state: Optional[str] = None

    @property
    def state(self) -> Optional[str]:
        """
        Retrieves the state as it was returned from the server.

        Warning:
            This will emit a warning if the state is unset, implying either that
            the server didn't return a state or `verify_and_process` hasn't been
            called yet.

        Returns:
            Optional[str]: The state parameter returned from the server.
        """
        if self._state is None:
            warnings.warn(
                "'state' parameter is unset. This means the server either "
                "didn't return state (was this expected?) or 'verify_and_process' hasn't been called yet.",
                UnsetStateWarning,
            )
        return self._state

    @property
    def oauth_client(self) -> WebApplicationClient:
        """
        Retrieves the OAuth Client to aid in generating requests and parsing responses.

        Raises:
            NotImplementedError: If the provider is not supported or `client_id` is not set.

        Returns:
            WebApplicationClient: OAuth client instance.
        """
        if self.client_id == NotImplemented:
            raise NotImplementedError(f"Provider {self.provider} not supported")  # pragma: no cover
        if self._oauth_client is None:
            self._oauth_client = WebApplicationClient(self.client_id)
        return self._oauth_client

    @property
    def access_token(self) -> Optional[str]:
        """
        Retrieves the access token from token endpoint.

        Returns:
            Optional[str]: The access token if available.
        """
        return self.oauth_client.access_token

    @property
    def refresh_token(self) -> Optional[str]:
        """
        Retrieves the refresh token if returned from provider.

        Returns:
            Optional[str]: The refresh token if available.
        """
        return self._refresh_token or self.oauth_client.refresh_token

    async def openid_from_response(self, response: dict, session: Optional[httpx.AsyncClient] = None) -> OpenID:
        """
        Converts a response from the provider's user info endpoint to an OpenID object.

        Args:
            response (dict): The response from the user info endpoint.
            session (Optional[httpx.AsyncClient]): The HTTPX AsyncClient session.

        Raises:
            NotImplementedError: If the provider is not supported.

        Returns:
            OpenID: The user information in a standardized format.
        """
        raise NotImplementedError(f"Provider {self.provider} not supported")

    async def get_discovery_document(self) -> DiscoveryDocument:
        """
        Retrieves the discovery document containing useful URLs.

        Raises:
            NotImplementedError: If the provider is not supported.

        Returns:
            DiscoveryDocument: A dictionary containing important endpoints like authorization, token and userinfo.
        """
        raise NotImplementedError(f"Provider {self.provider} not supported")

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

    async def get_login_url(
        self,
        *,
        redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        state: Optional[str] = None,
    ) -> str:
        """
        Generates and returns the prepared login URL.

        Args:
            redirect_uri (Optional[str]): Overrides the `redirect_uri` specified on this instance.
            params (Optional[Dict[str, Any]]): Additional query parameters to add to the login request.
            state (Optional[str]): The state parameter for the OAuth 2.0 authorization request.

        Raises:
            ValueError: If `redirect_uri` is not provided either at construction or request time.

        Returns:
            str: The prepared login URL.
        """
        params = params or {}
        redirect_uri = redirect_uri or self.redirect_uri
        if redirect_uri is None:
            raise ValueError("redirect_uri must be provided, either at construction or request time")
        request_uri = self.oauth_client.prepare_request_uri(
            await self.authorization_endpoint, redirect_uri=redirect_uri, state=state, scope=self.scope, **params
        )
        return request_uri

    async def get_login_redirect(
        self,
        *,
        redirect_uri: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        state: Optional[str] = None,
    ) -> RedirectResponse:
        """
        Constructs and returns a redirect response to the login page of OAuth SSO provider.

        Args:
            redirect_uri (Optional[str]): Overrides the `redirect_uri` specified on this instance.
            params (Optional[Dict[str, Any]]): Additional query parameters to add to the login request.
            state (Optional[str]): The state parameter for the OAuth 2.0 authorization request.

        Returns:
            RedirectResponse: A Starlette response directing to the login page of the OAuth SSO provider.
        """
        login_uri = await self.get_login_url(redirect_uri=redirect_uri, params=params, state=state)
        response = RedirectResponse(login_uri, 303)
        return response

    async def verify_and_process(
        self,
        request: Request,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        redirect_uri: Optional[str] = None,
    ) -> Optional[OpenID]:
        """
        Processes the login given a FastAPI (Starlette) Request object. This should be used for the /callback path.

        Args:
            request (Request): FastAPI or Starlette request object.
            params (Optional[Dict[str, Any]]): Additional query parameters to pass to the provider.
            headers (Optional[Dict[str, Any]]): Additional headers to pass to the provider.
            redirect_uri (Optional[str]): Overrides the `redirect_uri` specified on this instance.

        Raises:
            SSOLoginError: If the 'code' parameter is not found in the callback request.

        Returns:
            Optional[OpenID]: User information in OpenID format if the login was successful.
        """
        headers = headers or {}
        code = request.query_params.get("code")
        if code is None:
            raise SSOLoginError(400, "'code' parameter was not found in callback request")
        self._state = request.query_params.get("state")
        return await self.process_login(
            code, request, params=params, additional_headers=headers, redirect_uri=redirect_uri
        )

    def __enter__(self) -> "SSOBase":
        self._oauth_client = None
        self._refresh_token = None
        return self

    def __exit__(
        self,
        _exc_type: Optional[Type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        return None

    async def process_login(
        self,
        code: str,
        request: Request,
        *,
        params: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, Any]] = None,
        redirect_uri: Optional[str] = None,
    ) -> Optional[OpenID]:
        """
        Processes login from the callback endpoint to verify the user and request user info endpoint.
        It's a lower-level method, typically, you should use `verify_and_process` instead.

        Args:
            code (str): The authorization code.
            request (Request): FastAPI or Starlette request object.
            params (Optional[Dict[str, Any]]): Additional query parameters to pass to the provider.
            additional_headers (Optional[Dict[str, Any]]): Additional headers to be added to all requests.
            redirect_uri (Optional[str]): Overrides the `redirect_uri` specified on this instance.

        Raises:
            ReusedOauthClientWarning: If the SSO object is reused, which is not safe and caused security issues.

        Returns:
            Optional[OpenID]: User information in OpenID format if the login was successful.
        """
        # pylint: disable=too-many-locals
        if self._oauth_client is not None:  # pragma: no cover
            self._oauth_client = None
            self._refresh_token = None
            warnings.warn(
                (
                    "Reusing the SSO object is not safe and caused a security issue in previous versions."
                    "To make sure you don't see this warning, please use the SSO object as a context manager."
                ),
                ReusedOauthClientWarning,
            )
        params = params or {}
        additional_headers = additional_headers or {}
        additional_headers.update(self.additional_headers or {})

        url = request.url

        if not self.allow_insecure_http and url.scheme != "https":
            current_url = str(url).replace("http://", "https://")
        else:
            current_url = str(url)

        current_path = f"{url.scheme}://{url.netloc}{url.path}"

        token_url, headers, body = self.oauth_client.prepare_token_request(
            await self.token_endpoint,
            authorization_response=current_url,
            redirect_url=redirect_uri or self.redirect_uri or current_path,
            code=code,
            **params,
        )  # type: ignore

        if token_url is None:  # pragma: no cover
            return None

        headers.update(additional_headers)

        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with httpx.AsyncClient() as session:
            response = await session.post(token_url, headers=headers, content=body, auth=auth)
            content = response.json()
            self._refresh_token = content.get("refresh_token")
            self.oauth_client.parse_request_body_response(json.dumps(content))

            uri, headers, _ = self.oauth_client.add_token(await self.userinfo_endpoint)
            headers.update(additional_headers)
            session.headers.update(headers)
            response = await session.get(uri)
            content = response.json()

            return await self.openid_from_response(content, session)

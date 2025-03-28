"""SSO login base dependency."""

import asyncio
import json
import logging
import os
import sys
import warnings
from types import TracebackType
from typing import Any, ClassVar, Literal, Optional, TypedDict, TypeVar, Union, overload

import httpx
import jwt
import pydantic
from oauthlib.oauth2 import WebApplicationClient
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from fastapi_sso.pkce import get_pkce_challenge_pair
from fastapi_sso.state import generate_random_state

if sys.version_info < (3, 10):
    from typing import Callable  # pragma: no cover

    from typing_extensions import ParamSpec  # pragma: no cover
else:
    from collections.abc import Callable
    from typing import ParamSpec

logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")


def _decode_id_token(id_token: str, verify: bool = False) -> dict:
    return jwt.decode(id_token, options={"verify_signature": verify})


class DiscoveryDocument(TypedDict):
    """Discovery document."""

    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str


class UnsetStateWarning(UserWarning):
    """Warning about unset state parameter."""


class ReusedOauthClientWarning(UserWarning):
    """Warning about reused oauth client instance."""


class SSOLoginError(HTTPException):
    """Raised when any login-related error ocurrs.

    Such as when user is not verified or if there was an attempt for fake login.
    """


class OpenID(pydantic.BaseModel):
    """Class (schema) to represent information got from sso provider in a common form."""

    id: Optional[str] = None
    email: Optional[pydantic.EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    picture: Optional[str] = None
    provider: Optional[str] = None


class SecurityWarning(UserWarning):
    """Raised when insecure usage is detected"""


def requires_async_context(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if not args or not isinstance(args[0], SSOBase):
            return func(*args, **kwargs)
        if not args[0]._in_stack:
            warnings.warn(
                "Please make sure you are using SSO provider in an async context (using 'async with provider:'). "
                "See https://github.com/tomasvotava/fastapi-sso/issues/186 for more information.",
                category=SecurityWarning,
                stacklevel=1,
            )
        return func(*args, **kwargs)

    return wrapper


class SSOBase:
    """Base class for all SSO providers."""

    provider: str = NotImplemented
    client_id: str = NotImplemented
    client_secret: str = NotImplemented
    redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = NotImplemented
    scope: ClassVar[list[str]] = []
    additional_headers: ClassVar[Optional[dict[str, Any]]] = None
    uses_pkce: bool = False
    requires_state: bool = False
    use_id_token_for_user_info: ClassVar[bool] = False

    _pkce_challenge_length: int = 96

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = None,
        allow_insecure_http: bool = False,
        use_state: bool = False,
        scope: Optional[list[str]] = None,
    ):
        """Base class (mixin) for all SSO providers."""
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = redirect_uri
        self.allow_insecure_http: bool = allow_insecure_http
        self._login_lock = asyncio.Lock()
        self._in_stack = False
        self._oauth_client: Optional[WebApplicationClient] = None
        self._generated_state: Optional[str] = None

        if self.allow_insecure_http:
            logger.debug("Initializing %s with allow_insecure_http=True", self.__class__.__name__)
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
        self._scope = scope or self.scope
        self._refresh_token: Optional[str] = None
        self._id_token: Optional[str] = None
        self._state: Optional[str] = None
        self._pkce_code_challenge: Optional[str] = None
        self._pkce_code_verifier: Optional[str] = None
        self._pkce_challenge_method = "S256"

    @property
    def state(self) -> Optional[str]:
        """Retrieves the state as it was returned from the server.

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
    @requires_async_context
    def oauth_client(self) -> WebApplicationClient:
        """Retrieves the OAuth Client to aid in generating requests and parsing responses.

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
    @requires_async_context
    def access_token(self) -> Optional[str]:
        """Retrieves the access token from token endpoint.

        Returns:
            Optional[str]: The access token if available.
        """
        return self.oauth_client.access_token

    @property
    @requires_async_context
    def refresh_token(self) -> Optional[str]:
        """Retrieves the refresh token if returned from provider.

        Returns:
            Optional[str]: The refresh token if available.
        """
        return self._refresh_token or self.oauth_client.refresh_token

    @property
    @requires_async_context
    def id_token(self) -> Optional[str]:
        """Retrieves the id token if returned from provider.

        Returns:
            Optional[str]: The id token if available.
        """
        return self._id_token

    async def openid_from_response(self, response: dict, session: Optional[httpx.AsyncClient] = None) -> OpenID:
        """Converts a response from the provider's user info endpoint to an OpenID object.

        Args:
            response (dict): The response from the user info endpoint.
            session (Optional[httpx.AsyncClient]): The HTTPX AsyncClient session.

        Raises:
            NotImplementedError: If the provider is not supported.

        Returns:
            OpenID: The user information in a standardized format.
        """
        raise NotImplementedError(f"Provider {self.provider} not supported")

    async def openid_from_token(self, id_token: dict, session: Optional[httpx.AsyncClient] = None) -> OpenID:
        """Converts an ID token from the provider's token endpoint to an OpenID object.

        Args:
            id_token (dict): The id token data retrieved from the token endpoint.
            session: (Optional[httpx.AsyncClient]): The HTTPX AsyncClient session.

        Returns:
            OpenID: The user information in a standardized format.
        """
        raise NotImplementedError(f"Provider {self.provider} not supported")

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Retrieves the discovery document containing useful URLs.

        Raises:
            NotImplementedError: If the provider is not supported.

        Returns:
            DiscoveryDocument: A dictionary containing important endpoints like authorization, token and userinfo.
        """
        raise NotImplementedError(f"Provider {self.provider} not supported")

    @property
    async def authorization_endpoint(self) -> Optional[str]:
        """Return `authorization_endpoint` from discovery document."""
        discovery = await self.get_discovery_document()
        return discovery.get("authorization_endpoint")

    @property
    async def token_endpoint(self) -> Optional[str]:
        """Return `token_endpoint` from discovery document."""
        discovery = await self.get_discovery_document()
        return discovery.get("token_endpoint")

    @property
    async def userinfo_endpoint(self) -> Optional[str]:
        """Return `userinfo_endpoint` from discovery document."""
        discovery = await self.get_discovery_document()
        return discovery.get("userinfo_endpoint")

    async def get_login_url(
        self,
        *,
        redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = None,
        params: Optional[dict[str, Any]] = None,
        state: Optional[str] = None,
    ) -> str:
        """Generates and returns the prepared login URL.

        Args:
            redirect_uri (Optional[str]): Overrides the `redirect_uri` specified on this instance.
            params (Optional[dict[str, Any]]): Additional query parameters to add to the login request.
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
        if self.uses_pkce and not all((self._pkce_code_verifier, self._pkce_code_challenge)):
            warnings.warn(
                f"{self.__class__.__name__!r} uses PKCE and no code was generated yet. "
                "Use SSO class as a context manager to get rid of this warning and possible errors."
            )
        if self.requires_state and not state:
            if self._generated_state is None:
                warnings.warn(
                    f"{self.__class__.__name__!r} requires state in the request but none was provided nor "
                    "generated automatically. Use SSO as a context manager. The login process will most probably fail."
                )
            state = self._generated_state
        request_uri = self.oauth_client.prepare_request_uri(
            await self.authorization_endpoint,
            redirect_uri=redirect_uri,
            state=state,
            scope=self._scope,
            code_challenge=self._pkce_code_challenge,
            code_challenge_method=self._pkce_challenge_method,
            **params,
        )
        return request_uri

    async def get_login_redirect(
        self,
        *,
        redirect_uri: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        state: Optional[str] = None,
    ) -> RedirectResponse:
        """Constructs and returns a redirect response to the login page of OAuth SSO provider.

        Args:
            redirect_uri (Optional[str]): Overrides the `redirect_uri` specified on this instance.
            params (Optional[dict[str, Any]]): Additional query parameters to add to the login request.
            state (Optional[str]): The state parameter for the OAuth 2.0 authorization request.

        Returns:
            RedirectResponse: A Starlette response directing to the login page of the OAuth SSO provider.
        """
        if self.requires_state and not state:
            state = self._generated_state
        login_uri = await self.get_login_url(redirect_uri=redirect_uri, params=params, state=state)
        response = RedirectResponse(login_uri, 303)
        if self.uses_pkce:
            response.set_cookie("pkce_code_verifier", str(self._pkce_code_verifier))
        return response

    @overload
    async def verify_and_process(
        self,
        request: Request,
        *,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, Any]] = None,
        redirect_uri: Optional[str] = None,
        convert_response: Literal[True] = True,
    ) -> Optional[OpenID]: ...

    @overload
    async def verify_and_process(
        self,
        request: Request,
        *,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, Any]] = None,
        redirect_uri: Optional[str] = None,
        convert_response: Literal[False],
    ) -> Optional[dict[str, Any]]: ...

    @requires_async_context
    async def verify_and_process(
        self,
        request: Request,
        *,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, Any]] = None,
        redirect_uri: Optional[str] = None,
        convert_response: Union[Literal[True], Literal[False]] = True,
    ) -> Union[Optional[OpenID], Optional[dict[str, Any]]]:
        """Processes the login given a FastAPI (Starlette) Request object. This should be used for the /callback path.

        Args:
            request (Request): FastAPI or Starlette request object.
            params (Optional[dict[str, Any]]): Additional query parameters to pass to the provider.
            headers (Optional[dict[str, Any]]): Additional headers to pass to the provider.
            redirect_uri (Optional[str]): Overrides the `redirect_uri` specified on this instance.
            convert_response (bool): If True, userinfo response is converted to OpenID object.

        Raises:
            SSOLoginError: If the 'code' parameter is not found in the callback request.

        Returns:
            Optional[OpenID]: User information as OpenID instance (if convert_response == True)
            Optional[dict[str, Any]]: The original JSON response from the API.
        """
        headers = headers or {}
        code = request.query_params.get("code")
        if code is None:
            logger.debug(
                "Callback request:\n\tURI: %s\n\tHeaders: %s\n\tQuery params: %s",
                request.url,
                request.headers,
                request.query_params,
            )
            raise SSOLoginError(400, "'code' parameter was not found in callback request")
        self._state = request.query_params.get("state")
        pkce_code_verifier: Optional[str] = None
        if self.uses_pkce:
            pkce_code_verifier = request.cookies.get("pkce_code_verifier")
            if pkce_code_verifier is None:
                warnings.warn(
                    "PKCE code verifier was not found in the request Cookie. This will probably lead to a login error."
                )
        return await self.process_login(
            code,
            request,
            params=params,
            additional_headers=headers,
            redirect_uri=redirect_uri,
            pkce_code_verifier=pkce_code_verifier,
            convert_response=convert_response,
        )

    def __enter__(self) -> "SSOBase":
        warnings.warn(
            "SSO Providers are supposed to be used in async context, please change 'with provider' to "
            "'async with provider'. See https://github.com/tomasvotava/fastapi-sso/issues/186 for more information.",
            DeprecationWarning,
            stacklevel=1,
        )
        self._oauth_client = None
        self._refresh_token = None
        self._id_token = None
        self._state = None
        if self.requires_state:
            self._generated_state = generate_random_state()
        if self.uses_pkce:
            self._pkce_code_verifier, self._pkce_code_challenge = get_pkce_challenge_pair(self._pkce_challenge_length)
        return self

    async def __aenter__(self) -> "SSOBase":
        await self._login_lock.acquire()
        self._in_stack = True
        self._oauth_client = None
        self._refresh_token = None
        self._id_token = None
        self._state = None
        if self.requires_state:
            self._generated_state = generate_random_state()
        if self.uses_pkce:
            self._pkce_code_verifier, self._pkce_code_challenge = get_pkce_challenge_pair(self._pkce_challenge_length)
        return self

    async def __aexit__(
        self,
        _exc_type: Optional[type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        self._in_stack = False
        self._login_lock.release()

    def __exit__(
        self,
        _exc_type: Optional[type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        return None

    @property
    def _extra_query_params(self) -> dict:
        return {}

    @overload
    async def process_login(
        self,
        code: str,
        request: Request,
        *,
        params: Optional[dict[str, Any]] = None,
        additional_headers: Optional[dict[str, Any]] = None,
        redirect_uri: Optional[str] = None,
        pkce_code_verifier: Optional[str] = None,
        convert_response: Literal[True] = True,
    ) -> Optional[OpenID]: ...

    @overload
    async def process_login(
        self,
        code: str,
        request: Request,
        *,
        params: Optional[dict[str, Any]] = None,
        additional_headers: Optional[dict[str, Any]] = None,
        redirect_uri: Optional[str] = None,
        pkce_code_verifier: Optional[str] = None,
        convert_response: Literal[False],
    ) -> Optional[dict[str, Any]]: ...

    @requires_async_context
    async def process_login(
        self,
        code: str,
        request: Request,
        *,
        params: Optional[dict[str, Any]] = None,
        additional_headers: Optional[dict[str, Any]] = None,
        redirect_uri: Optional[str] = None,
        pkce_code_verifier: Optional[str] = None,
        convert_response: Union[Literal[True], Literal[False]] = True,
    ) -> Union[Optional[OpenID], Optional[dict[str, Any]]]:
        """Processes login from the callback endpoint to verify the user and request user info endpoint.
        It's a lower-level method, typically, you should use `verify_and_process` instead.

        Args:
            code (str): The authorization code.
            request (Request): FastAPI or Starlette request object.
            params (Optional[dict[str, Any]]): Additional query parameters to pass to the provider.
            additional_headers (Optional[dict[str, Any]]): Additional headers to be added to all requests.
            redirect_uri (Optional[str]): Overrides the `redirect_uri` specified on this instance.
            pkce_code_verifier (Optional[str]): A PKCE code verifier sent to the server to verify the login request.
            convert_response (bool): If True, userinfo response is converted to OpenID object.

        Raises:
            ReusedOauthClientWarning: If the SSO object is reused, which is not safe and caused security issues.

        Returns:
            Optional[OpenID]: User information in OpenID format if the login was successful (convert_response == True).
            Optional[dict[str, Any]]: Original userinfo API endpoint response.
        """
        if self._oauth_client is not None:  # pragma: no cover
            self._oauth_client = None
            self._refresh_token = None
            self._id_token = None
            warnings.warn(
                (
                    "Reusing the SSO object is not safe and caused a security issue in previous versions."
                    "To make sure you don't see this warning, please use the SSO object as a context manager."
                ),
                ReusedOauthClientWarning,
            )
        params = params or {}
        params.update(self._extra_query_params)
        additional_headers = additional_headers or {}
        additional_headers.update(self.additional_headers or {})

        url = request.url

        if not self.allow_insecure_http and url.scheme != "https":
            current_url = str(url).replace("http://", "https://")
        else:
            current_url = str(url)

        current_path = f"{url.scheme}://{url.netloc}{url.path}"

        if pkce_code_verifier:
            params.update({"code_verifier": pkce_code_verifier})

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
            self._id_token = content.get("id_token")
            self.oauth_client.parse_request_body_response(json.dumps(content))

            uri, headers, _ = self.oauth_client.add_token(await self.userinfo_endpoint)
            headers.update(additional_headers)
            session.headers.update(headers)
            response = await session.get(uri)
            content = response.json()
            if convert_response:
                if self.use_id_token_for_user_info:
                    if not self._id_token:
                        raise SSOLoginError(401, f"Provider {self.provider!r} did not return id token.")
                    return await self.openid_from_token(_decode_id_token(self._id_token), session)
                return await self.openid_from_response(content, session)
            return content

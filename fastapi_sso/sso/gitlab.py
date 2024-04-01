"""Gitlab SSO Oauth Helper class"""

from typing import TYPE_CHECKING, Any, List, Optional, Union

import pydantic

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class GitlabSSO(SSOBase):
    """Class providing login via Gitlab SSO"""

    provider = "gitlab"
    scope = ["read_user", "openid", "profile"]
    additional_headers = {"accept": "application/json"}
    base_endpoint_url = "https://gitlab.com"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_endpoint_url: Optional[Union[pydantic.AnyHttpUrl, str]] = None,
        redirect_uri: Any | str | None = None,
        allow_insecure_http: bool = False,
        use_state: bool = False,  # TODO: Remove use_state argument
        scope: List[str] | None = None,
    ) -> None:
        super().__init__(
            client_id,
            client_secret,
            redirect_uri,
            allow_insecure_http,
            use_state,  # TODO: Remove use_state argument
            scope,
        )
        self.base_endpoint_url = base_endpoint_url or self.base_endpoint_url

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": f"{self.base_endpoint_url}/oauth/authorize",
            "token_endpoint": f"{self.base_endpoint_url}/oauth/token",
            "userinfo_endpoint": f"{self.base_endpoint_url}/api/v4/user",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        return OpenID(
            email=response["email"],
            provider=self.provider,
            id=str(response["id"]),
            display_name=response["username"],
            picture=response["avatar_url"],
        )

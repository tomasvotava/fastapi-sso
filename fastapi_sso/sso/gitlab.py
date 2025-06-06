"""Gitlab SSO Oauth Helper class."""

from typing import TYPE_CHECKING, ClassVar, Optional, Union
from urllib.parse import urljoin

import pydantic

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class GitlabSSO(SSOBase):
    """Class providing login via Gitlab SSO."""

    provider = "gitlab"
    scope: ClassVar = ["read_user", "openid", "profile"]
    additional_headers: ClassVar = {"accept": "application/json"}
    base_endpoint_url = "https://gitlab.com"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = None,
        allow_insecure_http: bool = False,
        use_state: bool = False,  # TODO: Remove use_state argument
        scope: Optional[list[str]] = None,
        base_endpoint_url: Optional[str] = None,
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
        """Override the discovery document method to return Yandex OAuth endpoints."""
        return {
            "authorization_endpoint": urljoin(self.base_endpoint_url, "/oauth/authorize"),
            "token_endpoint": urljoin(self.base_endpoint_url, "/oauth/token"),
            "userinfo_endpoint": urljoin(self.base_endpoint_url, "/api/v4/user"),
        }

    def _parse_name(self, full_name: Optional[str]) -> tuple[Union[str, None], Union[str, None]]:
        """Parses the full name from Gitlab into the first and last name."""
        if not full_name or not isinstance(full_name, str):
            return None, None

        name_parts = full_name.split()

        if len(name_parts) == 1:
            return name_parts[0], None

        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])
        return first_name, last_name

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        """Converts Gitlab user info response to OpenID object."""
        first_name, last_name = self._parse_name(response.get("name"))

        return OpenID(
            email=response["email"],
            provider=self.provider,
            id=str(response["id"]),
            first_name=first_name,
            last_name=last_name,
            display_name=response["username"],
            picture=response["avatar_url"],
        )

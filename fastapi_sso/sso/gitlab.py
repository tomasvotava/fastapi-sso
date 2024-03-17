"""Gitlab SSO Oauth Helper class"""

from typing import TYPE_CHECKING, Optional

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class GitlabSSO(SSOBase):
    """Class providing login via Gitlab SSO"""

    provider = "gitlab"
    scope = ["read_user", "openid", "profile"]
    additional_headers = {"accept": "application/json"}

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://gitlab.com/oauth/authorize",
            "token_endpoint": "https://gitlab.com/oauth/token",
            "userinfo_endpoint": "https://gitlab.com/api/v4/user",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        return OpenID(
            email=response["email"],
            provider=self.provider,
            id=response["id"],
            display_name=response["username"],
            picture=response["avatar_url"],
        )

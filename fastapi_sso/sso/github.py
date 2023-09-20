"""Github SSO Oauth Helper class"""

from typing import TYPE_CHECKING, Optional

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx


class GithubSSO(SSOBase):
    """Class providing login via Github SSO"""

    provider = "github"
    scope = ["user:email"]
    additional_headers = {"accept": "application/json"}

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://github.com/login/oauth/authorize",
            "token_endpoint": "https://github.com/login/oauth/access_token",
            "userinfo_endpoint": "https://api.github.com/user",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        return OpenID(
            email=response["email"],
            provider=self.provider,
            id=str(response["id"]),
            display_name=response["login"],
            picture=response["avatar_url"],
        )

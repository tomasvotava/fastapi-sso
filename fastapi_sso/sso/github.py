"""Github SSO Oauth Helper class"""

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase


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

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        return OpenID(
            email=response["email"],
            provider=cls.provider,
            id=response["id"],
            display_name=response["login"],
            picture=response["avatar_url"],
        )

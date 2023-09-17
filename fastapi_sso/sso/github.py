"""Github SSO Oauth Helper class"""

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase, SSOLoginError 


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
            "emails_endpoint": "https://api.github.com/user/emails",
        }


    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:

        # if the email is empty then it means that the user has set it has private
        # so the email must be retrieved using emails_endopoint.
        # This endpoint return the list of all the email addresses.
        if response["email"] is None:
            raise SSOLoginError(401, "Failed to process login via GitHub, please set your email as public in GitHub settings")

        return OpenID(
            email=response["email"],
            provider=cls.provider,
            id=response["id"],
            display_name=response["login"],
            picture=response["avatar_url"],
        )

"""Github SSO Oauth Helper class"""

from typing import TYPE_CHECKING, Optional

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase, SSOLoginError

if TYPE_CHECKING:
    import httpx


class GithubSSO(SSOBase):
    """Class providing login via Github SSO"""

    provider = "github"
    scope = ["user:email"]
    additional_headers = {"accept": "application/json"}
    emails_endpoint = "https://api.github.com/user/emails"

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://github.com/login/oauth/authorize",
            "token_endpoint": "https://github.com/login/oauth/access_token",
            "userinfo_endpoint": "https://api.github.com/user",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        # if the email is empty then it means that the user has set it has private
        # so the email must be retrieved using emails_endopoint.
        # This endpoint return the list of all the email addresses.
        if response["email"] is None:
            if session is None:
                raise SSOLoginError(401, "Failed to process login via GitHub")

            uri, headers, _ = self.oauth_client.add_token(self.emails_endpoint)
            email_response = await session.get(uri, headers=headers)
            emails = email_response.json()
            for email in emails:
                if email["primary"]:
                    response["email"] = email["email"]
                    break

        if response["email"] is None:
            raise SSOLoginError(401, "Failed to process login via GitHub")

        return OpenID(
            email=response["email"],
            provider=self.provider,
            id=str(response["id"]),
            display_name=response["login"],
            picture=response["avatar_url"],
        )

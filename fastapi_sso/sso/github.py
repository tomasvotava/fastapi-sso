"""Github SSO Oauth Helper class"""


from typing import Dict, Optional
import httpx

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase, SSOLoginError

class GithubSSO(SSOBase):
    """Class providing login via Github SSO"""

    provider = "github"
    scope = ["user:email"]
    additional_headers = {"accept": "application/json"}

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://github.com/login/oauth/authorize",
            "emails_endpoint": "https://api.github.com/user/emails",
            "token_endpoint": "https://github.com/login/oauth/access_token",
            "userinfo_endpoint": "https://api.github.com/user",
        }

    @property
    async def emails_endpoint(self) -> Optional[str]:
        """Return `emails_endpoint` from discovery document"""
        discovery = await self.get_discovery_document()
        return discovery.get("emails_endpoint")

    async def get_extra_data(self, content: Dict, session: httpx.AsyncClient) -> Dict:
        # if the email is empty then it means that the user has set it has private
        # so the email must be retrieved using emails_endopoint.
        # This endpoint return the list of all the email addresses.
        if content["email"] is not None:
            return content

        uri, headers, _ = self.oauth_client.add_token(await self.emails_endpoint)
        email_response = await session.get(uri, headers=headers)
        emails = email_response.json()
        for email in emails:
            if email["primary"]:
                content["email"] = email["email"]
                break

        return content

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        if response["email"] is None:
            raise SSOLoginError(401, "Failed to process login via GitHub")

        return OpenID(
            email=response["email"],
            provider=cls.provider,
            id=response["id"],
            display_name=response["login"],
            picture=response["avatar_url"],
        )

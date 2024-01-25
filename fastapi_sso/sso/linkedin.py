"""LinkedIn SSO Oauth Helper class"""

from typing import TYPE_CHECKING, Optional

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx


class LinkedInSSO(SSOBase):
    """Class providing login via LinkedIn SSO"""

    provider = "linkedin"
    scope = ["openid", "profile", "email"]
    additional_headers = {"accept": "application/json"}

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://www.linkedin.com/oauth/v2/authorization",
            "token_endpoint": "https://www.linkedin.com/oauth/v2/accessToken",
            "userinfo_endpoint": "https://api.linkedin.com/v2/userinfo",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        """Response format
        sub	Subject Identifier	Text
        name	Full name	Text
        given_name	Member's first name	Text
        family_name	Member's last name	Text
        picture	Member's profile picture URL	Text
        locale	Member's locale	dict {'country': str, 'language': str}
        email	Member's primary e-mail address.	Text
        email_verified	Indicator that Member's primary email has been verified	Boolean
        """
        return OpenID(
            email=response.get("email"),
            provider=self.provider,
            id=response["sub"],
            first_name=response["given_name"],
            last_name=response["family_name"],
            picture=response["picture"],
        )

"""Microsoft SSO Oauth Helper class"""

from typing import Dict

from fastapi_sso.sso.base import OpenID, SSOBase


class MicrosoftSSO(SSOBase):
    """Class providing login via Microsoft Graph OAuth"""

    provider = "microsoft"
    scope = ["email", "openid", "profile"]
    version = "v1.0"

    @classmethod
    async def get_discovery_document(cls) -> Dict[str, str]:
        """Get document containing handy urls"""
        return {
            "authorization_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "userinfo_endpoint": f"https://graph.microsoft.com/{cls.version}/me",
        }

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        """Return OpenID from user information provided by Microsoft Office 365"""
        return OpenID(
            first_name=response.get("givenName"),
            last_name=response.get("surname"),
            email=response.get("userPrincipalName", ""),
            provider=cls.provider,
            id=response.get("id"),
            display_name=response.get("displayName"),
            picture=None,
        )

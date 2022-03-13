"""Microsoft SSO Oauth Helper class"""

from typing import Dict

from fastapi_sso.sso.base import OpenID, SSOBase


class MicrosoftSSO(SSOBase):
    """Class providing login via Microsoft Graph OAuth"""

    provider = "microsoft"
    scope = ["openid", "User.read"]
    version = "v1.0"

    async def get_discovery_document(self) -> Dict[str, str]:
        """Get document containing handy urls"""
        return {
            "authorization_endpoint": f"https://login.microsoftonline.com/{self.client_tenant}/oauth2/v2.0/authorize",
            "token_endpoint": f"https://login.microsoftonline.com/{self.client_tenant}/oauth2/v2.0/token",
            "userinfo_endpoint": f"https://graph.microsoft.com/{self.version}/me",
        }

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        """Return OpenID from user information provided by Microsoft Office 365"""
        return OpenID(
            displayName=response.get("displayName"),
            givenName=response.get("givenName"),
            jobTitle=response.get("jobTitle"),
            mail=response.get("mail"),
        )

"""Google SSO Login Helper
"""

from typing import Dict
import httpx

from fastapi_sso.sso.base import OpenID, SSOBase, SSOLoginError


class GoogleSSO(SSOBase):
    """Class providing login via Facebook OAuth"""

    discovery_url = "https://accounts.google.com/.well-known/openid-configuration"
    provider = "google"
    scope = ["openid", "email", "profile"]

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        """Return OpenID from user information provided by Google"""
        if response.get("email_verified"):
            return OpenID(
                email=response.get("email", ""),
                provider=cls.provider,
                id=response.get("sub"),
                first_name=response.get("given_name"),
                last_name=response.get("family_name"),
                display_name=response.get("name"),
                picture=response.get("picture"),
            )
        raise SSOLoginError(401, f"User {response.get('email')} is not verified with Google")

    @classmethod
    async def get_discovery_document(cls) -> Dict[str, str]:
        """Get document containing handy urls"""
        async with httpx.AsyncClient() as session:
            response = await session.get(cls.discovery_url)
            content = response.json()
            return content

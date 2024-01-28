"""Google SSO Login Helper."""


__all__ = ("GoogleSSO",)

from typing import Optional

import httpx

from fastapi_sso.infrastructure import DiscoveryDocument, OpenID, SSOBase, SSOLoginError


class GoogleSSO(SSOBase):
    """Class providing login via Google OAuth"""

    discovery_url = "https://accounts.google.com/.well-known/openid-configuration"
    provider = "google"
    scope = ["openid", "email", "profile"]

    async def openid_from_response(self, response: dict, session: Optional[httpx.AsyncClient] = None) -> OpenID:
        """Return OpenID from user information provided by Google"""

        if not response.get("email_verified"):
            raise SSOLoginError(401, f"User {response.get('email')} is not verified with Google")
        else:
            return OpenID(
                email=response.get("email", ""),
                provider=self.provider,
                id=response.get("sub"),
                first_name=response.get("given_name"),
                last_name=response.get("family_name"),
                display_name=response.get("name"),
                picture=response.get("picture"),
            )

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy urls"""

        async with httpx.AsyncClient() as session:
            response = await session.get(self.discovery_url)
            content = response.json()
            return content

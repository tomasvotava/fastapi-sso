"""Fitbit OAuth Login Helper."""


from typing import Optional

import httpx

from fastapi_sso.infrastructure import DiscoveryDocument, OpenID, SSOBase, SSOLoginError


class FitbitSSO(SSOBase):
    """Class providing login via Fitbit OAuth"""

    provider = "fitbit"
    scope = ["profile"]

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        """Return OpenID from user information provided by Google"""

        if not (info := response.get("user")):
            raise SSOLoginError(401, "Failed to process login via Fitbit")

        return OpenID(
            id=info["encodedId"],
            first_name=info["fullName"],
            display_name=info["displayName"],
            picture=info["avatar"],
            provider=self.provider,
        )

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy urls"""

        return {
            "authorization_endpoint": "https://www.fitbit.com/oauth2/authorize?response_type=code",
            "token_endpoint": "https://api.fitbit.com/oauth2/token",
            "userinfo_endpoint": "https://api.fitbit.com/1/user/-/profile.json",
        }

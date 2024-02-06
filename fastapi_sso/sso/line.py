import warnings
from typing import TYPE_CHECKING, Any, Dict, Optional

import httpx
from starlette.requests import Request

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, ReusedOauthClientWarning, SSOBase

if TYPE_CHECKING:
    import httpx


class LineSSO(SSOBase):
    """Class providing login via Line OAuth"""

    provider = "line"
    base_url = "https://api.line.me/oauth2/v2.1"
    scope = ["email", "profile", "openid"]

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy urls"""
        return {
            "authorization_endpoint": f"https://access.line.me/oauth2/v2.1/authorize",
            "token_endpoint": f"{self.base_url}/token",
            "userinfo_endpoint": f"{self.base_url}/userinfo",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        """Return OpenID from user information provided by Line"""
        return OpenID(
            email=response.get("email"),
            first_name="",
            last_name="",
            display_name=response.get("name"),
            provider=self.provider,
            id=response.get("sub"),
            picture=response.get("picture"),
        )

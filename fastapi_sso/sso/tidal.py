"""Tidal SSO Login Helper."""

from typing import TYPE_CHECKING, ClassVar, Optional

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class TidalSSO(SSOBase):
    """Class providing login via Tidal OAuth."""

    provider = "tidal"
    scope: ClassVar = ["user.read"]
    uses_pkce = True

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy urls."""
        return {
            "authorization_endpoint": "https://login.tidal.com/authorize",
            "token_endpoint": "https://auth.tidal.com/v1/oauth2/token",
            "userinfo_endpoint": "https://openapi.tidal.com/v2/users/me",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        """Return OpenID from user information provided by Tidal."""
        response = response["data"]
        return OpenID(
            id=response.get("id"),
            display_name=response["attributes"].get("username"),
            email=response["attributes"].get("email"),
            provider=self.provider,
        )

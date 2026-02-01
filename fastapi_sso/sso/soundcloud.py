"""Soundcloud SSO Login Helper."""

from typing import TYPE_CHECKING, ClassVar, Optional

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class SoundcloudSSO(SSOBase):
    """Class providing login via Soundcloud OAuth."""

    provider = "soundcloud"
    scope: ClassVar = ["openid"]

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy urls."""
        return {
            "authorization_endpoint": "https://secure.soundcloud.com/authorize",
            "token_endpoint": "https://secure.soundcloud.com/oauth/token",
            "userinfo_endpoint": "https://api.soundcloud.com/me",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        """Return OpenID from user information provided by Soundcloud."""
        return OpenID(
            id=str(response.get("id")),
            first_name=response.get("first_name"),
            last_name=response.get("last_name"),
            display_name=response.get("username"),
            picture=response.get("avatar_url"),
            provider=self.provider,
        )

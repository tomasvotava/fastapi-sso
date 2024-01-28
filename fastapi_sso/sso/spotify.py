"""Spotify SSO Login Helper."""


__all__ = ("SpotifySSO",)

from typing import Optional

import httpx

from fastapi_sso.infrastructure import DiscoveryDocument, OpenID, SSOBase


class SpotifySSO(SSOBase):
    """Class providing login via Spotify OAuth."""

    provider = "spotify"
    scope = ["user-read-private", "user-read-email"]

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy urls"""
        return {
            "authorization_endpoint": "https://accounts.spotify.com/authorize",
            "token_endpoint": "https://accounts.spotify.com/api/token",
            "userinfo_endpoint": "https://api.spotify.com/v1/me",
        }

    async def openid_from_response(self, response: dict, session: Optional[httpx.AsyncClient] = None) -> OpenID:
        """Return OpenID from user information provided by Spotify."""

        if response.get("images") and len(response["images"]) > 0:
            picture: Optional[str] = response["images"][0]["url"]
        else:
            picture = None

        return OpenID(
            email=response.get("email", ""),
            display_name=response.get("display_name"),
            provider=self.provider,
            id=response.get("id"),
            picture=picture,
        )

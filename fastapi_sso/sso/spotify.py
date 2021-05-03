"""Spotify SSO Login Helper
"""

from typing import Dict

from fastapi_sso.sso.base import OpenID, SSOBase


class SpotifySSO(SSOBase):
    """Class providing login via Spotify OAuth"""

    provider = "spotify"
    scope = ["user-read-private", "user-read-email"]

    @classmethod
    async def get_discovery_document(cls) -> Dict[str, str]:
        """Get document containing handy urls"""
        return {
            "authorization_endpoint": "https://accounts.spotify.com/authorize",
            "token_endpoint": "https://accounts.spotify.com/api/token",
            "userinfo_endpoint": "https://api.spotify.com/v1/me",
        }

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        """Return OpenID from user information provided by Spotify"""
        if response.get("images", []):
            picture = response["images"][0]["url"]
        else:
            picture = None
        return OpenID(
            email=response.get("email", ""),
            display_name=response.get("display_name"),
            provider=cls.provider,
            id=response.get("id"),
            picture=picture,
        )

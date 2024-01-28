"""Kakao SSO Oauth Helper class"""


__all__ = ("KakaoSSO",)


from typing import Optional

import httpx

from fastapi_sso.infrastructure import DiscoveryDocument, OpenID, SSOBase


class KakaoSSO(SSOBase):
    """Class providing login using Kakao OAuth"""

    provider = "kakao"
    scope = ["openid"]
    version = "v2"

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://kauth.kakao.com/oauth/authorize",
            "token_endpoint": "https://kauth.kakao.com/oauth/token",
            "userinfo_endpoint": f"https://kapi.kakao.com/{self.version}/user/me",
        }

    async def openid_from_response(self, response: dict, session: Optional[httpx.AsyncClient] = None) -> OpenID:
        return OpenID(display_name=response["properties"]["nickname"], provider=self.provider)

"""Kakao SSO Oauth Helper class"""

from typing import Dict

from fastapi_sso.sso.base import OpenID, SSOBase


class KakaoSSO(SSOBase):
    """Class providing login using Kakao OAuth"""

    provider = "kakao"
    scope = ["openid"]
    version = "v2"

    async def get_discovery_document(self) -> Dict[str, str]:
        return {
            "authorization_endpoint": "https://kauth.kakao.com/oauth/authorize",
            "token_endpoint": "https://kauth.kakao.com/oauth/token",
            "userinfo_endpoint": f"https://kapi.kakao.com/{self.version}/user/me",
        }

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        return OpenID(display_name=response["properties"]["nickname"], provider=cls.provider)

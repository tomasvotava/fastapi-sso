import os
from typing import Dict

from fastapi_sso.sso.base import OpenID, SSOBase


class KakaoSSO(SSOBase):
    provider = "kakao"
    scope = ["openid"]
    version = "v2"

    async def get_discovery_document(self) -> Dict[str, str]:
        return {
            "authorization_endpoint": f"https://kauth.kakao.com/oauth/authorize?client_id={self.client_secret}&response_type=code&redirect_uri={self.redirect_uri}",
            "token_endpoint": f"https://kauth.kakao.com/oauth/token",
            "userinfo_endpoint": f"https://kapi.kakao.com/{self.version}/user/me",
        }

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        return OpenID(display_name=response["properties"]["nickname"], provider=cls.provider)

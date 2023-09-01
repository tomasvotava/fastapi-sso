"""Naver SSO Oauth Helper class"""

from typing import List

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase


class NaverSSO(SSOBase):
    """Class providing login using Naver OAuth"""

    provider = "naver"
    scope: List[str] = []
    additional_headers = {"accept": "application/json"}

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://nid.naver.com/oauth2.0/authorize",
            "token_endpoint": "https://nid.naver.com/oauth2.0/token",
            "userinfo_endpoint": "https://openapi.naver.com/v1/nid/me",
        }

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        return OpenID(
            display_name=response["properties"]["nickname"],
            provider=cls.provider,
            data=response,
        )

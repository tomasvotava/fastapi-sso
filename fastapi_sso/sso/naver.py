"""Naver SSO Oauth Helper class."""


__all__ = ("NaverSSO",)


from typing import List, Optional

import httpx

from fastapi_sso.infrastructure import DiscoveryDocument, OpenID, SSOBase


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

    async def openid_from_response(self, response: dict, session: Optional[httpx.AsyncClient] = None) -> OpenID:
        return OpenID(display_name=response["properties"]["nickname"], provider=self.provider)

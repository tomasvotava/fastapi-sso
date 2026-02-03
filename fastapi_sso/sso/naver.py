"""Naver SSO Oauth Helper class."""

from typing import TYPE_CHECKING, ClassVar, Optional

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class NaverSSO(SSOBase):
    """Class providing login using Naver OAuth."""

    provider = "naver"
    scope: ClassVar[list[str]] = []
    additional_headers: ClassVar = {"accept": "application/json"}

    @property
    def _extra_query_params(self) -> dict:
        return {"client_secret": self.client_secret}

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://nid.naver.com/oauth2.0/authorize",
            "token_endpoint": "https://nid.naver.com/oauth2.0/token",
            "userinfo_endpoint": "https://openapi.naver.com/v1/nid/me",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        return OpenID(
            id=response["response"]["id"],
            email=response["response"].get("email"),
            display_name=response["response"].get("nickname"),
            picture=response["response"].get("profile_image"),
            provider=self.provider,
        )

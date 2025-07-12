"""LinkedIn SSO Oauth Helper class."""

from typing import TYPE_CHECKING, ClassVar, Any

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class LinkedInSSO(SSOBase):
    """Class providing login via LinkedIn SSO."""

    provider = "linkedin"
    scope: ClassVar = ["openid", "profile", "email"]
    additional_headers: ClassVar = {"accept": "application/json"}
    use_id_token_for_user_info: ClassVar = True

    @property
    def _extra_query_params(self) -> dict[str, Any]:
        return {"client_secret": self.client_secret}

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://www.linkedin.com/oauth/v2/authorization",
            "token_endpoint": "https://www.linkedin.com/oauth/v2/accessToken",
            "userinfo_endpoint": "https://api.linkedin.com/v2/userinfo",
        }

    async def openid_from_token(self, id_token: dict[str, Any], session: "httpx.AsyncClient" | None = None) -> OpenID:
        return await self.openid_from_response(id_token, session)

    async def openid_from_response(self, response: dict[str, Any], session: "httpx.AsyncClient" | None = None) -> OpenID:
        return OpenID(
            email=response.get("email"),
            provider=self.provider,
            id=response.get("sub"),
            first_name=response.get("given_name"),
            last_name=response.get("family_name"),
            picture=response.get("picture"),
        )

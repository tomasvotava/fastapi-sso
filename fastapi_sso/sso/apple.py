"""Apple SSO Login helper."""

from typing import TYPE_CHECKING, ClassVar, Optional

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class AppleSSO(SSOBase):
    """Class providing login via Apple ID OAuth."""

    provider = "apple"
    scope: ClassVar = ["openid", "email"]
    use_id_token_for_user_info: ClassVar = True
    use_basic_auth: ClassVar = False

    @property
    def _extra_query_params(self) -> dict:
        return {"client_secret": self.client_secret}

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy URLs."""
        return {
            "authorization_endpoint": "https://appleid.apple.com/auth/authorize",
            "token_endpoint": "https://appleid.apple.com/auth/token",
            "userinfo_endpoint": "https://appleid.apple.com/auth/keys",
        }

    async def openid_from_token(self, id_token: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        return await self.openid_from_response(id_token, session)

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        """Return OpenID from user information provided by Apple."""
        return OpenID(
            id=response.get("sub"),
            email=response.get("email"),
            provider=self.provider,
        )

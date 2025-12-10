"""Microsoft SSO Oauth Helper class."""

from typing import TYPE_CHECKING, ClassVar, Optional, Union

import pydantic

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase, _decode_id_token

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class MicrosoftSSO(SSOBase):
    """Class providing login using Microsoft OAuth."""

    provider = "microsoft"
    scope: ClassVar = ["openid", "User.Read", "email"]
    version = "v1.0"
    tenant: str = "common"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = None,
        allow_insecure_http: bool = False,
        use_state: bool = False,  # TODO: Remove use_state argument
        scope: Optional[list[str]] = None,
        tenant: Optional[str] = None,
    ):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            allow_insecure_http=allow_insecure_http,
            use_state=use_state,  # TODO: Remove use_state argument
            scope=scope,
        )
        self.tenant = tenant or self.tenant

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/authorize",
            "token_endpoint": f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/token",
            "userinfo_endpoint": f"https://graph.microsoft.com/{self.version}/me",
        }

    async def get_user_roles(self) -> list[str]:
        """Get user roles from Microsoft ID token."""
        token_info = _decode_id_token(self._id_token)
        return token_info.get("roles")

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        token_info = _decode_id_token(self._id_token)
        return OpenID(
            email=response.get("mail"),
            display_name=response.get("displayName"),
            provider=self.provider,
            id=response.get("id"),
            first_name=response.get("givenName"),
            last_name=response.get("surname"),
            roles=token_info.get("roles"),
        )

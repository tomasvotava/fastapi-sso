"""Microsoft SSO Oauth Helper class"""

from typing import List, Optional

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase


class MicrosoftSSO(SSOBase):
    """Class providing login using Microsoft OAuth"""

    provider = "microsoft"
    scope = ["openid"]
    version = "v1.0"
    tenant: str = "common"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: Optional[str] = None,
        allow_insecure_http: bool = False,
        use_state: bool = False,  # TODO: Remove use_state argument
        scope: Optional[List[str]] = None,
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

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        return OpenID(email=response["mail"], display_name=response["displayName"], provider=cls.provider)

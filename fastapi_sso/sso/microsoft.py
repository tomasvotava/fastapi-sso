"""Microsoft SSO Oauth Helper class"""

from typing import Dict

from fastapi_sso.sso.base import OpenID, SSOBase


class MicrosoftSSOBase(SSOBase):
    client_tenant: str = NotImplemented  # Microsoft

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        client_tenant: str,
        redirect_uri: str,
        allow_insecure_http: bool = False,
        use_state: bool = True,
    ):
        super().__init__(client_id, client_secret, redirect_uri, allow_insecure_http, use_state)
        self.client_tenant = client_tenant


class MicrosoftSSO(MicrosoftSSOBase):
    provider = "microsoft"
    scope = ["openid"]
    version = "v1.0"

    async def get_discovery_document(self) -> Dict[str, str]:
        return {
            "authorization_endpoint": f"https://login.microsoftonline.com/{self.client_tenant}/oauth2/v2.0/authorize",
            "token_endpoint": f"https://login.microsoftonline.com/{self.client_tenant}/oauth2/v2.0/token",
            "userinfo_endpoint": f"https://graph.microsoft.com/{self.version}/me",
        }

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        return OpenID(email=response["mail"], display_name=response["displayName"], provider=cls.provider)

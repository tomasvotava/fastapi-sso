"""Discord SSO Oauth Helper class"""

from typing import TYPE_CHECKING, ClassVar, List, Optional, Union

import pydantic

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class DiscordSSO(SSOBase):
    """Class providing login using Discord OAuth"""

    provider = "discord"
    scope: ClassVar = ["identify", "email", "openid"]

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = None,
        allow_insecure_http: bool = False,
        scope: Optional[List[str]] = None,
    ):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            allow_insecure_http=allow_insecure_http,
            scope=scope,
        )

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://discord.com/oauth2/authorize",
            "token_endpoint": "https://discord.com/api/oauth2/token",
            "userinfo_endpoint": "https://discord.com/api/users/@me",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        user_id = response.get("id")
        avatar = response.get("avatar")
        picture = None
        if user_id and avatar:
            picture = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png"

        return OpenID(
            email=response.get("email"),
            display_name=response.get("global_name"),
            provider=self.provider,
            id=user_id,
            first_name=response.get("username"),
            picture=picture,
        )

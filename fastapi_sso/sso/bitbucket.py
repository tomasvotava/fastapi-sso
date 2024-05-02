"""BitBucket SSO Oauth Helper class"""

from typing import TYPE_CHECKING, ClassVar, List, Optional, Union

import pydantic

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

if TYPE_CHECKING:
    import httpx  # pragma: no cover


class BitbucketSSO(SSOBase):
    """Class providing login using BitBucket OAuth"""

    provider = "bitbucket"
    scope: ClassVar = ["account", "email"]
    version = "2.0"

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

    async def get_useremail(self, session: Optional["httpx.AsyncClient"] = None) -> dict:
        """Get user email"""
        if session is None:
            raise ValueError("Session is required to make HTTP requests")

        response = await session.get(f"https://api.bitbucket.org/{self.version}/user/emails")
        return response.json()

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://bitbucket.org/site/oauth2/authorize",
            "token_endpoint": "https://bitbucket.org/site/oauth2/access_token",
            "userinfo_endpoint": f"https://api.bitbucket.org/{self.version}/user",
        }

    async def openid_from_response(self, response: dict, session: Optional["httpx.AsyncClient"] = None) -> OpenID:
        email = await self.get_useremail(session=session)
        return OpenID(
            email=email["values"][0]["email"],
            display_name=response.get("display_name"),
            provider=self.provider,
            id=str(response.get("uuid")).strip("{}"),
            first_name=response.get("nickname"),
            picture=response.get("links", {}).get("avatar", {}).get("href"),
        )

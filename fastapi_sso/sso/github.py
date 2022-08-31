"""Github SSO Oauth Helper class"""
from typing import Any, Dict, Optional
from fastapi_sso.sso.base import SSOBase, DiscoveryDocument, OpenID
from starlette.requests import Request

import httpx
import json

class PatchedSSOBase(SSOBase):

    @property
    async def email_endpoint(self) -> Optional[str]:
        """Return `userinfo_endpoint` from discovery document"""
        discovery = await self.get_discovery_document()
        return discovery.get("email_endpoint")

    # Ideally this should be fixed upstream
    async def process_login(
        self, code: str, request: Request, *, params: Optional[Dict[str, Any]] = None
    ) -> Optional[OpenID]:
        """This method should be called from callback endpoint to verify the user and request user info endpoint.
        This is low level, you should use {verify_and_process} instead.

        Arguments:
            params {Optional[Dict[str, Any]]} -- Optional additional query parameters to pass to the provider
        """
        # pylint: disable=too-many-locals
        params = params or {}
        url = request.url
        scheme = url.scheme
        if not self.allow_insecure_http and scheme != "https":
            current_url = str(url).replace("http://", "https://")
            scheme = "https"
        else:
            current_url = str(url)
        current_path = f"{scheme}://{url.netloc}{url.path}"

        token_url, headers, body = self.oauth_client.prepare_token_request(
            await self.token_endpoint,
            authorization_response=current_url,
            redirect_url=current_path,
            code=code,
            **params,
        )  # type: ignore

        if token_url is None:
            return None

        auth = httpx.BasicAuth(self.client_id, self.client_secret)

        # https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps
        # Required, otherwise github will not return JSON and break parsing
        headers["Accept"] = "application/json"

        async with httpx.AsyncClient() as session:
            response = await session.post(token_url, headers=headers, content=body, auth=auth)
            content = response.json()
            self._refresh_token = content.get("refresh_token")
            self.oauth_client.parse_request_body_response(json.dumps(content))

            uri, headers, _ = self.oauth_client.add_token(await self.userinfo_endpoint)
            response = await session.get(uri, headers=headers)
            content = response.json()

            # Fetch EMail Endpoint
            uri, headers, _ = self.oauth_client.add_token(await self.email_endpoint)
            response = await session.get(uri, headers=headers)
            content["email"] = response.json()

        return await self.openid_from_response(content)




class GithubSSO(PatchedSSOBase):
    """Github SSO Provider"""

    provider = "github"
    # https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps
    scope = ["user:email"]

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy urls"""
        return {
            "authorization_endpoint": "https://github.com/login/oauth/authorize",
            "token_endpoint": "https://github.com/login/oauth/access_token",
            "userinfo_endpoint": "https://api.github.com/user",
            "email_endpoint": "https://api.github.com/user/emails",
        }

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        primary_email = ""
        # Since there are multiple EMail Adresses, pick the primary
        for email in response.get("email"):
            if email["verified"] is True and email["primary"] is True:
                primary_email = str(email["email"])

        return OpenID(
                provider=cls.provider,
                id=response.get("id"),
                email=primary_email,
                display_name=response.get("login"),
                picture=response.get("avatar_url"),
            )


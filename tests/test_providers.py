# type: ignore


from typing import Type
from urllib.parse import quote_plus

import pytest
from fastapi.responses import RedirectResponse
from utils import AnythingDict, Request, Response, make_fake_async_client

from fastapi_sso.sso.base import OpenID, SSOBase
from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.fitbit import FitbitSSO
from fastapi_sso.sso.generic import create_provider
from fastapi_sso.sso.github import GithubSSO
from fastapi_sso.sso.gitlab import GitlabSSO
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.kakao import KakaoSSO
from fastapi_sso.sso.line import LineSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from fastapi_sso.sso.naver import NaverSSO
from fastapi_sso.sso.spotify import SpotifySSO
from fastapi_sso.sso.notion import NotionSSO

GenericProvider = create_provider(
    name="generic",
    discovery_document={
        "authorization_endpoint": "https://example.com/auth",
        "token_endpoint": "https://example.com/token",
        "userinfo_endpoint": "https://example.com/userinfo",
    },
    response_convertor=lambda _, __: OpenID(id="test", email="test@example.com", display_name="Test"),
)

tested_providers = (
    FacebookSSO,
    FitbitSSO,
    GithubSSO,
    GitlabSSO,
    GoogleSSO,
    KakaoSSO,
    LineSSO,
    MicrosoftSSO,
    NaverSSO,
    SpotifySSO,
    GenericProvider,
    NotionSSO,
)

# Run all tests for each of the listed providers
pytestmark = pytest.mark.parametrize("Provider", tested_providers)


@pytest.fixture(autouse=True)
def mock_google_dicscovery_document(monkeypatch: pytest.MonkeyPatch):
    """GoogleSSO has a discovery document dependent on Google API"""

    async def _fake_get_discovery_document(_):
        return await GenericProvider("test", "test").get_discovery_document()

    monkeypatch.setattr(GoogleSSO, "get_discovery_document", _fake_get_discovery_document)


class TestProviders:
    @pytest.mark.parametrize("item", ("authorization_endpoint", "token_endpoint", "userinfo_endpoint"))
    async def test_discovery_document(self, Provider: Type[SSOBase], item: str):
        sso = Provider("client_id", "client_secret")
        document = await sso.get_discovery_document()
        assert item in document, f"Discovery document for provider {sso.provider} must have {item}"
        assert (
            await getattr(sso, item) == document[item]
        ), f"Discovery document for provider {sso.provider} must have {item}"

    async def test_login_url_request_time(self, Provider: Type[SSOBase]):
        sso = Provider("client_id", "client_secret")
        url = await sso.get_login_url(redirect_uri="http://localhost")
        assert url.startswith(
            await sso.authorization_endpoint
        ), f"Login URL must start with {await sso.authorization_endpoint}"
        assert "redirect_uri=http%3A%2F%2Flocalhost" in url, "Login URL must have redirect_uri query parameter"

        with pytest.raises(ValueError):
            await sso.get_login_url()

    async def test_login_url_construction_time(self, Provider: Type[SSOBase]):
        sso = Provider("client_id", "client_secret", redirect_uri="http://localhost")
        url = await sso.get_login_url()
        assert url.startswith(
            await sso.authorization_endpoint
        ), f"Login URL must start with {await sso.authorization_endpoint}"
        assert "redirect_uri=http%3A%2F%2Flocalhost" in url, "Login URL must have redirect_uri query parameter"

    async def assert_get_login_url_and_redirect(self, sso: SSOBase, **kwargs):
        url = await sso.get_login_url(**kwargs)
        redirect = await sso.get_login_redirect(**kwargs)
        assert isinstance(url, str), "Login URL must be a string"
        assert isinstance(redirect, RedirectResponse), "Login redirect must be a RedirectResponse"
        assert redirect.headers["location"] == url, "Login redirect must have the same URL as login URL"
        return url, redirect

    async def test_login_url_additional_params(self, Provider: Type[SSOBase]):
        sso = Provider("client_id", "client_secret", redirect_uri="http://localhost")
        url, _ = await self.assert_get_login_url_and_redirect(sso, params={"access_type": "offline", "param": "value"})
        assert "access_type=offline" in url, "Login URL must have additional query parameters"
        assert "param=value" in url, "Login URL must have additional query parameters"

    async def test_login_url_state_at_request_time(self, Provider: Type[SSOBase]):
        sso = Provider("client_id", "client_secret")
        url, _ = await self.assert_get_login_url_and_redirect(sso, redirect_uri="http://localhost", state="unique")
        assert "state=unique" in url, "Login URL must have state query parameter"

    async def test_login_url_scope_default(self, Provider: Type[SSOBase]):
        sso = Provider("client_id", "client_secret")
        url, _ = await self.assert_get_login_url_and_redirect(sso, redirect_uri="http://localhost")
        assert quote_plus(" ".join(sso.scope)) in url, "Login URL must have all scopes"

    async def test_login_url_scope_additional(self, Provider: Type[SSOBase]):
        sso = Provider("client_id", "client_secret", scope=["openid", "additional"])
        url, _ = await self.assert_get_login_url_and_redirect(sso, redirect_uri="http://localhost")
        assert quote_plus(" ".join(sso.scope)) in url, "Login URL must have all scopes"

    async def test_process_login(self, Provider: Type[SSOBase], monkeypatch: pytest.MonkeyPatch):
        sso = Provider("client_id", "client_secret")
        FakeAsyncClient = make_fake_async_client(
            returns_post=Response(url="https://localhost", json_content={"access_token": "token"}),
            returns_get=Response(
                url="https://localhost",
                json_content=AnythingDict(
                    {"token_endpoint": "https://localhost", "userinfo_endpoint": "https://localhost"}
                ),
            ),
        )

        async def fake_openid_from_response(_, __):
            return OpenID(id="test", email="email@example.com", display_name="Test")

        monkeypatch.setattr("httpx.AsyncClient", FakeAsyncClient)
        monkeypatch.setattr(sso, "openid_from_response", fake_openid_from_response)
        request = Request(url="https://localhost?code=code&state=unique")
        await sso.process_login("code", request)

    def test_context_manager_behavior(self, Provider: Type[SSOBase]):
        sso = Provider("client_id", "client_secret")
        assert sso._oauth_client is None, "OAuth client must be after initialization"
        assert sso._refresh_token is None, "Refresh token must be None after initialization"
        sso.oauth_client
        sso._refresh_token = "test"
        assert sso._oauth_client is not None, "OAuth client must be initialized after first access"
        with sso:
            assert sso._oauth_client is None, "OAuth client must be None within the context manager"
            assert sso._refresh_token is None, "Refresh token must be None within the context manager"

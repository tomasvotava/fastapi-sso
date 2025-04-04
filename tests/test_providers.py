# type: ignore

from urllib.parse import quote_plus

import jwt
import pytest
from fastapi.responses import RedirectResponse
from utils import AnythingDict, Request, Response, make_fake_async_client

from fastapi_sso.sso.base import OpenID, SecurityWarning, SSOBase, SSOLoginError
from fastapi_sso.sso.bitbucket import BitbucketSSO
from fastapi_sso.sso.discord import DiscordSSO
from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.fitbit import FitbitSSO
from fastapi_sso.sso.generic import create_provider
from fastapi_sso.sso.github import GithubSSO
from fastapi_sso.sso.gitlab import GitlabSSO
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.kakao import KakaoSSO
from fastapi_sso.sso.line import LineSSO
from fastapi_sso.sso.linkedin import LinkedInSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from fastapi_sso.sso.naver import NaverSSO
from fastapi_sso.sso.notion import NotionSSO
from fastapi_sso.sso.seznam import SeznamSSO
from fastapi_sso.sso.spotify import SpotifySSO
from fastapi_sso.sso.twitter import TwitterSSO
from fastapi_sso.sso.yandex import YandexSSO

fake_id_token = jwt.encode({"email": "user@idtoken.com"}, key="test", algorithm="HS256")

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
    LinkedInSSO,
    TwitterSSO,
    YandexSSO,
    SeznamSSO,
    BitbucketSSO,
    DiscordSSO,
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
    async def test_discovery_document(self, Provider: type[SSOBase], item: str):
        sso = Provider("client_id", "client_secret")
        async with sso:
            document = await sso.get_discovery_document()
            assert item in document, f"Discovery document for provider {sso.provider} must have {item}"
            assert (
                await getattr(sso, item) == document[item]
            ), f"Discovery document for provider {sso.provider} must have {item}"

    async def test_login_url_request_time(self, Provider: type[SSOBase]):
        sso = Provider("client_id", "client_secret")
        async with sso:
            url = await sso.get_login_url(redirect_uri="http://localhost")
            assert url.startswith(
                await sso.authorization_endpoint
            ), f"Login URL must start with {await sso.authorization_endpoint}"
            assert "redirect_uri=http%3A%2F%2Flocalhost" in url, "Login URL must have redirect_uri query parameter"

            with pytest.raises(ValueError):
                await sso.get_login_url()

    async def test_login_url_construction_time(self, Provider: type[SSOBase]):
        sso = Provider("client_id", "client_secret", redirect_uri="http://localhost")

        async with sso:
            url = await sso.get_login_url()
            assert url.startswith(
                await sso.authorization_endpoint
            ), f"Login URL must start with {await sso.authorization_endpoint}"
            assert "redirect_uri=http%3A%2F%2Flocalhost" in url, "Login URL must have redirect_uri query parameter"

    async def assert_get_login_url_and_redirect(self, sso: SSOBase, **kwargs):
        async with sso:
            url = await sso.get_login_url(**kwargs)
            redirect = await sso.get_login_redirect(**kwargs)
            assert isinstance(url, str), "Login URL must be a string"
            assert isinstance(redirect, RedirectResponse), "Login redirect must be a RedirectResponse"
            assert redirect.headers["location"] == url, "Login redirect must have the same URL as login URL"
            return url, redirect

    async def test_login_url_additional_params(self, Provider: type[SSOBase]):
        sso = Provider("client_id", "client_secret", redirect_uri="http://localhost")

        url, _ = await self.assert_get_login_url_and_redirect(sso, params={"access_type": "offline", "param": "value"})
        assert "access_type=offline" in url, "Login URL must have additional query parameters"
        assert "param=value" in url, "Login URL must have additional query parameters"

    async def test_login_url_state_at_request_time(self, Provider: type[SSOBase]):
        sso = Provider("client_id", "client_secret")
        url, _ = await self.assert_get_login_url_and_redirect(sso, redirect_uri="http://localhost", state="unique")
        assert "state=unique" in url, "Login URL must have state query parameter"

    async def test_login_url_scope_default(self, Provider: type[SSOBase]):
        sso = Provider("client_id", "client_secret")
        url, _ = await self.assert_get_login_url_and_redirect(sso, redirect_uri="http://localhost")
        assert quote_plus(" ".join(sso._scope)) in url, "Login URL must have all scopes"

    async def test_login_url_scope_additional(self, Provider: type[SSOBase]):
        sso = Provider("client_id", "client_secret", scope=["openid", "additional"])
        url, _ = await self.assert_get_login_url_and_redirect(sso, redirect_uri="http://localhost")
        assert quote_plus(" ".join(sso._scope)) in url, "Login URL must have all scopes"

    async def test_process_login(self, Provider: type[SSOBase], monkeypatch: pytest.MonkeyPatch):
        sso = Provider("client_id", "client_secret")
        get_response = Response(
            url="https://localhost",
            json_content=AnythingDict(
                {"token_endpoint": "https://localhost", "userinfo_endpoint": "https://localhost"}
            ),
        )

        FakeAsyncClient = make_fake_async_client(
            returns_post=Response(url="https://localhost", json_content={"access_token": "token"}),
            returns_get=get_response,
        )

        async def fake_openid_from_response(_, __):
            return OpenID(id="test", email="email@example.com", display_name="Test")

        async def fake_openid_from_id_token(_, __):
            return OpenID(id="idtoken", email="user@idtoken.com", display_name="ID Token")

        async with sso:
            monkeypatch.setattr("httpx.AsyncClient", FakeAsyncClient)
            monkeypatch.setattr(sso, "openid_from_response", fake_openid_from_response)
            monkeypatch.setattr(sso, "openid_from_token", fake_openid_from_id_token)
            request = Request(url="https://localhost?code=code&state=unique")
            if sso.use_id_token_for_user_info:
                with pytest.raises(SSOLoginError, match="Provider .* did not return id token"):
                    await sso.process_login("code", request)
            else:
                await sso.process_login("code", request)

        if sso.use_id_token_for_user_info:
            monkeypatch.setattr("jwt.decode", lambda _, options: {})
            FakeAsyncClient = make_fake_async_client(
                returns_post=Response(
                    url="https://localhost", json_content={"access_token": "token", "id_token": "fake id token"}
                ),
                returns_get=get_response,
            )
            monkeypatch.setattr("httpx.AsyncClient", FakeAsyncClient)
            await sso.process_login("code", request)

    async def test_context_manager_behavior(self, Provider: type[SSOBase]):
        sso = Provider("client_id", "client_secret")
        assert sso._oauth_client is None, "OAuth client must be after initialization"
        assert sso._refresh_token is None, "Refresh token must be None after initialization"
        with pytest.warns(SecurityWarning, match="Please make sure you are using SSO provider in an async context"):
            sso.oauth_client
        sso._refresh_token = "test"
        assert sso._oauth_client is not None, "OAuth client must be initialized after first access"
        async with sso:
            assert sso._oauth_client is None, "OAuth client must be None within the context manager"
            assert sso._refresh_token is None, "Refresh token must be None within the context manager"

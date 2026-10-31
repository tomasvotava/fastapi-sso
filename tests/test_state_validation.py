# type: ignore

import warnings

import pytest
from utils import Request

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SecurityWarning, SSOBase, SSOLoginError
from fastapi_sso.sso.google import GoogleSSO


class FakeSSO(SSOBase):
    provider = "fake"

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://fake.com/authorize",
            "token_endpoint": "https://fake.com/token",
            "userinfo_endpoint": "https://fake.com/userinfo",
        }

    async def openid_from_response(self, response: dict, session=None) -> OpenID:
        return OpenID(id="fake-id", provider=self.provider)


@pytest.fixture()
def sso(monkeypatch: pytest.MonkeyPatch) -> FakeSSO:
    async def fake_process_login(self, code, request, **kwargs):
        return "logged-in"

    monkeypatch.setattr(SSOBase, "process_login", fake_process_login)
    return FakeSSO("client_id", "client_secret", redirect_uri="https://localhost/callback")


def callback(state: str | None = None, cookie: str | None = None) -> Request:
    request = Request(cookies={"sso_state": cookie} if cookie is not None else None)
    request.query_params["code"] = "code"
    if state is not None:
        request.query_params["state"] = state
    return request


@pytest.mark.parametrize("provider", [SSOBase, GoogleSSO])
def test_state_is_required_by_default(provider: type[SSOBase]):
    assert provider("client_id", "client_secret").requires_state is True


async def test_callback_without_state_is_rejected(sso: FakeSSO):
    async with sso:
        with pytest.raises(SSOLoginError, match="'state' parameter was not found"):
            await sso.verify_and_process(callback())


async def test_callback_with_state_but_no_cookie_is_rejected(sso: FakeSSO):
    async with sso:
        with pytest.raises(SSOLoginError, match="State cookie not found"):
            await sso.verify_and_process(callback(state="attacker-state"))


async def test_callback_with_mismatched_cookie_is_rejected(sso: FakeSSO):
    async with sso:
        with pytest.raises(SSOLoginError, match="Invalid state"):
            await sso.verify_and_process(callback(state="attacker-state", cookie="victim-state"))


async def test_callback_with_non_ascii_state_is_rejected(sso: FakeSSO):
    async with sso:
        with pytest.raises(SSOLoginError, match="Invalid state"):
            await sso.verify_and_process(callback(state="státe", cookie="state"))


async def test_callback_with_matching_cookie_is_accepted(sso: FakeSSO):
    async with sso:
        assert await sso.verify_and_process(callback(state="state", cookie="state")) == "logged-in"


async def test_state_validation_can_be_opted_out_of(sso: FakeSSO):
    sso.requires_state = False
    async with sso:
        assert await sso.verify_and_process(callback()) == "logged-in"


async def test_login_redirect_sets_hardened_state_cookie(sso: FakeSSO):
    async with sso:
        response = await sso.get_login_redirect()
    cookie = response.headers["set-cookie"]
    assert f"sso_state={sso._generated_state}" in cookie
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=lax" in cookie


async def test_state_cookie_is_not_secure_over_insecure_http(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OAUTHLIB_INSECURE_TRANSPORT", raising=False)
    sso = FakeSSO("client_id", "client_secret", redirect_uri="http://localhost/callback", allow_insecure_http=True)
    async with sso:
        response = await sso.get_login_redirect()
    assert "Secure" not in response.headers["set-cookie"]


async def test_login_url_warns_that_state_is_not_bound(sso: FakeSSO):
    async with sso:
        with pytest.warns(SecurityWarning, match="not bound to the 'sso_state' cookie"):
            await sso.get_login_url()


async def test_login_redirect_does_not_warn_about_binding(sso: FakeSSO):
    async with sso:
        with warnings.catch_warnings():
            warnings.simplefilter("error", SecurityWarning)
            await sso.get_login_redirect()


async def test_login_redirect_sets_redirect_uri_cookie(sso: FakeSSO):
    async with sso:
        response = await sso.get_login_redirect(redirect_uri="https://example.com/custom/callback")
    cookies = [v.decode("latin1") for k, v in response.raw_headers if k.lower() == b"set-cookie"]
    redirect_cookie = next((c for c in cookies if "sso_redirect_uri=" in c), None)
    assert redirect_cookie is not None
    assert "sso_redirect_uri=" in redirect_cookie
    expected_encoded = "https%3A%2F%2Fexample.com%2Fcustom%2Fcallback"
    assert expected_encoded in redirect_cookie or "https://example.com/custom/callback" in redirect_cookie
    assert "HttpOnly" in redirect_cookie
    assert "Secure" in redirect_cookie
    assert "SameSite=lax" in redirect_cookie


async def test_verify_and_process_uses_cookie_redirect_uri(monkeypatch: pytest.MonkeyPatch):
    captured = {}

    async def fake_process_login(self, code, request, **kwargs):
        captured.update(kwargs)
        return "logged-in"

    monkeypatch.setattr(SSOBase, "process_login", fake_process_login)
    sso = FakeSSO("client_id", "client_secret")
    request = Request(cookies={"sso_state": "state", "sso_redirect_uri": "https://example.com/from-cookie"})
    request.query_params["code"] = "code"
    request.query_params["state"] = "state"

    async with sso:
        result = await sso.verify_and_process(request)

    assert result == "logged-in"
    assert captured.get("redirect_uri") == "https://example.com/from-cookie"


async def test_process_login_uses_https_current_path_behind_reverse_proxy(monkeypatch: pytest.MonkeyPatch):
    captured_redirect_url = {}

    sso = FakeSSO("client_id", "client_secret", allow_insecure_http=False)

    def fake_prepare_token_request(*args, **kwargs):
        captured_redirect_url["url"] = kwargs.get("redirect_url")
        return "https://fake.com/token", {}, "{}"

    class DummyURL:
        scheme = "http"
        netloc = "my-service.com"
        path = "/auth/callback"
        def __str__(self):
            return "http://my-service.com/auth/callback"

    class DummyRequest:
        def __init__(self):
            self.url = DummyURL()
            self.cookies = {}

    async with sso:
        from oauthlib.oauth2 import WebApplicationClient

        monkeypatch.setattr(WebApplicationClient, "prepare_token_request", fake_prepare_token_request)
        import httpx

        async def fake_post(*args, **kwargs):
            class FakeResponse:
                def json(self):
                    return {
                        "access_token": "fake-access-token",
                        "token_type": "bearer",
                        "refresh_token": None,
                        "id_token": None,
                    }

            return FakeResponse()

        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
        monkeypatch.setattr(sso.oauth_client, "parse_request_body_response", lambda *a: None)
        monkeypatch.setattr(sso.oauth_client, "add_token", lambda *a: ("https://fake.com/userinfo", {}, None))
        async def fake_parse(*args):
            return {}
        monkeypatch.setattr(sso, "parse_userinfo_response", fake_parse)
        async def fake_openid(*args):
            return "done"
        monkeypatch.setattr(sso, "openid_from_response", fake_openid)

        await sso.process_login("code", DummyRequest())

    assert captured_redirect_url.get("url") == "https://my-service.com/auth/callback"

# type: ignore

import pytest
from utils import Request

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase, SSOLoginError
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

# type: ignore

import json

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm
from utils import Request, Response

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase, SSOLoginError

JWKS_URI = "https://fake.com/jwks"
USERINFO_URI = "https://fake.com/userinfo"
CLIENT_ID = "client_id"

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
other_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
third_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)


class FakeSSO(SSOBase):
    provider = "fake"

    async def get_discovery_document(self) -> DiscoveryDocument:
        return {
            "authorization_endpoint": "https://fake.com/authorize",
            "token_endpoint": "https://fake.com/token",
            "userinfo_endpoint": USERINFO_URI,
            "jwks_uri": JWKS_URI,
        }

    async def openid_from_response(self, response: dict, session=None) -> OpenID:
        return OpenID(id=response["sub"], email=response.get("email"), provider=self.provider)


class FakeSSOWithoutJwks(FakeSSO):
    async def get_discovery_document(self) -> DiscoveryDocument:
        document = await super().get_discovery_document()
        del document["jwks_uri"]
        return document


@pytest.fixture()
def sso(monkeypatch: pytest.MonkeyPatch) -> FakeSSO:
    monkeypatch.setenv("OAUTHLIB_INSECURE_TRANSPORT", "1")
    return FakeSSO(CLIENT_ID, "client_secret")


def public_jwk(key=private_key, kid="test-key") -> dict:
    jwk = json.loads(RSAAlgorithm.to_jwk(key.public_key()))
    jwk.update({"kid": kid, "alg": "RS256", "use": "sig"})
    return jwk


def token(key=private_key, kid="test-key", aud=CLIENT_ID, algorithm="RS256", **claims) -> str:
    payload = {"sub": "user-id", "email": "user@example.com", "aud": aud, "iss": "https://fake.com", **claims}
    headers = {"kid": kid} if kid else {}
    return jwt.encode(payload, key, algorithm=algorithm, headers=headers)


def signed(userinfo: str) -> Response:
    return Response(text=userinfo, headers={"content-type": "application/jwt"})


def make_client(userinfo: Response, keys: list[dict] | None = None):
    jwks = Response(json_content={"keys": [public_jwk()] if keys is None else keys})

    class FakeAsyncClient:
        headers = {}

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            self.headers = {}
            return None

        async def get(self, url, *args, **kwargs) -> Response:
            return jwks if str(url) == JWKS_URI else userinfo

        async def post(self, *args, **kwargs) -> Response:
            return Response(json_content={"access_token": "token"})

    return FakeAsyncClient


async def login(sso: SSOBase, monkeypatch, userinfo: Response, keys: list[dict] | None = None, convert: bool = False):
    async with sso:
        monkeypatch.setattr("httpx.AsyncClient", make_client(userinfo, keys))
        return await sso.process_login(
            "code",
            Request(url="https://fake.com/callback?code=code&state=unique"),
            convert_response=convert,
        )


async def test_json_response_is_still_supported(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    userinfo = Response(
        json_content={"sub": "user-id", "email": "user@example.com"},
        text='{"sub": "user-id", "email": "user@example.com"}',
        headers={"content-type": "application/json"},
    )
    assert await login(sso, monkeypatch, userinfo) == {"sub": "user-id", "email": "user@example.com"}


async def test_signed_response_is_verified(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    content = await login(sso, monkeypatch, signed(token()))
    assert content["sub"] == "user-id"
    assert content["email"] == "user@example.com"


async def test_signed_response_is_detected_without_content_type(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    content = await login(sso, monkeypatch, Response(text=token()))
    assert content["sub"] == "user-id"


async def test_json_response_with_charset_is_supported(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    userinfo = Response(
        json_content={"sub": "user-id"},
        text='{"sub": "user-id"}',
        headers={"content-type": "application/json; charset=utf-8"},
    )
    assert await login(sso, monkeypatch, userinfo) == {"sub": "user-id"}


async def test_json_body_with_an_unknown_content_type_is_supported(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    userinfo = Response(
        json_content={"sub": "user-id"},
        text='{"sub": "user-id"}',
        headers={"content-type": "text/plain"},
    )
    assert await login(sso, monkeypatch, userinfo) == {"sub": "user-id"}


async def test_signed_response_without_kid_is_accepted(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    content = await login(sso, monkeypatch, signed(token(kid=None)))
    assert content["sub"] == "user-id"


async def test_signed_response_without_kid_tries_every_key(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    keys = [public_jwk(), public_jwk(other_private_key, kid="rotated-key")]
    content = await login(sso, monkeypatch, signed(token(key=other_private_key, kid=None)), keys=keys)
    assert content["sub"] == "user-id"


async def test_signed_response_with_kid_uses_the_matching_key(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    keys = [public_jwk(), public_jwk(other_private_key, kid="rotated-key")]
    content = await login(sso, monkeypatch, signed(token(key=other_private_key, kid="rotated-key")), keys=keys)
    assert content["sub"] == "user-id"


async def test_signed_response_signed_by_an_unknown_key_is_rejected(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(SSOLoginError, match="Invalid signed userinfo response"):
        await login(sso, monkeypatch, signed(token(key=other_private_key, kid=None)))


async def test_signed_response_can_be_converted_to_openid(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    openid = await login(sso, monkeypatch, signed(token()), convert=True)
    assert openid.id == "user-id"
    assert openid.email == "user@example.com"


async def test_unknown_kid_is_rejected(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(SSOLoginError, match="No key matching kid"):
        await login(sso, monkeypatch, signed(token(kid="another-key")))


async def test_invalid_signature_is_rejected(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(SSOLoginError, match="Invalid signed userinfo response"):
        await login(sso, monkeypatch, signed(token(key=other_private_key)))


async def test_all_key_failures_are_reported(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    keys = [public_jwk(), public_jwk(other_private_key, kid="rotated-key")]
    with pytest.raises(SSOLoginError, match=r"test-key.*rotated-key"):
        await login(sso, monkeypatch, signed(token(key=third_private_key, kid=None)), keys=keys)


async def test_wrong_audience_is_rejected(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(SSOLoginError, match="Invalid signed userinfo response"):
        await login(sso, monkeypatch, signed(token(aud="another-client")))


async def test_symmetric_algorithm_is_rejected(sso: FakeSSO, monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(SSOLoginError, match="Invalid signed userinfo response"):
        await login(sso, monkeypatch, signed(token(key="client_secret", algorithm="HS256")))


async def test_missing_jwks_uri_is_rejected(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OAUTHLIB_INSECURE_TRANSPORT", "1")
    sso = FakeSSOWithoutJwks(CLIENT_ID, "client_secret")
    with pytest.raises(SSOLoginError, match="exposes no jwks_uri"):
        await login(sso, monkeypatch, signed(token()))

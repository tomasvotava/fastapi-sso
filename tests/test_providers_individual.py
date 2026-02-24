from typing import cast
from unittest.mock import MagicMock

import jwt
import pytest
from starlette.datastructures import URL
from starlette.requests import Request
from utils import Response, make_fake_async_client

from fastapi_sso import AppleSSO, BitbucketSSO, NotionSSO, OpenID, SSOLoginError


async def test_notion_openid_response():
    sso = NotionSSO("client_id", "client_secret")
    valid_response = {
        "bot": {
            "owner": {
                "type": "user",
                "user": {
                    "id": "test",
                    "person": {"email": "test@example.com"},
                    "avatar_url": "avatar",
                    "name": "Test User",
                },
            }
        }
    }
    invalid_response = {"bot": {"owner": {"type": "workspace", "workspace": {}}}}
    with pytest.raises(SSOLoginError):
        await sso.openid_from_response(invalid_response)
    openid = OpenID(id="test", email="test@example.com", display_name="Test User", picture="avatar", provider="notion")
    assert await sso.openid_from_response(valid_response) == openid


async def test_bitbucket_openid_response():
    sso = BitbucketSSO("client_id", "client_secret")
    valid_response = {
        "uuid": "00000000-0000-0000-0000-000000000000",
        "nickname": "testuser",
        "links": {"avatar": {"href": "https://example.com/myavatar.png"}},
        "display_name": "Test User",
    }

    class FakeSesssion:
        async def get(self, url: str) -> MagicMock:
            response = MagicMock()
            response.json.return_value = {"values": [{"email": "test@example.com"}]}
            return response

    openid = OpenID(
        id=valid_response["uuid"],
        display_name=valid_response["display_name"],
        provider="bitbucket",
        email="test@example.com",
        first_name="testuser",
        picture=valid_response["links"]["avatar"]["href"],
    )

    with pytest.raises(ValueError, match="Session is required to make HTTP requests"):
        await sso.openid_from_response(valid_response)

    assert openid == await sso.openid_from_response(valid_response, FakeSesssion())


async def test_apple_login_url_uses_form_post():
    sso = AppleSSO("client_id", "client_secret", redirect_uri="https://localhost/auth/callback")
    async with sso:
        url = await sso.get_login_url()
    assert "response_mode=form_post" in url


async def test_apple_verify_and_process_form_post_callback(monkeypatch: pytest.MonkeyPatch):
    sso = AppleSSO("client_id", "client_secret", redirect_uri="https://localhost/auth/callback")
    fake_id_token = jwt.encode({"email": "user@idtoken.com"}, key="test", algorithm="HS256")
    fake_user_info = Response(url="https://localhost", json_content={"ok": True})
    FakeAsyncClient = make_fake_async_client(
        returns_post=Response(url="https://localhost", json_content={"access_token": "token", "id_token": fake_id_token}),
        returns_get=fake_user_info,
    )

    class PostRequest:
        method = "POST"
        query_params = {}
        headers = {}
        cookies = {}
        url = URL("https://localhost/auth/callback")

        @staticmethod
        async def form():
            return {"code": "code", "state": "state"}

    monkeypatch.setattr("httpx.AsyncClient", FakeAsyncClient)
    monkeypatch.setattr("jwt.decode", lambda _, options: {"sub": "apple-user-id", "email": "test@example.com"})

    async with sso:
        user = await sso.verify_and_process(cast(Request, PostRequest()))

    assert user is not None
    assert user.id == "apple-user-id"
    assert user.email == "test@example.com"

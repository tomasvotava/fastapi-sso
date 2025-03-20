from unittest.mock import MagicMock

import pytest

from fastapi_sso import BitbucketSSO, NotionSSO, OpenID, SSOLoginError


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

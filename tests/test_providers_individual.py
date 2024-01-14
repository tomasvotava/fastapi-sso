import pytest
from fastapi_sso import NotionSSO, OpenID, SSOLoginError


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

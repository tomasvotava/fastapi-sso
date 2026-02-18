from typing import Any

import pytest

from fastapi_sso.sso.base import OpenID, SSOBase
from fastapi_sso.sso.apple import AppleSSO
from fastapi_sso.sso.discord import DiscordSSO
from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.fitbit import FitbitSSO
from fastapi_sso.sso.github import GithubSSO
from fastapi_sso.sso.gitlab import GitlabSSO
from fastapi_sso.sso.kakao import KakaoSSO
from fastapi_sso.sso.line import LineSSO
from fastapi_sso.sso.linkedin import LinkedInSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from fastapi_sso.sso.naver import NaverSSO
from fastapi_sso.sso.soundcloud import SoundcloudSSO
from fastapi_sso.sso.spotify import SpotifySSO
from fastapi_sso.sso.tidal import TidalSSO
from fastapi_sso.sso.twitter import TwitterSSO
from fastapi_sso.sso.yandex import YandexSSO

sso_test_cases: tuple[tuple[type[SSOBase], dict[str, Any], OpenID], ...] = (
    (
        AppleSSO,
        {"sub": "apple-user-id", "email": "test@example.com"},
        OpenID(id="apple-user-id", email="test@example.com", provider="apple"),
    ),
    (
        TwitterSSO,
        {"data": {"id": "test", "username": "TestUser1234", "name": "Test User"}},
        OpenID(id="test", display_name="TestUser1234", first_name="Test", last_name="User", provider="twitter"),
    ),
    (
        SpotifySSO,
        {"email": "test@example.com", "display_name": "testuser", "id": "test", "images": [{"url": "https://myimage"}]},
        OpenID(
            id="test", provider="spotify", display_name="testuser", email="test@example.com", picture="https://myimage"
        ),
    ),
    (
        SoundcloudSSO,
        {
            "id": 123456,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "avatar_url": "https://myimage",
        },
        OpenID(
            id="123456",
            first_name="Test",
            last_name="User",
            display_name="testuser",
            picture="https://myimage",
            provider="soundcloud",
        ),
    ),
    (
        TidalSSO,
        {
            "id": "123456",
            "firstName": "Test",
            "lastName": "User",
            "username": "testuser",
            "email": "test@example.com",
        },
        OpenID(
            id="123456",
            first_name="Test",
            last_name="User",
            display_name="testuser",
            email="test@example.com",
            provider="tidal",
        ),
    ),
    (
        NaverSSO,
        {
            "response": {
                "nickname": "test",
                "profile_image": "https://myimage",
                "id": "test",
                "email": "test@example.com",
            }
        },
        OpenID(id="test", email="test@example.com", display_name="test", provider="naver", picture="https://myimage"),
    ),
    (
        MicrosoftSSO,
        {"mail": "test@example.com", "displayName": "Test User", "id": "test", "givenName": "Test", "surname": "User"},
        OpenID(
            email="test@example.com",
            display_name="Test User",
            id="test",
            provider="microsoft",
            first_name="Test",
            last_name="User",
        ),
    ),
    (
        LinkedInSSO,
        {
            "email": "test@example.com",
            "sub": "test",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://myimage",
        },
        OpenID(
            email="test@example.com",
            id="test",
            first_name="Test",
            last_name="User",
            provider="linkedin",
            picture="https://myimage",
        ),
    ),
    (
        LineSSO,
        {"email": "test@example.com", "name": "Test User", "sub": "test", "picture": "https://myimage"},
        OpenID(
            email="test@example.com", display_name="Test User", id="test", picture="https://myimage", provider="line"
        ),
    ),
    (KakaoSSO, {"properties": {"nickname": "Test User"}}, OpenID(provider="kakao", display_name="Test User")),
    (
        # Gitlab Case 1: full name is empty
        GitlabSSO,
        {"email": "test@example.com", "id": "test", "username": "test_user", "avatar_url": "https://myimage"},
        OpenID(
            email="test@example.com", id="test", display_name="test_user", picture="https://myimage", provider="gitlab"
        ),
    ),
    (
        # Gitlab Case 2: full name contains only first name
        GitlabSSO,
        {
            "email": "test@example.com",
            "id": "test",
            "username": "test_user",
            "avatar_url": "https://myimage",
            "name": "Test",
        },
        OpenID(
            email="test@example.com",
            id="test",
            display_name="test_user",
            picture="https://myimage",
            first_name="Test",
            last_name=None,
            provider="gitlab",
        ),
    ),
    (
        # Gitlab Case 3: full name contains long last name
        GitlabSSO,
        {
            "email": "test@example.com",
            "id": "test",
            "username": "test_user",
            "avatar_url": "https://myimage",
            "name": "Test User Long Last Name",
        },
        OpenID(
            email="test@example.com",
            id="test",
            display_name="test_user",
            picture="https://myimage",
            first_name="Test",
            last_name="User Long Last Name",
            provider="gitlab",
        ),
    ),
    (
        # Gitlab Case 4: full name contains standard first and last names
        GitlabSSO,
        {
            "email": "test@example.com",
            "id": "test",
            "username": "test_user",
            "avatar_url": "https://myimage",
            "name": "Test User",
        },
        OpenID(
            email="test@example.com",
            id="test",
            display_name="test_user",
            picture="https://myimage",
            first_name="Test",
            last_name="User",
            provider="gitlab",
        ),
    ),
    (
        # Gitlab Case 5: full name contains invalid type or data
        GitlabSSO,
        {
            "email": "test@example.com",
            "id": "test",
            "username": "test_user",
            "avatar_url": "https://myimage",
            "name": {"invalid": 1},
        },
        OpenID(
            email="test@example.com",
            id="test",
            display_name="test_user",
            picture="https://myimage",
            first_name=None,
            last_name=None,
            provider="gitlab",
        ),
    ),
    (
        GithubSSO,
        {"email": "test@example.com", "id": "test", "login": "testuser", "avatar_url": "https://myimage"},
        OpenID(
            email="test@example.com", id="test", display_name="testuser", picture="https://myimage", provider="github"
        ),
    ),
    (
        FitbitSSO,
        {"user": {"encodedId": "test", "fullName": "Test", "displayName": "Test User", "avatar": "https://myimage"}},
        OpenID(id="test", first_name="Test", display_name="Test User", provider="fitbit", picture="https://myimage"),
    ),
    (
        FacebookSSO,
        {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "name": "Test User",
            "id": "test",
            "picture": {"data": {"url": "https://myimage"}},
        },
        OpenID(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            display_name="Test User",
            id="test",
            provider="facebook",
            picture="https://myimage",
        ),
    ),
    (
        YandexSSO,
        {
            "id": "test",
            "display_name": "test",
            "first_name": "Test",
            "last_name": "User",
            "default_email": "test@example.com",
            "default_avatar_id": "123456",
        },
        OpenID(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            display_name="test",
            id="test",
            provider="yandex",
            picture="https://avatars.yandex.net/get-yapic/123456/islands-200",
        ),
    ),
    (
        DiscordSSO,
        {
            "id": "test",
            "avatar": "avatar",
            "email": "test@example.com",
            "global_name": "Test User",
            "username": "testuser",
        },
        OpenID(
            email="test@example.com",
            first_name="testuser",
            id="test",
            picture="https://cdn.discordapp.com/avatars/test/avatar.png",
            provider="discord",
            display_name="Test User",
        ),
    ),
)


@pytest.mark.parametrize(("ProviderClass", "response", "openid"), sso_test_cases)
async def test_provider_openid_by_response(
    ProviderClass: type[SSOBase], response: dict[str, Any], openid: OpenID
) -> None:
    sso = ProviderClass("client_id", "client_secret")
    async with sso:
        assert await sso.openid_from_response(response) == openid

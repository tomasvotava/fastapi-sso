import pytest
from fastapi_sso.sso.base import OpenID, SSOBase
from typing import Dict, Type, Tuple, Any

from fastapi_sso.sso.twitter import TwitterSSO
from fastapi_sso.sso.naver import NaverSSO
from fastapi_sso.sso.spotify import SpotifySSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from fastapi_sso.sso.linkedin import LinkedInSSO
from fastapi_sso.sso.line import LineSSO
from fastapi_sso.sso.kakao import KakaoSSO
from fastapi_sso.sso.gitlab import GitlabSSO
from fastapi_sso.sso.github import GithubSSO
from fastapi_sso.sso.fitbit import FitbitSSO
from fastapi_sso.sso.facebook import FacebookSSO

sso_mapping: Dict[Type[SSOBase], Tuple[Dict[str, Any], OpenID]] = {
    TwitterSSO: (
        {"data": {"id": "test", "username": "TestUser1234", "name": "Test User"}},
        OpenID(id="test", display_name="TestUser1234", first_name="Test", last_name="User", provider="twitter"),
    ),
    SpotifySSO: (
        {"email": "test@example.com", "display_name": "testuser", "id": "test", "images": [{"url": "https://myimage"}]},
        OpenID(
            id="test", provider="spotify", display_name="testuser", email="test@example.com", picture="https://myimage"
        ),
    ),
    NaverSSO: ({"properties": {"nickname": "test"}}, OpenID(display_name="test", provider="naver")),
    MicrosoftSSO: (
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
    LinkedInSSO: (
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
    LineSSO: (
        {"email": "test@example.com", "name": "Test User", "sub": "test", "picture": "https://myimage"},
        OpenID(
            email="test@example.com", display_name="Test User", id="test", picture="https://myimage", provider="line"
        ),
    ),
    KakaoSSO: ({"properties": {"nickname": "Test User"}}, OpenID(provider="kakao", display_name="Test User")),
    GitlabSSO: (
        {"email": "test@example.com", "id": "test", "username": "test_user", "avatar_url": "https://myimage"},
        OpenID(
            email="test@example.com", id="test", display_name="test_user", picture="https://myimage", provider="gitlab"
        ),
    ),
    GithubSSO: (
        {"email": "test@example.com", "id": "test", "login": "testuser", "avatar_url": "https://myimage"},
        OpenID(
            email="test@example.com", id="test", display_name="testuser", picture="https://myimage", provider="github"
        ),
    ),
    FitbitSSO: (
        {"user": {"encodedId": "test", "fullName": "Test", "displayName": "Test User", "avatar": "https://myimage"}},
        OpenID(id="test", first_name="Test", display_name="Test User", provider="fitbit", picture="https://myimage"),
    ),
    FacebookSSO: (
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
}


@pytest.mark.parametrize(
    ("ProviderClass", "response", "openid"), [(key, value[0], value[1]) for key, value in sso_mapping.items()]
)
async def test_provider_openid_by_response(
    ProviderClass: Type[SSOBase], response: Dict[str, Any], openid: OpenID
) -> None:
    sso = ProviderClass("client_id", "client_secret")
    with sso:
        assert await sso.openid_from_response(response) == openid

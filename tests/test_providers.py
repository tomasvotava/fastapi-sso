# type: ignore

from fastapi_sso.sso.facebook import FacebookSSO
from fastapi_sso.sso.fitbit import FitbitSSO
from fastapi_sso.sso.generic import create_provider
from fastapi_sso.sso.github import GithubSSO
from fastapi_sso.sso.gitlab import GitlabSSO
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.kakao import KakaoSSO
from fastapi_sso.sso.microsoft import MicrosoftSSO
from fastapi_sso.sso.naver import NaverSSO
from fastapi_sso.sso.spotify import SpotifySSO

tested_providers = (
    FacebookSSO,
    FitbitSSO,
    GithubSSO,
    GitlabSSO,
    GoogleSSO,
    KakaoSSO,
    MicrosoftSSO,
    NaverSSO,
    SpotifySSO,
)


class TestProviders:
    async def test_discovery_document(self):
        for Provider in tested_providers:
            sso = Provider("client_id", "client_secret")
            document = await sso.get_discovery_document()
            for item in ("authorization_endpoint", "token_endpoint", "userinfo_endpoint"):
                assert item in document, f"Discovery document for provider {sso.provider} must have {item}"

"""This package includes all the concrete SSO implementations.
All of them must inherit from SSOBase class.
"""

__all__ = (
    "FacebookSSO",
    "FitbitSSO",
    "GithubSSO",
    "GitlabSSO",
    "GoogleSSO",
    "KakaoSSO",
    "MicrosoftSSO",
    "NaverSSO",
    "NotionSSO",
    "SpotifySSO",
)

from .facebook import FacebookSSO
from .fitbit import FitbitSSO
from .github import GithubSSO
from .gitlab import GitlabSSO
from .google import GoogleSSO
from .kakao import KakaoSSO
from .microsoft import MicrosoftSSO
from .naver import NaverSSO
from .notion import NotionSSO
from .spotify import SpotifySSO

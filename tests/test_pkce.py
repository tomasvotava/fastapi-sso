import pytest

from fastapi_sso.pkce import get_code_verifier


@pytest.mark.parametrize(("requested", "expected"), [(100, 100), (20, 43), (200, 128)])
def test_pkce_selected_length(requested: int, expected: int) -> None:
    assert expected == len(get_code_verifier(requested))

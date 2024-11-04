# type: ignore

import os

import pytest
from utils import Request

from fastapi_sso.sso.base import SecurityWarning, SSOBase, SSOLoginError, UnsetStateWarning, requires_async_context


class TestSSOBase:
    def test_base(self):
        sso = SSOBase("client_id", "client_secret")
        assert sso.client_id == "client_id"
        assert sso.client_secret == "client_secret"
        assert sso._oauth_client is None
        assert sso._refresh_token is None
        assert sso._state is None
        with pytest.warns(SecurityWarning, match="Please make sure you are using SSO provider in an async context"):
            assert sso.oauth_client is not None
            assert sso.access_token is None
            assert sso.refresh_token is None
            assert sso.id_token is None

    async def test_unset_usage(self):
        sso = SSOBase("client_id", "client_secret")
        with pytest.warns(UnsetStateWarning):
            assert sso.state is None

        with pytest.raises(ValueError):
            await sso.get_login_url()

    def test_state_warning(self):
        with pytest.warns(UnsetStateWarning):
            sso = SSOBase("client_id", "client_secret")
            sso.state

    def test_deprecated_use_state_warning(self):
        with pytest.warns(DeprecationWarning):
            SSOBase("client_id", "client_secret", use_state=True)

    async def test_not_implemented_ssobase(self):
        sso = SSOBase("client_id", "client_secret")
        with pytest.raises(NotImplementedError):
            await sso.openid_from_response({})
        with pytest.raises(NotImplementedError):
            await sso.get_discovery_document()

        request = Request()
        request.query_params["code"] = "code"
        with pytest.raises(NotImplementedError), pytest.warns(
            SecurityWarning, match="Please make sure you are using SSO provider in an async context"
        ):
            await sso.verify_and_process(request)

        sso.client_id = NotImplemented
        with pytest.raises(NotImplementedError), pytest.warns(
            SecurityWarning, match="Please make sure you are using SSO provider in an async context"
        ):
            _ = sso.oauth_client

    async def test_login_error(self):
        sso = SSOBase("client_id", "client_secret")

        with pytest.raises(SSOLoginError), pytest.warns(
            SecurityWarning, match="Please make sure you are using SSO provider in an async context"
        ):
            await sso.verify_and_process(Request())

    def test_autoset_insecure_transport_env_var(self):
        assert not os.getenv(
            "OAUTHLIB_INSECURE_TRANSPORT"
        ), "OAUTHLIB_INSECURE_TRANSPORT should not be true before test"
        SSOBase("client_id", "client_secret", allow_insecure_http=True)
        assert os.getenv("OAUTHLIB_INSECURE_TRANSPORT"), "OAUTHLIB_INSECURE_TRANSPORT should be truthy after test"

    def test_warns_on_sync_context(self):
        sso = SSOBase("client_id", "client_secret")
        with pytest.warns(DeprecationWarning, match="SSO Providers are supposed to be used in async context"), sso:
            assert sso._state is None
            assert sso._oauth_client is None
            assert sso._id_token is None
            assert sso._refresh_token is None
            assert bool(sso._generated_state) == sso.requires_state
            assert bool(sso._pkce_code_verifier) == bool(sso.uses_pkce)
            assert bool(sso._pkce_code_challenge) == bool(sso.uses_pkce)

    def test_async_context_decorator(self):
        sso = SSOBase("client_id", "client_secret")
        sso._in_stack = False

        @requires_async_context
        def method(sso: SSOBase):
            return

        @requires_async_context
        def function(ret):
            return ret

        with pytest.warns(SecurityWarning, match="Please make sure you are using SSO provider in an async context"):
            method(sso)

        assert function(42) == 42

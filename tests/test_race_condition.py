# See [!186](https://github.com/tomasvotava/fastapi-sso/issues/186)
# Author: @parikls

import asyncio
from unittest.mock import Mock, patch

from starlette.datastructures import URL

from fastapi_sso import create_provider


async def test__race_condition():
    discovery = {
        "authorization_endpoint": "https://authorization_endpoint",
        "token_endpoint": "https://token_endpoint",
        "userinfo_endpoint": "https://userinfo_endpoint",
    }
    factory = create_provider(name="provider", discovery_document=discovery)

    provider = factory(client_id="client_id", client_secret="client_secret")  # noqa: S106

    # mock for the response. will return a token which we've set
    class Response:
        def __init__(self, token: str):
            self.token = token

        def json(self):
            return {
                "refresh_token": self.token,
                "access_token": self.token,
                "id_token": self.token,
            }

    # mock of the httpx client
    class AsyncClient:
        post_responses = []  # list of the responses which a client will return for the `POST` requests

        def __init__(self):
            self.headers = {}

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def post(self, *args, **kwargs):
            await asyncio.sleep(0)  # simulate a loop switch cos it'll happen during a real HTTP request
            return self.post_responses.pop()

        # we actually don't care what GET will return for this particular test,
        # but this method is required to fully run the `process_login` code
        async def get(self, *args, **kwargs):
            await asyncio.sleep(0)
            return Response(token="")

    with patch("fastapi_sso.sso.base.httpx") as httpx:
        httpx.AsyncClient = AsyncClient

        first_response = Response(token="first_token")  # noqa: S106
        second_response = Response(token="second_token")  # noqa: S106

        AsyncClient.post_responses = [second_response, first_response]  # reversed order because of `pop`

        async def process_login():
            # this coro will be executed concurrently.
            # completely not caring about the params
            request = Mock()
            request.url = URL("https://url.com?state=state&code=code")
            async with provider:
                await provider.process_login(
                    code="code", request=request, params=dict(state="state"), convert_response=False
                )
                return provider.access_token

        # process login concurrently twice
        tasks = [process_login(), process_login()]
        results = await asyncio.gather(*tasks)

        # we would want to get the first and second tokens,
        # but we see that the first request actually obtained the second token as well
        assert results == [first_response.token, second_response.token]

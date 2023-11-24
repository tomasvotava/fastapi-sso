from starlette.datastructures import URL


class Request:
    def __init__(self, url="http://localhost", query_params=None):
        self.url = URL(url)
        self.query_params = query_params or {}


class Response:
    def __init__(self, url="http://localhost", json_content=None):
        self.url = URL(url)
        self.json_content = json_content or {}

    def json(self):
        return self.json_content


class AnythingDict:
    def __init__(self, data=None):
        self.data = data or {}

    def __getitem__(self, key):
        return self.data.get(key, "test")

    def __contains__(self, key):
        return True

    def __repr__(self):
        return "<AnythingDict>"

    def get(self, key, default=None):
        return self.data.get(key, default) or "test"


def make_fake_async_client(returns_post: Response, returns_get: Response):
    class FakeAsyncClient:
        headers = {}

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            self.headers = {}
            return None

        async def get(self, *args, **kwargs) -> Response:
            return returns_get

        async def post(self, *args, **kwargs) -> Response:
            return returns_post

    return FakeAsyncClient

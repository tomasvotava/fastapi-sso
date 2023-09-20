from fastapi_sso.sso.base import OpenID
from fastapi_sso.sso.generic import create_provider

DISCOVERY = {
    "authorization_endpoint": "http://localhost:9090/auth",
    "token_endpoint": "http://localhost:9090/token",
    "userinfo_endpoint": "http://localhost:9090/me",
}


class TestGenericProvider:
    async def test_discovery_document_static(self):
        Provider = create_provider(discovery_document=DISCOVERY)
        sso = Provider("client_id", "client_secret")
        document = await sso.get_discovery_document()
        assert document == DISCOVERY

    async def test_discovery_document_callable(self):
        Provider = create_provider(discovery_document=lambda _: DISCOVERY)
        sso = Provider("client_id", "client_secret")
        document = await sso.get_discovery_document()
        assert document == DISCOVERY

    async def test_empty_response_convertor(self):
        Provider = create_provider(discovery_document=DISCOVERY)
        sso = Provider("client_id", "client_secret")
        openid = await sso.openid_from_response({})
        assert openid.provider == Provider.provider
        assert openid.id is None

    async def test_response_convertor(self):
        Provider = create_provider(
            discovery_document=DISCOVERY,
            response_convertor=lambda response: OpenID(
                id=response["id"],
                email=response["email"],
                display_name=response["display_name"],
                data={"gibberish": "lorem ipsum"},
            ),
        )
        sso = Provider("client_id", "client_secret")
        openid_response = {
            "id": "test",
            "email": "email@example.com",
            "display_name": "Test",
            "data": {"gibberish": "lorem ipsum"}
        }
        openid = await sso.openid_from_response(openid_response)
        assert openid.provider is None
        assert openid.id == openid_response["id"]
        assert openid.email == openid_response["email"]
        assert openid.display_name == openid_response["display_name"]
        assert openid.data == openid_response["data"]

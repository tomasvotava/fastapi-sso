from fastapi_sso.infrastructure import DiscoveryDocument, OpenID, factories

DISCOVERY: DiscoveryDocument = {
    "authorization_endpoint": "http://localhost:9090/auth",
    "token_endpoint": "http://localhost:9090/token",
    "userinfo_endpoint": "http://localhost:9090/me",
}


class TestGenericProvider:
    async def test_discovery_document_static(self):
        Provider = factories.create_provider(discovery_document=DISCOVERY)
        sso = Provider("client_id", "client_secret")
        document = await sso.get_discovery_document()
        assert document == DISCOVERY

    async def test_discovery_document_callable(self):
        Provider = factories.create_provider(discovery_document=lambda _: DISCOVERY)
        sso = Provider("client_id", "client_secret")
        document = await sso.get_discovery_document()
        assert document == DISCOVERY

    async def test_empty_response_convertor(self):
        Provider = factories.create_provider(discovery_document=DISCOVERY)
        sso = Provider("client_id", "client_secret")
        openid = await sso.openid_from_response({})
        assert openid.provider == Provider.provider
        assert openid.id is None

    async def test_response_convertor(self):
        Provider = factories.create_provider(
            discovery_document=DISCOVERY,
            response_convertor=lambda response, _: OpenID(
                id=response["id"], email=response["email"], display_name=response["display_name"]
            ),
        )
        sso = Provider("client_id", "client_secret")
        openid_response = {"id": "test", "email": "email@example.com", "display_name": "Test"}
        openid = await sso.openid_from_response(openid_response)
        assert openid.provider is None
        assert openid.id == openid_response["id"]
        assert openid.email == openid_response["email"]
        assert openid.display_name == openid_response["display_name"]

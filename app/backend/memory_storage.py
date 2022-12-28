from fhir_kindling import FhirServer
from app.backend.models.server import Server


class Store:
    _server: Server

    def __init__(self):
        self.store = {}
        self._server = None

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value

    def set_server_config(self, server: Server):
        self._server = server

    def get_server_config(self):
        if self._server:
            return self._server
        else:
            raise ValueError("Server not set")

    def get_server_connection(self) -> FhirServer:
        if self._server:
            return FhirServer(
                api_address=self._server.api_url,
                username=self._server.credentials.username,
                password=self._server.credentials.password,
                token=self._server.credentials.token,
            )
        else:
            raise ValueError("Server not set")


store = Store()

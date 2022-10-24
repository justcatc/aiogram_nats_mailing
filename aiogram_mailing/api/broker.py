from typing import Any, List, Optional, TypeAlias, Union

import nats
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.js.client import JetStreamContext

SERVERS: TypeAlias = Union[str, List[str]]
Event: TypeAlias = Msg


class NatsBroker:
    def __init__(
        self,
        servers: SERVERS,
        user: Optional[str] = None,
        password: Optional[str] = None,
        **options: Any,
    ):
        if isinstance(servers, str):
            servers = [servers]
        self.servers = servers
        options["user"] = user
        options["password"] = password
        self.options = options
        self._connection: Optional[Client] = None

    @property
    def _connection_exists(self) -> bool:
        return self._connection is not None and not self._connection.is_closed

    @property
    def connection(self) -> Client:
        if not self._connection_exists:
            raise RuntimeError("Connection is not created")
        return self._connection

    @connection.setter
    def connection(self, value: Client):
        if self._connection_exists:
            raise RuntimeError(
                "For reset connection " "use .set_connection method"
            )
        self._connection = value

    async def close_connection(self):
        if self._connection:
            if not self._connection.is_closed:
                await self._connection.close()
            self._connection = None

    async def new_connection(self) -> Client:
        return await nats.connect(servers=self.servers, **self.options)

    async def set_connection(self, connection: Client):
        await self.close_connection()
        self.connection = connection

    async def create_connection(self) -> Client:
        conn = await self.new_connection()
        await self.set_connection(conn)
        return conn

    async def get_connection(self) -> Client:
        if not self._connection_exists:
            return await self.create_connection()
        return self.connection

    async def get_context(self) -> JetStreamContext:
        return (await self.get_connection()).jetstream()

from typing import Any, Dict, Optional

from nats.js.api import (
    DiscardPolicy,
    PubAck,
    RetentionPolicy,
    StorageType,
    StreamInfo,
)
from nats.js.errors import BadRequestError

from .broker import SERVERS, NatsBroker

DEFAULT_STREAM_CONF = dict(
    discard=DiscardPolicy.OLD,
    retention=RetentionPolicy.INTEREST,
    storage=StorageType.FILE,
)


class NatsPublisher(NatsBroker):
    def __init__(
        self,
        servers: SERVERS,
        user: Optional[str] = None,
        password: Optional[str] = None,
        **options: Any,
    ):
        super().__init__(servers, user, password, **options)
        self._streams: Dict[str, StreamInfo] = {}

    def _check_stream(self, name: str):
        if name not in self._streams:
            raise KeyError(f"Stream {name!r} not found")

    async def add_stream(self, name: str, **conf: Any):
        if name in self._streams:
            raise RuntimeError("Stream already added")
        ctx = await self.get_context()
        try:
            config = DEFAULT_STREAM_CONF.copy()
            config.update(conf)
            stream = await ctx.add_stream(name=name, **config)
        except BadRequestError:
            stream = await ctx.stream_info(name=name)

        self._streams[name] = stream

    async def purge_stream(self, name: str, **options: Any):
        self._check_stream(name)
        ctx = await self.get_context()
        await ctx.purge_stream(name=name, **options)

    async def delete_stream(self, name: str, **options: Any):
        self._check_stream(name)
        ctx = await self.get_context()
        await ctx.delete_stream(name=name)
        del self._streams[name]

    async def publish(
        self,
        stream: str,
        subject: str,
        payload: bytes,
        headers: Optional[Dict[str, Any]] = None,
    ) -> PubAck:
        return await (await self.get_context()).publish(
            subject=subject, payload=payload, stream=stream, headers=headers
        )

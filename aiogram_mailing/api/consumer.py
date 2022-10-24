from typing import Any, Dict, Optional

from nats.aio.subscription import Subscription

from .broker import SERVERS, Event, NatsBroker


class NatsConsumer(NatsBroker):
    def __init__(
        self,
        servers: SERVERS,
        user: Optional[str] = None,
        password: Optional[str] = None,
        **options: Any,
    ):
        super().__init__(servers, user, password, **options)
        self._subscribtions: Dict[str, Subscription] = {}

    def _check_sub(self, name: str):
        if name not in self._subscribtions:
            raise KeyError(f"Subscribtion {name!r} not found")

    def _as_name(self, stream: str, name: str) -> str:
        return f"{stream}:{name}"

    async def handle_event(self, event: Event):
        pass

    async def subscribe(self, stream: str, name: str):
        key = self._as_name(stream, name)
        if key in self._subscribtions:
            raise RuntimeError("Sunscribtion arleady added")
        ctx = await self.get_context()
        sub = await ctx.subscribe(
            subject=name, queue="workers", stream=stream, cb=self.handle_event
        )
        self._subscribtions[key] = sub

    async def unsubscribe(self, stream: str, name: str):
        key = self._as_name(stream, name)
        self._check_sub(key)
        sub = self._subscribtions[key]
        await sub.unsubscribe()

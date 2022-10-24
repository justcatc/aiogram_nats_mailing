from typing import Any, Optional

import ormsgpack
from aiogram import Bot
from nats.errors import TimeoutError

from .api.broker import SERVERS, Event
from .api.consumer import NatsConsumer
from .message import Message


class MessageConsumer(NatsConsumer):
    def __init__(
        self,
        bot: Bot,
        servers: SERVERS,
        user: Optional[str] = None,
        password: Optional[str] = None,
        **options: Any,
    ):
        super().__init__(servers, user, password, **options)
        self.bot = bot

    async def handle_message(self, msg: Message):
        raise NotImplementedError

    async def handle_event(self, event: Event):
        try:
            await self.handle_message(
                msg=Message(**ormsgpack.unpackb(event.data))
            )
        except TimeoutError:
            await event.nak()
        else:
            await event.ack()

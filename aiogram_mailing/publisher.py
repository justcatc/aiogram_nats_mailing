import ormsgpack

from .api.publisher import NatsPublisher
from .message import Message


class MessagePublisher(NatsPublisher):
    async def publish_message(
        self, stream: str, subject: str, message: Message
    ):
        await self.publish(
            stream,
            subject,
            ormsgpack.packb(message, option=ormsgpack.OPT_SERIALIZE_PYDANTIC),
        )

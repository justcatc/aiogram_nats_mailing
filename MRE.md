just example


```python
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramRetryAfter
from aiogram.filters.command import Command

from aiogram_mailing import Event, Message, MessageConsumer, MessagePublisher


class CustomMessageConsumer(MessageConsumer):
    async def handle_message(self, msg: Message):
        await self.bot.send_message(chat_id=msg.chat_id, text=msg.text)

    async def handle_event(self, event: Event):
        try:
            return await super().handle_event(event)
        except TelegramRetryAfter as e:
            await event.nak(e.retry_after)


def get_users_ids() -> int:
    yield from (1234,)


async def add_message(msg: types.Message, publisher: MessagePublisher):
    users_ids = get_users_ids()

    for user_id in users_ids:
        msg = Message(chat_id=user_id, text="hello")
        await publisher.publish_message(
            stream="mailing_stream", subject="mailing_worker", message=msg
        )


async def main():
    bot = Bot("")
    dp = Dispatcher()

    dp.message.register(add_message, Command(commands="add_message"))

    publisher = MessagePublisher(servers="nats://localhost:4222")
    consumer = CustomMessageConsumer(bot=bot, servers="nats://localhost:4222")

    await publisher.add_stream(name="mailing_stream")
    await consumer.subscribe(stream="mailing_stream", name="mailing_worker")

    await dp.start_polling(bot, publisher=publisher)


if __name__ == "__main__":
    asyncio.run(main())
```

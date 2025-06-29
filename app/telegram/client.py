import asyncio
import logging
from utils import setup_logging
from telethon.sync import TelegramClient as TelethonClient
from config import TelegramClientConfig
from .dialog_manager import DialogManager, Message


class TelegramClient:

    def __init__(self, config: TelegramClientConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.server = None
        setup_logging()
        self.client = None
        self.dialog_manager = DialogManager()

    async def init(self):
        self.client = TelethonClient("anon", api_id=self.config.telethon.api_id, api_hash=self.config.telethon.api_hash)
        await self.client.start()


    async def handle_request(self, reader, writer):

        data = await reader.read(1024*100)
        message = data.decode().strip()
        self.logger.info(f"Passed: {message}")

        await self.ask(message)
        for message in self.dialog_manager.messages:
            writer.write((message.author + ':' + message.text + '\n\n').encode())
            await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def ask(self, message):
        self.dialog_manager.add_message(Message(author='@user', text=message))
        await self.client.send_message(
            entity='@grokAI',
            message=message
        )

        response = await self._get_answer()
        self.dialog_manager.add_message(Message(author='@grok', text=response))
        
        return response

    async def _get_answer(self):
        last_message = (await self.client.get_messages('@grokAI', 1))[0]
        new = last_message

        while last_message == new:
            await asyncio.sleep(1)
            new = (await self.client.get_messages('@grokAI', 1))[0]

        self.logger.info(f"GROK: {new.message}")
        return new.message


    async def start(self):
        try:
            self.server = await asyncio.start_server(
                self.handle_request,
                self.config.client.host,
                self.config.client.port
            )
            self.logger.info(f"vim client started on {self.config.client.host}:{self.config.client.port}")
            await self.server.serve_forever()
        finally:
            if self.server:
                await self.stop()

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("Server stopped")

import asyncio
import logging
from utils import setup_logging
from telethon.sync import TelegramClient


class TelegramC:

    def __init__(self, host='127.0.0.1', port=12346):
        self.api_id = 1
        self.api_hash = ""
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.server = None
        setup_logging()
        self.client = None

    async def init(self):
        self.client = TelegramClient("anon", self.api_id, self.api_hash)
        await self.client.start()


    async def handle_request(self, reader, writer):

        data = await reader.read(1024*100)
        message = data.decode().strip()
        self.logger.info(f"Passed: {message}")

        response = (await self.ask(message)).message

        writer.write(response.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def ask(self, message):
        await self.client.send_message(
            entity='@grokAI',
            message=message
        )

        return await self._get_answer()

    async def _get_answer(self):
        last_message = (await self.client.get_messages('@grokAI', 1))[0]
        new = last_message

        while last_message == new:
            await asyncio.sleep(1)
            new = (await self.client.get_messages('@grokAI', 1))[0]
        return new
        

    async def start(self):
        try:
            self.server = await asyncio.start_server(
                self.handle_request,
                self.host,
                self.port
            )
            self.logger.info(f"vim client started on {self.host}:{self.port}")
            await self.server.serve_forever()
        finally:
            if self.server:
                await self.stop()

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("Server stopped")

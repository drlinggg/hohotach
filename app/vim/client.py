import asyncio
import logging
from utils import setup_logging
from config import ClientConfig


class VimClient:

    def __init__(self, config: ClientConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.server = None
        setup_logging()

    async def handle_request(self, reader, writer):

        data = await reader.read(1024*100)
        message = data.decode().strip()
        self.logger.info(f"Received: {message}")

        response = await self.post_request(message)

        writer.write(response.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def post_request(self, message):
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', 12346)
            writer.write(message.encode())
            await writer.drain()

            data = await reader.read(1024*100)
            response = data.decode()

            writer.close()
            await writer.wait_closed()

            return response

        except Exception as e:
            error_msg = f"TCP error: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    async def start(self):
        try:
            self.server = await asyncio.start_server(
                self.handle_request,
                self.config.host,
                self.config.port
            )
            self.logger.info(f"vim client started on {self.config.host}:{self.config.port}")
            await self.server.serve_forever()
        finally:
            if self.server:
                await self.stop()

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("Server stopped")

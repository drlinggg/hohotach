import asyncio
from vim import VimClient
from telegram import TelegramClient
from config import HohotachConfig
from utils import try_load_envfile
import os

async def main():

    config = HohotachConfig.from_file_or_default()

    vim = VimClient(config.vim_client)
    telegram = TelegramClient(config.telegram_client)
    await telegram.init()

    await asyncio.gather(
        vim.start(),
        telegram.start()
    )

if __name__ == "__main__":
    try_load_envfile(os.environ.get("ENVFILE", ".env"))
    asyncio.run(main())

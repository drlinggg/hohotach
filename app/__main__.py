import asyncio
from vim import VimClient
from telegram import TelegramC

async def main():
    vim = VimClient(host="127.0.0.1", port=12345)
    telegram = TelegramC(host="127.0.0.1", port=12346)
    await telegram.init()

    await asyncio.gather(
        vim.start(),
        telegram.start()
    )

if __name__ == "__main__":
    asyncio.run(main())

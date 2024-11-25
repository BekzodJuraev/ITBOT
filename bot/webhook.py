from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging
import aiohttp
ngrok_url = 'https://188.120.236.240/telegram_webhook/'


bot = Bot(token="7677882278:AAHiw2W0wxkrBZmJEj12DwQryxgR3qucWZ4")
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())
#daphne -p 8000 Statron.asgi:application



async def set_webhook(dispatcher):
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        session = aiohttp.ClientSession(connector=connector)
        webhook_url = f"{ngrok_url}"
        await bot.set_webhook(webhook_url, session=session)
        await session.close()

        logging.info(f"Webhook set to {webhook_url}")
    except Exception as e:
        logging.error(f"Failed to set webhook: {e}")

# Add other handlers here

if __name__ == '__main__':
    executor.start_webhook(
        dispatcher=dp,
        webhook_path='/telegram_webhook/',
        on_startup=set_webhook,
        skip_updates=True,
        host='0.0.0.0',
        port=7000,
    )

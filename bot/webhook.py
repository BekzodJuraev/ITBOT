from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging

ngrok_url = 'https://83d3-5-133-120-92.ngrok-free.app/telegram_webhook/'


bot = Bot(token="7851466499:AAEvRraJBWbhrFyGOpIttv8Bcx22aa2rlxs")

dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())
#daphne -p 8000 Statron.asgi:application



async def set_webhook(dispatcher):
    try:
        webhook_url = f"{ngrok_url}"
        await bot.set_webhook(webhook_url)

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

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging
from config import TOKEN_BOT,DOMAIN
#ngrok_url = 'https://eb6a-213-230-87-48.ngrok-free.app/telegram_webhook/'
ngrok_url = f"{DOMAIN}/telegram_webhook/"
#TOKEN_BOT="5135151315:AAHypfMOijVW2fE5SM4iQr8LB3bCn0yaS7Q"

bot = Bot(token=TOKEN_BOT)

dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())


async def on_startup(dispatcher):
    try:
        await bot.delete_webhook(drop_pending_updates=True)  # Clears old updates
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook set to {WEBHOOK_URL}")
    except Exception as e:
        logging.error(f"Failed to set webhook: {e}")

if __name__ == '__main__':
    executor.start_webhook(
        dispatcher=dp,
        webhook_path='/telegram_webhook/',
        on_startup=on_startup,  # Calls async on_startup properly
        host='0.0.0.0',
        port=7000,
        skip_updates=True
    )

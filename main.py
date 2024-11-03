import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import aiohttp

API_TOKEN = 'YOUR_API_TOKEN'
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
PROXY_URL = 'YOUR_PROXY_URL'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, proxy=PROXY_URL)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def get_gpt_response(prompt):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150
                },
                proxy=PROXY_URL
            ) as resp:
                if resp.status != 200:
                    logging.error(f"Ошибка API OpenAI: {resp.status}, {await resp.text()}")
                    return "Ошибка запроса к OpenAI API."

                response_data = await resp.json()
                return response_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
    except Exception as e:
        logging.exception("Ошибка при запросе к OpenAI API")
        return "Произошла ошибка при обращении к GPT. Попробуйте позже."

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для общения с GPT. Просто отправьте мне сообщение, и я отвечу.")

@dp.message_handler()
async def echo(message: types.Message):
    response_text = await get_gpt_response(message.text)
    await message.reply(response_text)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)

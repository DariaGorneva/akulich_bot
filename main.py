import threading
from dotenv import load_dotenv
from src.database import Database
load_dotenv()
from src.handlers import init
from src.config import Configuration
import logging
import time
from telebot import telebot, TeleBot
from fastapi import FastAPI
import uvicorn


app = FastAPI(
    title='Bot'
)     # экземпляр приложения


def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)


def start_bot():
    bot: TeleBot = TeleBot(Configuration.TG_TOKEN, skip_pending=True)
    db = Database()
    init(bot, db)
    while True:
        try:
            logging.info("Bot running..")

            print('Running')
            bot.polling(none_stop=True, interval=2)
            break
        except telebot.apihelper.ApiException as e:
            logging.error(e)
            bot.stop_polling()

            time.sleep(15)

            logging.info("Running again!")
    return {'ok'}


@app.get("/")
async def response():
    return {'message': 'Bot running'}


if __name__ == '__main__':
    # Создаем два потока - для сервера и для телеграм-бота
    server_thread = threading.Thread(target=start_server)
    bot_thread = threading.Thread(target=start_bot)

    # Запускаем потоки
    server_thread.start()
    bot_thread.start()

    # Ждем, пока оба потока завершат работу
    server_thread.join()
    bot_thread.join()

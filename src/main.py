from dotenv import load_dotenv
from src.database import Database
load_dotenv()
from src.handlers import init
from src.config import Configuration
import logging
import time
from telebot import telebot, TeleBot


if __name__ == '__main__':
    bot: TeleBot = TeleBot(Configuration.TG_TOKEN, skip_pending=True)
    db = Database()
    init(bot, db)

    while True:
        try:
            logging.info("Bot running..")
            bot.polling(none_stop=True, interval=2)
            break
        except telebot.apihelper.ApiException as e:
            logging.error(e)
            bot.stop_polling()

            time.sleep(15)

            logging.info("Running again!")

import os
import gspread as gspread


class Configuration:  # заменяем calldadta кнопок
    NEW_PURCHASE = 'Новая покупка'
    ADD_CATEGORY_KEY = 'Добавить категорию'
    ADD_PRICE_KEY = 'Добавить цену'
    ADD_COMMENT_KEY = 'Добавить комментарий'
    DONE_PURCHASE_KEY = 'Готово'
    USERS = [int(os.getenv('USER_1')), int(os.getenv('USER_2'))]
    TG_TOKEN = os.getenv('TG_TOKEN')
    GOOGLE_TOKEN = os.getenv('GOOGLE_TOKEN')
    SERVICE_ACCOUNT = os.getenv('SERVICE_ACCOUNT')
    APP_DOMAIN = os.getenv('APP_URL')


# подключаемся к гугл-таблицам
gc = gspread.service_account(Configuration.SERVICE_ACCOUNT)


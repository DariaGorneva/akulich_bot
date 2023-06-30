from dotenv import load_dotenv
from src.database import Database
load_dotenv()
from src.message_processor import MessageProcessor
from src.config import Configuration
from fastapi import FastAPI
import uvicorn
import requests
from fastapi.responses import Response
from src.pydantic_models import TelegramUpdate


app = FastAPI(
    title='Bot'
)
db = Database()


@app.on_event('startup')    # когда поднимаем сайт
def on_startup():
    requests.get(
        url=f'https://api.telegram.org/bot{Configuration.TG_TOKEN}/setWebhook?url={Configuration.APP_DOMAIN}/update'
    )


@app.post('/update')
async def telegram_update(request: TelegramUpdate):
    print(request)
    processor = MessageProcessor(db)
    try:
        processor.process(request)
    except Exception as err:
        print(err)

    return Response(status_code=200, content='ok')


def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.get("/")
async def response():
    return {'message': 'Bot running'}


if __name__ == '__main__':
    start_server()


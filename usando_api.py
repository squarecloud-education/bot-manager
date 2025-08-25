import os
from dotenv import load_dotenv
from squarecloud import Client
import squarecloud
import asyncio

load_dotenv(".env", override=True)
SQUARE_KEY = os.getenv("SQUARE_KEY")

client = Client(SQUARE_KEY)

async def main():
    # meus_apps = await client.all_apps()
    # print(meus_apps)

    # app_status = await meu_app.status()
    # print(meu_app.id)
    # print(app_status.cpu)
    # print(app_status.network)
    # print(app_status.storage)
    # print(app_status.uptime)
    # meu_app = await client.app("cda1f1c214414f45ae219134a0ba37d7")
    # await meu_app.restart()
    app_arquivo = squarecloud.File("main.zip")
    await client.upload_app(app_arquivo)


asyncio.run(main())
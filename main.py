import os, discord, zipfile
from squarecloud.client import Client
from squarecloud.file import File
from pathlib import Path
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from views import SelectAplicacoes

load_dotenv(override=True)
BOT_TOKEN = os.getenv("BOT_TOKEN")
SQUARE_KEY = os.getenv("SQUARE_KEY")

intents = discord.Intents.all()
bot = commands.Bot(".", intents=intents)
square_client = Client(SQUARE_KEY)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot pronto!")

@bot.tree.command()
@app_commands.choices(
    linguagem=[
        app_commands.Choice(name="Python", value="python"),
        app_commands.Choice(name='JavaScript', value='javascript')
    ]
)
async def deploy(interaction:discord.Interaction, upload_zip:discord.Attachment, nome:str, descricao:str|None, memoria:int, linguagem:app_commands.Choice[str], arquivo_principal:str):
    if memoria < 256:
        await interaction.response.send_message("O mínimo de memória deve ser 256MB.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)

    zip_path = Path(f'./tmp/{datetime.now().timestamp()}_{upload_zip.filename}')
    await upload_zip.save(zip_path)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip:
            arquivos_no_zip = zip.namelist()
            if arquivo_principal not in arquivos_no_zip:
                await interaction.followup.send(f"O arquivo principal `{arquivo_principal}` não está no zip enviado.")
                os.unlink(zip_path)
                return
    except Exception as erro:
        await interaction.followup.send("O zip está incorreto ou inválido.")
        print(erro)
        return

    linhas = [
        f"MAIN={arquivo_principal}",
        f"MEMORY={memoria}",
        f"VERSION=recommended",
        f"DISPLAY_NAME={nome}"
    ]
    if descricao:
        linhas.append(f"DESCRIPTION={descricao}")

    conteudo_config = "\n".join(linhas)

    with zipfile.ZipFile(zip_path, 'a') as zip:
        if 'squarecloud.app' not in zip.namelist() and 'squarecloud.config' not in zip.namelist():
            zip.writestr("squarecloud.app", conteudo_config)
        dependencias_arquivos = {
            'python':'requirements.txt',
            'javascript':'package.json'
        }
        if dependencias_arquivos[linguagem.value] not in zip.namelist():
            await interaction.followup.send(f"O arquivo de dependências está ausente. Inclua o `{dependencias_arquivos[linguagem.value]}` no projeto.")
            return
    
    await square_client.upload_app(File(zip_path))
    os.unlink(zip_path)
    await interaction.followup.send("A aplicação foi enviada para a hospedagem com sucesso.")

@bot.tree.command()
async def apps(interaction:discord.Interaction):
    aplicacoes = await square_client.all_apps()
    if not aplicacoes:
        await interaction.response.send_message(f"Você não tem nenhuma aplicação hospedada.")
        return
    
    await interaction.response.defer(ephemeral=True)
    view = discord.ui.View()
    view.add_item(SelectAplicacoes(aplicacoes))
    await interaction.followup.send("Teste", view=view)


bot.run(BOT_TOKEN)
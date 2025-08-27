import discord
from discord.ui import Select, Button
from squarecloud import Application, StatusData

class EmbedAplicacao(discord.Embed):
    def __init__(self, app:Application, status_app:StatusData):
        super().__init__()
        self.title = app.name
        descricao = [
            f"```{app.desc}```" if app.desc else "",
            "🟢`Online`" if status_app.running else "🔴`Offline`"
        ]
        descricao = "\n".join(descricao)
        self.description= descricao
        self.add_field(name="CPU", value=status_app.cpu)
        self.add_field(name="RAM", value=status_app.ram)
        self.add_field(name="Armazenamento", value=status_app.storage)
        self.add_field(name="Rede Total", value=status_app.network['total'])


class SelectAplicacoes(Select):
    def __init__(self, aplicacoes:list[Application]):
        self.aplicacoes = aplicacoes
        opcoes = []
        for app in aplicacoes:
            opcoes.append(discord.SelectOption(label=app.name, value=app.id))
        
        super().__init__(placeholder="Selecione uma aplicação", options=opcoes)
    
    async def callback(self, interact:discord.Interaction):
        app_escolhido = self.values[0]
        for app in self.aplicacoes:
            if app.id == app_escolhido:
                app_escolhido = app
        
        app_status = await app_escolhido.status()
        view = MenuAplicacao(app_escolhido, app_status)

        await interact.response.send_message(embed=EmbedAplicacao(app_escolhido, app_status), view=view)

class MenuAplicacao(discord.ui.View):
    def __init__(self, app:Application, status_app:StatusData):
        self.aplicacao = app
        self.client = app.client
        super().__init__()

        self.botao_iniciar = Button(label="Iniciar", style=discord.ButtonStyle.green, disabled=status_app.running)
        self.botao_parar = Button(label="Parar", style=discord.ButtonStyle.red, disabled=not status_app.running)
        self.botao_reiniciar = Button(label="Reiniciar", style=discord.ButtonStyle.blurple, disabled=not status_app.running)

        self.botao_iniciar.callback = self.iniciar
        self.botao_parar.callback = self.parar
        self.botao_reiniciar.callback = self.reiniciar

        self.add_item(self.botao_iniciar)
        self.add_item(self.botao_parar)
        self.add_item(self.botao_reiniciar)

    
    async def iniciar(self, interaction:discord.Interaction):
        await self.executar_acao(interaction, self.botao_iniciar, "Iniciando...", self.aplicacao.start)

    async def parar(self, interaction:discord.Interaction):
        await self.executar_acao(interaction, self.botao_parar, "Parando...", self.aplicacao.stop)

    async def reiniciar(self, interaction:discord.Interaction):
        await self.executar_acao(interaction, self.botao_reiniciar, "Reiniciando...", self.aplicacao.restart)

    async def executar_acao(self, interaction:discord.Interaction, botao:Button, label_temp:str, acao):
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        botao.label = label_temp
        await interaction.response.edit_message(view=self)

        await acao()
        app_status = await self.aplicacao.status()
        await interaction.message.edit(view=MenuAplicacao(self.aplicacao, app_status), embed=EmbedAplicacao(self.aplicacao, app_status))


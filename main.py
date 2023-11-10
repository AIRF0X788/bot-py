import discord
from discord.ext import commands
import json

intents = discord.Intents.all()

class CommandHistory:
    def __init__(self):
        self.history = {}

    def add_command(self, user_id, command):
        if user_id not in self.history:
            self.history[user_id] = [command]
        else:
            self.history[user_id].append(command)
        self.save_history()

    def get_lc(self, user_id):
        if user_id in self.history and self.history[user_id]:
            return self.history[user_id][-1]
        return "Aucune commande précédente pour cet utilisateur."

    def get_ac(self, user_id):
        if user_id in self.history and self.history[user_id]:
            return self.history[user_id]
        return "Aucune commande précédente pour cet utilisateur."

    def ch(self, user_id):
        if user_id in self.history:
            last_commands = self.history[user_id]
            self.history[user_id] = []
            self.save_history()
            return last_commands

    def save_history(self):
        with open("command_history.json", "w") as file:
            json.dump(self.history, file)

    def load_history(self):
        try:
            with open("command_history.json", "r") as file:
                self.history = json.load(file)
        except FileNotFoundError:
            self.history = {}

bot = commands.Bot(command_prefix='!', intents=intents)

history_manager = CommandHistory()
history_manager.load_history()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_command(ctx):
    if not ctx.author.bot:
        user_id = ctx.author.id
        command = ctx.message.content
        history_manager.add_command(user_id, command)

@bot.command()
async def lc(ctx):
    user_id = ctx.author.id
    lc = history_manager.get_lc(user_id)
    await ctx.send(f"Voici ta dernière commande utilisée : {lc}")

@bot.command()
async def ac(ctx):
    user_id = ctx.author.id
    ac = history_manager.get_ac(user_id)
    if isinstance(ac, list):
        await ctx.send(f"Voici l'historique de toutes tes commandes : {', '.join(ac)}")
    else:
        await ctx.send(ac)

@bot.command()
async def ch(ctx):
    user_id = ctx.author.id
    last_commands = history_manager.ch(user_id)
    if last_commands:
        await ctx.send("L'historique de l'utilisateur a été effacé.")
        with open("command_history.json", "r") as file:
            data = json.load(file)
            del data[str(user_id)]
        with open("command_history.json", "w") as file:
            json.dump(data, file)
    else:
        await ctx.send("Aucune commande précédente pour cet utilisateur.")


bot.run('MTE2NzM1OTk1MTg1ODA0OTA3NA.G2aXxo.rdwuUa0xkvwdD4Vbqua1_-bvcmOism-nubVp-A')

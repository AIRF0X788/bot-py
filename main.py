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

    def get_last_command(self, user_id):
        if user_id in self.history and self.history[user_id]:
            return self.history[user_id][-1]
        return "Aucune commande précédente pour cet utilisateur."

    def clear_history(self, user_id):
        if user_id in self.history:
            self.history[user_id] = []
            self.save_history()

    def save_history(self):
        with open("command_history.json", "w") as file:
            json.dump(self.history, file)

    def load_history(self):
        try:
            with open("command_history.json", "r") as file:
                self.history = json.load(file)
        except FileNotFoundError:
            self.history = {}

    def to_dict(self):
        return self.history

bot = commands.Bot(command_prefix='!', intents = intents)

history_manager = CommandHistory()
history_manager.load_history()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_command(ctx):
    if not ctx.author.bot:  # Vérifie que l'auteur de la commande n'est pas le bot lui-même
        user_id = ctx.author.id
        command = ctx.message.content
        history_manager.add_command(user_id, command)

@bot.command()
async def last_command(ctx):
    user_id = ctx.author.id
    last_command = history_manager.get_last_command(user_id)
    await ctx.send(f"Dernière commande de l'utilisateur : {last_command}")

@bot.command()
async def clear_history(ctx):
    user_id = ctx.author.id
    history_manager.clear_history(user_id)
    await ctx.send("L'historique de l'utilisateur a été effacé.")

@bot.command()
async def save_history(ctx):
    if ctx.author.id: 
        history_manager.save_history()
        await ctx.send("L'historique a été sauvegardé.")
    else:
        await ctx.send("Vous n'êtes pas autorisé à effectuer cette action.")

bot.run('MTE2NzM1OTk1MTg1ODA0OTA3NA.G2aXxo.rdwuUa0xkvwdD4Vbqua1_-bvcmOism-nubVp-A')

import discord
from discord.ext import commands
import json
import asyncio
import random
from random import shuffle
import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

class Node:
    def __init__(self, data):
        self.data = data
        self.next_node = None
        self.prev_node = None
        self.left = None
        self.right = None

class History:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.locked = False
        
    def lock(self):
        if not self.locked:
            self.locked = True
            return True
        return False
    
    def unlock(self):
        self.locked = False

    def command(self, command):
        if self.lock():
            try:
                new_node = Node(command)
                if not self.head:
                    self.head = new_node
                    self.tail = new_node
                    self.current = new_node
                else:
                    self.tail.next_node = new_node
                    new_node.prev_node = self.tail
                    self.tail = new_node
                    self.current = new_node
            finally:
                self.unlock()
        else:
            print("L'historique est actuellement verrouillé, veuillez réessayer ultérieurement.")

    def get_c(self, user_id):
        user_commands = []
        current_node = self.head
        while current_node:
            if current_node.data["user_id"] == user_id:
                user_commands.append(current_node.data["command"])
            current_node = current_node.next_node
        return user_commands

    def last_c(self):
        if self.tail:
            return self.tail.data
        else:
            return "Aucune commande pour le moment."

    def move_right(self):
        if self.current.next_node:
            self.current = self.current.next_node
            return self.current.data
        else:
            return "Aucune autre commande en avant."

    def move_left(self):
        if self.current.prev_node:
            self.current = self.current.prev_node
            return self.current.data
        else:
            return "Aucune autre commande en arrière."

    def clear_history(self):
        self.head = None
        self.tail = None
        self.current = None

    def serialize(self):
        serialized_commands = []
        current_node = self.head
        while current_node:
            serialized_commands.append(current_node.data)
            current_node = current_node.next_node
        return serialized_commands

history = {}

def save_json():
    serialized_history = {user_id: command_history.serialize() for user_id, command_history in history.items()}
    with open("history.json", "w") as file:
        json.dump(serialized_history, file, indent=4)

def load_json():
    try:
        with open("history.json", "r") as file:
            loaded_data = json.load(file)
            loaded_history = {}
            for user_id, commands_data in loaded_data.items():
                history = History()
                for command_data in commands_data:
                    history.command(command_data)
                loaded_history[int(user_id)] = history
            return loaded_history
    except FileNotFoundError:
        return {}

    
def pizza_questionnaire():
    root = Node("Pizza base tomate ?")
    root.left = Node("Végétarienne ?")
    root.left.left = Node("Artichaut ?")
    root.left.left.left = Node("Olive ?")
    root.left.left.right = Node("Olive ?")
    root.left.right = Node("Pepperoni ?")
    root.left.right.right = Node("Merguez ?")
    root.left.right.left = Node("Merguez ?")

    root.right = Node("Pizza base crème fraiche ?")
    root.right.left = Node("Végétarienne ?")
    root.right.left.left = Node("Artichaut ?")
    root.right.left.left.left = Node("Olive ?")
    root.right.left.left.right = Node("Olive ?")
    root.right.left.right = Node("Pepperoni ?")
    root.right.left.right.left = Node("Merguez ?")
    root.right.left.right.right = Node("Merguez ?")

    return root

pizza_tree = pizza_questionnaire()


def load_money():
    try:
        with open("money.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_money(data):
    with open("money.json", "w") as file:
        json.dump(data, file, indent=4)

money = load_money()


def create_deck():
    suits = ['♠️', '♥️', '♦️', '♣️']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [{'value': value, 'suit': suit} for suit in suits for value in values]
    shuffle(deck)
    return deck

deck = create_deck()

def hand_value(hand):
    total = 0
    num_aces = 0

    for card in hand:
        if card['value'].isdigit():
            total += int(card['value'])
        elif card['value'] in ['J', 'Q', 'K']:
            total += 10
        elif card['value'] == 'A':
            num_aces += 1
            total += 11

    while total > 21 and num_aces > 0:
        total -= 10
        num_aces -= 1

    return total

players = []
chamber = [False] * 6
bullet_found = False

game_in_progress = False
players = []
board = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
current_player = None

def display_board():
    return (
        f"```\n"
        f" {board[0]} | {board[1]} | {board[2]}\n"
        f"---|---|---\n"
        f" {board[3]} | {board[4]} | {board[5]}\n"
        f"---|---|---\n"
        f" {board[6]} | {board[7]} | {board[8]}\n"
        f"```"
    )

def check_winner():
    global game_in_progress  
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  
        (0, 3, 6), (1, 4, 7), (2, 5, 8), 
        (0, 4, 8), (2, 4, 6)            
    ]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]]:
            game_in_progress = False 
            return board[combo[0]]
    return None


work_info = {
    "Vous avez aidé à la caisse enregistreuse.": 20,
    "Vous avez fait du nettoyage.": 15,
    "Vous avez livré des colis.": 30,
    "Vous avez aidé à la préparation des repas.": 25,
    "Vous avez trié les documents.": 18,
    "Vous avez effectué des recherches.": 22,
    "Vous avez fait de la maintenance informatique.": 30,
    "Vous avez travaillé à l'accueil.": 28,
    "Vous avez aidé à organiser un événement.": 35,
    "Vous avez donné des cours particuliers.": 40,
    "Vous avez travaillé à l'entretien des jardins.": 20,
    "Vous avez fait de la comptabilité.": 33,
    "Vous avez préparé des rapports.": 27,
}

last_work_time = {}

def load_levels():
    try:
        with open("levels.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_levels(levels):
    with open("levels.json", "w") as file:
        json.dump(levels, file, indent=4)

@bot.event
async def on_ready():
    global history
    history = load_json()
    print(f"Connecté en tant que {bot.user.name}")



@bot.event 
async def on_command(ctx):
    user_id = ctx.author.id
    if user_id not in history:
        history[user_id] = History()
    command = ctx.message.content
    history[user_id].command({"user_id": user_id, "command": command})
    save_json()


##########Money##############
@bot.command(name="money")
async def check_money(ctx):
    user_id = str(ctx.author.id)
    if user_id in money:
        await ctx.send(f"Vous avez {money[user_id]}$.")
    else:
        await ctx.send("Vous n'avez pas encore d'argent.")
        

        
        
#######LEVELS######

levels = {
    "1 Novice": 150,
    "2 Débutant": 300,
    "3 Amateur": 600,
    "4 Intermédiaire": 1200,
    "5 Confirmé": 2400,
    "6 Expert": 4800,
    "7 Maître": 8000,
    "8 Champion": 15000,
    "9 Héros": 22000,
    "10 Légende": 30000,
}


@bot.command(name="buy_level")
async def buy_level(ctx, level_number: int):
    user_id = str(ctx.author.id)
    if user_id not in money:
        await ctx.send("Vous n'avez pas assez d'argent.")
        return
    
    levels = load_levels()
    
    current_level = levels.get(user_id, -0)
    
    if current_level != level_number - 1:
        await ctx.send("Vous ne pouvez acheter qu'un seul niveau à la fois.")
        return
    
    level_prices = [150, 300, 600, 1200, 2400, 4800, 8000, 15000, 22000, 30000]
    
    price = level_prices[current_level]
    if money[user_id] < price:
        await ctx.send("Vous n'avez pas assez d'argent pour acheter ce niveau.")
        return
    
    money[user_id] -= price
    levels[user_id] = current_level + 1 
    save_money(money)
    save_levels(levels)
    
    level_names = ["Sans niveau", "Novice", "Débutant", "Amateur", "Intermédiaire", "Confirmé", "Expert", "Maître", "Champion", "Héros", "Légende"]
    await ctx.send(f"Vous avez acheté avec succès le niveau {level_names[current_level + 1]}!")
    

@bot.command(name='all_levels')
async def all_levels(ctx):
    await ctx.send("Niveaux disponibles :")
    for level, price in levels.items():
        await ctx.send(f"{level}: {price} $")


@bot.command(name="my_level")
async def my_level(ctx):
    levels = load_levels()
    user_id = str(ctx.author.id)
    
    if user_id in levels:
        level = levels[user_id]
        level_names = ["Sans niveau", "Novice", "Débutant", "Amateur", "Intermédiaire", "Confirmé", "Expert", "Maître", "Champion", "Héros", "Légende"]
        current_level = level_names[level]
        
        level_messages = {
            "Sans niveau": "Vous n'avez pas de niveau",
            "Novice": "🌟 Vous êtes un Novice 🌟",
            "Débutant": "🔰 Vous êtes un Débutant 🔰",
            "Amateur": "🎯 Amateur, en route vers la gloire ! 🎯",
            "Intermédiaire": "🚀 Vous êtes désormais Intermédiaire 🚀",
            "Confirmé": "💡 Confirmé - La maîtrise approche 💡",
            "Expert": "⚔️ Vous êtes devenu un Expert ⚔️",
            "Maître": "👑 Maître, le sommet est à portée 👑",
            "Champion": "🏆 Vous êtes désormais un Champion 🏆",
            "Héros": "🌟 Héros - Légende en devenir 🌟",
            "Légende": "🌟🌟🌟 Vous êtes une Légende 🌟🌟🌟",
}

        
        if current_level in level_messages:
            await ctx.send(level_messages[current_level])
        else:
            await ctx.send(f"Votre niveau actuel : {current_level}")
    else:
        await ctx.send("Vous n'avez pas encore acheté de niveau.")



##########Argent début###############
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    if user_id not in money:
        money[user_id] = 100
        save_money(money)
        await message.channel.send(f"Bienvenue {message.author.mention} ! Vous avez reçu 100$ pour jouer au casino.")
    
    await bot.process_commands(message)

#############Work###############
@bot.command()
async def work(ctx):
    user_id = str(ctx.author.id)
    last_time = last_work_time.get(user_id)
    if last_time:
        time_diff = datetime.datetime.utcnow() - last_time
        if time_diff.total_seconds() < 600:
            remaining_time = 600 - time_diff.total_seconds()
            await ctx.send(f"Vous avez déjà travaillé récemment. Attendez encore {int(remaining_time // 60)} minutes.")
            return
    
    work_phrase, earned_amount = random.choice(list(work_info.items()))
    money[user_id] = money.get(user_id, 0) + earned_amount
    last_work_time[user_id] = datetime.datetime.utcnow()
    await ctx.send(f"{work_phrase} Vous avez travaillé et reçu votre salaire de {earned_amount}$ !")
    
    save_money(money)



######Slot############
@bot.command(name='spin')
async def slot(ctx, bet_amount: int = 0):
    if bet_amount <= 0:
        await ctx.send("Veuillez spécifier un montant à miser.")
        return
    
    user_id = str(ctx.author.id)
    if user_id not in money or money[user_id] < bet_amount:
        await ctx.send("Vous n'avez pas assez d'argent pour parier cette somme.")
        return

    money[user_id] -= bet_amount 

    symbols = ["🍒", "🍊", "🍋", "🍇", "🔔", "💎"]
    results = [random.choice(symbols) for _ in range(3)] 

    await ctx.send(f"Résultats : {' '.join(results)}")

    if results.count(results[0]) == 3:
        money[user_id] += bet_amount * 5
        await ctx.send(f"Bravo ! Vous avez gagné {bet_amount * 3}$.")
    elif results.count(results[0]) == 2 or results.count(results[1]) == 2:
        money[user_id] += bet_amount * 2.5
        await ctx.send(f"Vous avez deux symboles identiques ! Vous gagnez {bet_amount * 2}$.")
    else:
        await ctx.send("Désolé, aucun gain cette fois.")
    
    save_money(money)


###############Morpion###################

@bot.command(name='join_morpion')
async def join_morpion(ctx):
    global players, game_in_progress
    if game_in_progress:
        await ctx.send("Une partie est déjà en cours.")
        return
    
    if len(players) >= 2:
        await ctx.send("La partie est pleine.")
        return
    
    if ctx.author not in players:
        players.append(ctx.author)
        await ctx.send(f"{ctx.author.mention} a rejoint la partie de morpion !")
        
    if len(players) == 2:
        game_in_progress = True
        await ctx.send("La partie de morpion va commencer ! Utilisez !start_morpion pour démarrer.")

@bot.command(name='start_morpion')
async def start_morpion(ctx):
    global players, game_in_progress, current_player, board
    if not game_in_progress:
        await ctx.send("Il n'y a pas assez de joueurs pour démarrer la partie.")
        return
    
    if len(players) != 2:
        await ctx.send("La partie nécessite deux joueurs.")
        return
    
    board = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    current_player = players[0]
    
    await ctx.send(f"La partie de morpion démarre entre {players[0].mention} et {players[1].mention} !")
    await ctx.send(f"Utilise !play n (case de votre choix) pour jouer.")
    await ctx.send(display_board())
    await ctx.send(f"{current_player.mention}, c'est à votre tour.")

@bot.command(name='play')
async def play(ctx, position: int):
    global current_player, board, game_in_progress, players
    if ctx.author != current_player:
        await ctx.send("Ce n'est pas votre tour.")
        return
    
    if not 1 <= position <= 9 or board[position - 1] in ['X', 'O']:
        await ctx.send("Position invalide. Choisissez un nombre entre 1 et 9.")
        return
    
    marker = 'X' if current_player == players[0] else 'O'
    board[position - 1] = marker
    
    await ctx.send(display_board())
    
    winner = check_winner()
    if winner:
        await ctx.send(f"{winner} a gagné la partie !")
        game_in_progress = False
        players.clear()
        return
    
    if all(cell in ['X', 'O'] for cell in board):
        await ctx.send("Match nul !")
        game_in_progress = False
        players.clear()
        return
    
    current_player = players[1] if current_player == players[0] else players[0]
    await ctx.send(f"{current_player.mention}, c'est à votre tour.")


########Blackjack################

@bot.command(name="blackjack")
async def start_blackjack(ctx, bet_amount: int = 0):
    if bet_amount <= 0:
        await ctx.send("Veuillez spécifier un montant à miser.")
        return
    user_id = str(ctx.author.id)
    if user_id not in money or money[user_id] < bet_amount:
        await ctx.send("Vous n'avez pas assez d'argent pour parier.")
        return
    
    money[user_id] -= bet_amount
    save_money(money)
    
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    player_total = hand_value(player_hand)
    dealer_total = hand_value(dealer_hand)

    player_cards = [f"{card['value']}{card['suit']}" for card in player_hand]
    dealer_cards = [f"{dealer_hand[0]['value']}{dealer_hand[0]['suit']}", f"{dealer_hand[1]['value']}{dealer_hand[1]['suit']}"]
    
    player_message = await ctx.send(f"**Vos cartes :** {', '.join(player_cards)}\nTotal : {player_total}\n\n**Carte du croupier :** {dealer_cards[0]}")
    
    if player_total == 21:
        await ctx.send("Blackjack ! Vous avez gagné !")
        money[user_id] += bet_amount * 2
        save_money(money)
        return

    await player_message.add_reaction('👊')
    await player_message.add_reaction('✋')

    def check_reaction(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['👊', '✋'] and reaction.message.id == player_message.id

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)

            if str(reaction.emoji) == '👊':
                player_hand.append(deck.pop())
                player_total = hand_value(player_hand)
                player_cards.append(f"{player_hand[-1]['value']}{player_hand[-1]['suit']}")
                await player_message.edit(content=f"**Vos cartes :** {', '.join(player_cards)}\nTotal : {player_total}\n\n**Carte du croupier :** {dealer_cards[0]}")

                if player_total > 21:
                    await ctx.send("Buste ! Vous avez perdu.")
                    return

            elif str(reaction.emoji) == '✋':
                break

        except asyncio.TimeoutError:
            await ctx.send("Temps écoulé. Partie terminée.")
            return

    while dealer_total < 17:
        dealer_hand.append(deck.pop())
        dealer_total = hand_value(dealer_hand)
        dealer_cards.append(f"{dealer_hand[-1]['value']}{dealer_hand[-1]['suit']}")

    await player_message.edit(content=f"**Vos cartes :** {', '.join(player_cards)}\nTotal : {player_total}\n\n**Cartes du croupier :** {', '.join(dealer_cards)}\nTotal : {dealer_total}")

    if dealer_total > 21 or player_total > dealer_total:
        await ctx.send(f"Vous avez gagné {bet_amount * 2}$ !")
        money[user_id] += bet_amount * 2
    elif player_total == dealer_total:
        await ctx.send("Égalité. Vous récupérez votre mise.")
        money[user_id] += bet_amount
    else:
        await ctx.send(f"Vous avez perdu {bet_amount}$.")

    save_money(money)

    
    
#######Roulette russe ################

@bot.command(name='join_russian')
async def join_russian(ctx):
    if ctx.author not in players:
        players.append(ctx.author)
        await ctx.send(f"{ctx.author.mention} a rejoint la partie !\n**Joueurs actuels**:\n" + ', '.join([player.display_name for player in players]))

@bot.command(name='start_russian')
async def start_russian(ctx):
    global chamber, bullet_found
    if len(players) < 2:
        await ctx.send("Pas assez de joueurs pour démarrer le jeu !")
    else:
        await ctx.send("**Le jeu va commencer...**")
        chamber = [False] * 6  
        bullet_found = False
        await load_gun(ctx)

async def load_gun(ctx):
    global chamber, bullet_found
    chamber[random.randint(0, 5)] = True  
    await asyncio.sleep(2)
    await ctx.send("**Le pistolet est chargé...**")
    await asyncio.sleep(2)
    await ctx.send("**Le barillet tourne...**")
    await asyncio.sleep(2)
    await ctx.send("**La partie commence !**")
    await play_game(ctx)

async def play_game(ctx):
    global players, chamber, bullet_found
    random.shuffle(players)
    while not bullet_found:
        for player in players:
            await asyncio.sleep(2)
            await ctx.send(f":gun: {player.display_name} prend le pistolet...")
            await asyncio.sleep(2)
            shot = chamber.pop(0)
            if shot:
                await ctx.send(f":boom: {player.display_name} a été touché !")
                players.remove(player)
                if len(players) == 1:
                    await ctx.send(f":tada: **{players[0].display_name} remporte la partie !**")
                    players = []  
                    bullet_found = True
                    return
                bullet_found = True
                break
            else:
                chamber.append(False)
                await ctx.send(f":dash: Rien ne se passe pour {player.display_name}...")
        if not bullet_found:
            await ctx.send("**Aucune balle n'a été tirée. La partie continue...**")


########Arbre binaire###############        
        
async def initiate_conversation(ctx):
    message = await ctx.send("Bonjour ! Voulez-vous commencer à personnaliser votre pizza ?")

    reactions = ['✅']
    for reaction in reactions:
        await message.add_reaction(reaction)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in reactions

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

        if str(reaction.emoji) == '✅':
            await ctx.send("Parfait ! Commençons")

            await pose_question(ctx, pizza_tree)

    except asyncio.TimeoutError:
        await ctx.send("Temps écoulé")

async def pose_question(ctx, node):
    if node:
        message = await ctx.send(node.data)

        reactions = ['⭕', '❌']
        for reaction in reactions:
            await message.add_reaction(reaction) 
            await asyncio.sleep(0.1)

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in reactions

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check_reaction)

            if str(reaction.emoji) == '⭕':
                await pose_question(ctx, node.left)
            elif str(reaction.emoji) == '❌':
                await pose_question(ctx, node.right)

        except asyncio.TimeoutError:
            await ctx.send("Temps écoulé pour cette question")

    else:
        await ctx.send("Merci d'avoir répondu !")


@bot.command(name="talk")
async def start_conversation(ctx):
    await initiate_conversation(ctx)


#####Historique#########

@bot.command(name="lc")
async def last_command(ctx):
    user_id = ctx.author.id
    if user_id in history:
        last = history[user_id].last_c()
        await ctx.send(f"Dernière commande: {last}")
    else:
        await ctx.send("Aucune commande pour le moment")
        
        

@bot.command(name="uc")
async def user_commands(ctx):
    user_id = ctx.author.id
    if user_id in history:
        user_commands = history[user_id].get_c(user_id)
        if user_commands:
            pages = []
            commands_per_page = 5
            for i in range(0, len(user_commands), commands_per_page):
                page_commands = user_commands[i:i + commands_per_page]
                message = "\n".join(page_commands)
                embed = discord.Embed(title="Historique de vos commandes", description=message)
                pages.append(embed)

            current_page = 0
            msg = await ctx.send(embed=pages[current_page])

            reactions = ['⏪', '◀️', '▶️', '⏩']

            for reaction in reactions:
                await msg.add_reaction(reaction)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in reactions

            while True:
                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                    if str(reaction.emoji) == '⏪':
                        current_page = 0
                        await msg.edit(embed=pages[current_page])

                    elif str(reaction.emoji) == '◀️':
                        if current_page > 0:
                            current_page -= 1
                            await msg.edit(embed=pages[current_page])

                    elif str(reaction.emoji) == '▶️':
                        if current_page < len(pages) - 1:
                            current_page += 1
                            await msg.edit(embed=pages[current_page])

                    elif str(reaction.emoji) == '⏩':
                        current_page = len(pages) - 1
                        await msg.edit(embed=pages[current_page])

                    await msg.remove_reaction(reaction, user)

                except asyncio.TimeoutError:
                    break
        else:
            await ctx.send("Aucune commande pour le moment")

@bot.command(name="ch")
async def clear_history(ctx):
    user_id = ctx.author.id
    if user_id in history:
        history[user_id] = History()
        save_json()
        await ctx.send("History vidé")
    else:
        await ctx.send("Aucune commande pour le moment")


bot.run('DISCORD_TOKEN')

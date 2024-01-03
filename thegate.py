###############################################################################
#                           Imports & Base Setup                              #
###############################################################################
import discord
from discord.ext import commands
import random
import asyncio
import logging
import time
import datetime
import json

logging.basicConfig(level=logging.DEBUG)

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

###############################################################################
#                          Variables, dicts, lists                            #
###############################################################################

# Add a blacklist list
blacklist = []
owner_id = "524395497015419457"

VOICE_REWARDS = {
    'normal': 20,
    'normal_muted': 14,
    'normal_deafened': 5,
    'streaming': 28,
    'streaming_muted': 22,
    'streaming_deafened': 18,
    'video': 30,
    'video_muted': 24,
    'video_deafened': 20,
    'video_streaming': 36,
    'video_streaming_muted': 26,
    'video_streaming_deafened': 24,
}


@bot.event
async def on_ready():
    print(f'{bot.user.name} is connected.')
    bot.loop.create_task(update_balance())
    bot.loop.create_task(voice_rewards())
    bot.loop.create_task(update_event_status())


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Cooldown! Please wait {error.retry_after:.2f} seconds.")
    else:
        raise error
###############################################################################
#                                  Report                                     #
###############################################################################


@bot.command()
async def report(ctx, reported_user_id: int, reason: str):
    server = bot.get_guild(820981976428445726)  # ID of my old discord server
    report_channel = server.get_channel(988826691541549186)  # ID of the report channel on that server

    embed = discord.Embed(title=f"{ctx.author.id} reports → {reported_user_id}",
                          description=reason,
                          color=discord.Color.red())

    await report_channel.send(embed=embed)

###############################################################################
#                                  events                                     #
###############################################################################

events = {}  # Store events with event_id as key
reputation = {}  # Store server reputation with server_id as key


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command()
async def event(ctx, action, *args):
    if action == "create":
        await create_event(ctx, *args)
    elif action == "list":
        await list_events(ctx)
    elif action == "delete":
        await delete_event(ctx, *args)
    else:
        await ctx.send("Invalid action. Use 'create', 'list', or 'delete'.")


async def create_event(ctx, name, time, duration, rewards, server):
    if not server.isdigit():
        await ctx.send("Invalid server id. Please make sure !create is on the form : !create 'name_of_event' 'time_of_the_event' 'duration_of_the_event' 'rewards_of_the_event' 'the_id_of_the server_that_organizes_ the_event'.")
        pass
    event_id = random.randint(1000, 9999)
    while event_id in events:
        event_id = random.randint(1000, 9999)

    # Convert 'time' string into a timestamp
    event_time = datetime.datetime.strptime(time, "%H:%M")
    today = datetime.datetime.now()
    event_time = event_time.replace(year=today.year, month=today.month, day=today.day)

    events[event_id] = {
        "creator": ctx.author.id,
        "name": name,
        "time": event_time,
        "duration": duration,
        "rewards": rewards,
        "server": server,
        "participants": [],
        "status": "Upcoming"
    }

    await ctx.send(f"Event created with ID: {event_id}")


async def update_event_status():
    while True:
        current_time = datetime.datetime.now()
        for event_id, event in events.copy().items():
            event_time = event['time']
            event_duration = datetime.timedelta(minutes=int(event['duration']))
            if current_time >= event_time and current_time <= event_time + event_duration:
                events[event_id]['status'] = "Started"
            elif current_time > event_time + event_duration:
                del events[event_id]
        await asyncio.sleep(10)  # Check every 10 seconds


async def list_events(ctx):
    if not events:
        await ctx.send("No events found.")
        return

    embed = discord.Embed(title="Current events", color=discord.Color.blue())
    for event_id, event in events.items():
        embed.add_field(name=f"ID: {event_id} | Name: {event['name']} | Status: {event['status']}",
                        value=f"Time: {event['time']} | Duration: {event['duration']}min | "
                              f"Rewards: {event['rewards']} | Server: {event['server']}",
                        inline=False)

    await ctx.send(embed=embed)


async def delete_event(ctx, event_id: int):
    if event_id not in events:
        await ctx.send("Event not found.")
        return

    if ctx.author.id != events[event_id]["creator"]:
        await ctx.send("You are not the creator of this event.")
        return

    del events[event_id]
    await ctx.send(f"Event with ID {event_id} deleted.")


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command()
async def join(ctx, event_id: int):
    if event_id not in events:
        await ctx.send("Event not found.")
        return

    if ctx.author.id in events[event_id]["participants"]:
        await ctx.send("You have already joined this event.")
        return

    events[event_id]["participants"].append(ctx.author.id)
    server_id = int(events[event_id]["server"])
    reputation[server_id] = reputation.get(server_id, 0) + 1

    participants_str = ', '.join(str(participant_id) for participant_id in events[event_id]["participants"])
    await ctx.send(f"Successfully joined event with ID {event_id}, participants: {participants_str}")


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command()
async def rep(ctx, server_id: int):
    server_rep = reputation.get(server_id, 0)
    await ctx.send(f"Server {server_id} - reputation: {server_rep}")

###############################################################################
#                                 Factions                                    #
###############################################################################


def save_factions(factions):
    with open('factions.json', 'w') as f:
        json.dump(factions, f)


def load_factions():
    try:
        with open('factions.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


@bot.command()
async def createfaction(ctx, faction_name: str):
    factions = load_factions()
    if faction_name in factions:
        await ctx.send(f"Faction '{faction_name}' already exists.")
        return
    factions[faction_name] = {'members': [ctx.author.id], 'leader': ctx.author.id}
    save_factions(factions)
    await ctx.send(f"Faction '{faction_name}' created.")


@bot.command()
async def joinfaction(ctx, faction_name: str):
    factions = load_factions()
    if faction_name not in factions:
        await ctx.send(f"Faction '{faction_name}' does not exist.")
        return
    for faction in factions.values():
        if ctx.author.id in faction['members']:
            await ctx.send("You are already in a faction.")
            return
    factions[faction_name]['members'].append(ctx.author.id)
    save_factions(factions)
    await ctx.send(f"Joined faction '{faction_name}'.")


@bot.command()
async def leavefaction(ctx):
    factions = load_factions()
    for faction_name, faction in factions.items():
        if ctx.author.id in faction['members']:
            faction['members'].remove(ctx.author.id)
            if ctx.author.id == faction['leader']:
                if faction['members']:
                    faction['leader'] = random.choice(faction['members'])
                else:
                    del factions[faction_name]
            save_factions(factions)
            await ctx.send(f"Left faction '{faction_name}'.")
            return
    await ctx.send("You are not in a faction.")


@bot.command()
async def factioninfo(ctx, faction_name: str):
    factions = load_factions()
    if faction_name not in factions:
        await ctx.send(f"Faction '{faction_name}' does not exist.")
        return
    faction = factions[faction_name]
    leader = await bot.fetch_user(faction['leader'])
    member_names = [str(await bot.fetch_user(member_id)) for member_id in faction['members']]
    await ctx.send(f"Faction '{faction_name}':\nLeader: {leader}\nMembers: {', '.join(member_names)}")


@bot.command()
async def factionleaderboard(ctx):
    factions = load_factions()
    sorted_factions = sorted(factions.items(), key=lambda x: len(x[1]['members']), reverse=True)
    leaderboard = [f"{i+1}. {faction_name} ({len(faction['members'])} members)" for i, (faction_name, faction) in enumerate(sorted_factions)]
    await ctx.send("Faction Leaderboard:\n" + "\n".join(leaderboard))


@bot.command()
async def factioninvite(ctx, user: discord.Member):
    factions = load_factions()
    for faction_name, faction in factions.items():
        if ctx.author.id == faction['leader']:
            await user.send(f"You have been invited to join faction '{faction_name}' by {ctx.author}. Type!acceptinvite {faction_name}` to join.")
            await ctx.send(f"Invitation sent to {user}.")
            return
    await ctx.send("You are not a faction leader.")


@bot.command()
async def acceptinvite(ctx, faction_name: str):
    factions = load_factions()
    if faction_name not in factions:
        await ctx.send(f"Faction '{faction_name}' does not exist.")
        return
    factions[faction_name]['members'].append(ctx.author.id)
    save_factions(factions)
    await ctx.send(f"Joined faction '{faction_name}'.")


@bot.command()
async def factionkick(ctx, user: discord.Member):
    factions = load_factions()
    for faction_name, faction in factions.items():
        if ctx.author.id == faction['leader']:
            if user.id in faction['members']:
                faction['members'].remove(user.id)
                save_factions(factions)
                await ctx.send(f"{user} has been kicked from faction '{faction_name}'.")
                return
            else:
                await ctx.send(f"{user} is not a member of your faction.")
                return
    await ctx.send("You are not a faction leader.")


@bot.command()
async def factionmessage(ctx, *, message: str):
    factions = load_factions()
    for faction_name, faction in factions.items():
        if ctx.author.id in faction['members']:
            for member_id in faction['members']:
                member = await bot.fetch_user(member_id)
                await member.send(f"Faction '{faction_name}' message from {ctx.author}: {message}")
            await ctx.send("Message sent to all faction members.")
            return
    await ctx.send("You are not in a faction.")


@bot.command()
async def factionrename(ctx, new_name: str):
    factions = load_factions()
    for faction_name, faction in factions.items():
        if ctx.author.id == faction['leader']:
            if new_name not in factions:
                factions[new_name] = factions.pop(faction_name)
                save_factions(factions)
                await ctx.send(f"Faction '{faction_name}' has been renamed to '{new_name}'.")
                return
            else:
                await ctx.send(f"Faction '{new_name}' already exists.")
                return
    await ctx.send("You are not a faction leader.")


@bot.command()
async def factionwar(ctx, target_faction: str):
    factions = load_factions()
    user_faction = get_user_faction(ctx.author.id, factions)
    if not user_faction:
        await ctx.send("You are not in a faction.")
        return
    if target_faction not in factions:
        await ctx.send(f"Faction '{target_faction}' does not exist.")
        return
    if user_faction == target_faction:
        await ctx.send("You cannot declare war on your own faction.")
        return
    print("War declared")  # todo : complete "factionwar" function
    await ctx.send(f"Faction '{user_faction}' has declared war on faction '{target_faction}'.")


@bot.command()
async def factionquest(ctx):
    factions = load_factions()
    user_faction = get_user_faction(ctx.author.id, factions)
    if not user_faction:
        await ctx.send("You are not in a faction.")
        return
    print("Quest launched")  # todo : complete "factionquest" function
    await ctx.send(f"A new quest has been assigned to faction '{user_faction}'.")


@bot.command()
async def factiontrade(ctx, target_faction: str, offer: str):
    factions = load_factions()
    user_faction = get_user_faction(ctx.author.id, factions)
    if not user_faction:
        await ctx.send("You are not in a faction.")
        return
    if target_faction not in factions:
        await ctx.send(f"Faction '{target_faction}' does not exist.")
        return
    if user_faction == target_faction:
        await ctx.send("You cannot trade with your own faction.")
        return
    print("Trade initiation")  # todo : complete "factiontrade" function
    await ctx.send(f"Faction '{user_faction}' has proposed a trade with faction '{target_faction}': {offer}.")


@bot.command()
async def factionalliance(ctx, target_faction: str):
    factions = load_factions()
    user_faction = get_user_faction(ctx.author.id, factions)
    if not user_faction:
        await ctx.send("You are not in a faction.")
        return
    if target_faction not in factions:
        await ctx.send(f"Faction '{target_faction}' does not exist.")
        return
    if user_faction == target_faction:
        await ctx.send("You cannot form an alliance with your own faction.")
        return
    print("Alliance proposal")  # todo : complete "factionalliance" function
    await ctx.send(f"Faction '{user_faction}' has sent an alliance request to faction '{target_faction}'.")


@bot.command()
async def factionranking(ctx, sort_by: str = 'members'):
    factions = load_factions()
    if sort_by == 'members':
        sorted_factions = sorted(factions.items(), key=lambda x: len(x[1]['members']), reverse=True)
        # todo : add more sorts
    else:
        await ctx.send("Invalid sorting parameter.")
        return
    leaderboard = [f"{i+1}. {faction_name} ({len(faction['members'])} members)" for i, (faction_name, faction) in enumerate(sorted_factions)]
    await ctx.send("Faction Leaderboard:\n" + "\n".join(leaderboard))


@bot.command()
async def factionpromote(ctx, member: discord.Member):
    factions = load_factions()
    user_faction = get_user_faction(ctx.author.id, factions)
    if user_faction and factions[user_faction]['leader'] == ctx.author.id:
        factions[user_faction]['members'].remove(member.id)
        factions[user_faction]['commanders'].append(member.id)
        save_factions(factions)
        await ctx.send(f"Promoted {member} in faction '{user_faction}'.")
    else:
        await ctx.send("You are not the leader of a faction.")


@bot.command()
async def factiondemote(ctx, member: discord.Member):
    factions = load_factions()
    user_faction = get_user_faction(ctx.author.id, factions)
    if user_faction and factions[user_faction]['leader'] == ctx.author.id:
        factions[user_faction]['commanders'].remove(member.id)
        factions[user_faction]['members'].append(member.id)
        save_factions(factions)
        await ctx.send(f"Demoted {member} in faction '{user_faction}'.")
    else:
        await ctx.send("You are not the leader of a faction.")


@bot.command()
async def factiondisband(ctx):
    factions = load_factions()
    user_faction = get_user_faction(ctx.author.id, factions)
    if user_faction and factions[user_faction]['leader'] == ctx.author.id:
        del factions[user_faction]
        save_factions(factions)
        await ctx.send(f"Faction '{user_faction}' disbanded.")
    else:
        await ctx.send("You are not the leader of a faction.")


@bot.command()
async def factiontransfer(ctx, new_leader: discord.Member):
    factions = load_factions()
    user_faction = get_user_faction(ctx.author.id, factions)
    if user_faction and factions[user_faction]['leader'] == ctx.author.id:
        factions[user_faction]['leader'] = new_leader.id
        save_factions(factions)
        await ctx.send(f"Transferred faction leadership to {new_leader}.")
    else:
        await ctx.send("You are not the leader of a faction.")


@bot.command()
async def factionmembers(ctx):
    factions = load_factions()
    user_faction = get_user_faction(ctx.author.id, factions)
    if user_faction:
        member_names = [str(await bot.fetch_user(member_id)) for member_id in factions[user_faction]['members']]
        await ctx.send(f"Members of faction '{user_faction}':\n{', '.join(member_names)}")
    else:
        await ctx.send("You are not in a faction.")


# Helper function to get the user's faction
def get_user_faction(user_id, factions):
    for faction_name, faction in factions.items():
        if user_id in faction['members']:
            return faction_name
    return None
###############################################################################
#                                 Economie                                    #
###############################################################################


def economie_data():
    with open('eco_data.txt', 'w') as eco_data:
        json.dump(economy, eco_data)


def read_economie_data():
    try:
        with open('eco_data.txt', 'r') as eco_data:
            return json.load(eco_data)
    except FileNotFoundError:
        return {}


def check_user():
    # test if the user is registered (in the economy) & not blacklisted to remove repetitive checks from all economy functions.
    pass


def get_voice_state(member):
    if member.voice.self_stream and member.voice.self_video:
        state = 'video_streaming'
    elif member.voice.self_video:
        state = 'video'
    elif member.voice.self_stream:
        state = 'streaming'
    else:
        state = 'normal'

    if member.voice.self_deaf:
        state += '_deafened'
    else:
        if member.voice.self_mute:
            state += '_muted'

    return state


economy_data = read_economie_data()

economy = economy_data


async def update_balance():
    while True:
        for user_id, user_data in economy.items():
            mines = user_data.get('mines', 0)
            wagons = user_data.get('wagons', 0)
            user_data['balance'] += 30 * mines + 5 * wagons
            economie_data()
        await asyncio.sleep(3600)


async def voice_rewards():
    while True:
        for guild in bot.guilds:
            if guild.id == 820981976428445726:  # This was the ID of my old discord server if I remember well
                for member in guild.members:
                    if member.voice is not None and not member.voice.afk:
                        user_id = str(member.id)
                        if user_id in economy and user_id not in blacklist:
                            voice_state = get_voice_state(member)
                            economy[user_id]['balance'] += VOICE_REWARDS[voice_state]
                            print(time.strftime("%H:%M:%S") + " : Economy logs : Voice log: id(" + user_id + ") - Status = (" + voice_state + ") => " + str(VOICE_REWARDS[voice_state]) + "keys")
                            economie_data()
            await asyncio.sleep(300)


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='register')
async def register(ctx):
    user_id = str(ctx.author.id)
    if user_id in blacklist:
        await ctx.send(f"{ctx.author.mention}, you are on the blacklist and cannot use economy commands.")
    elif user_id not in economy:
        economy[user_id] = {'balance': 100, 'wagons': 0, 'mines': 0}  # Initialize 'wagons' and 'mines' keys
        economie_data()
        await ctx.send(f"{ctx.author.mention}, you are now registered and got 100 coins.")
    else:
        await ctx.send(f"{ctx.author.mention}, you are already registered.")


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='balance')
async def balance(ctx):
    user_id = str(ctx.author.id)
    if user_id in economy:
        await ctx.send(f"{ctx.author.mention}, your balance is {economy[user_id]['balance']} coins.")
    else:
        await ctx.send(f"{ctx.author.mention}, you are not registered. Use '!register' to register.")


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='give')
async def give(ctx, member: discord.Member, amount: int):
    sender_id = str(ctx.author.id)
    receiver_id = str(member.id)

    if sender_id not in economy or receiver_id not in economy:
        await ctx.send("Both members must be registered to make a transfer.")
    elif economy[sender_id]['balance'] < amount:
        await ctx.send("You don't have enough coins to make this transfer.")
    else:
        economy[sender_id]['balance'] -= amount
        economy[receiver_id]['balance'] += amount
        economie_data()
        await ctx.send(f"{ctx.author.mention} gave {amount} coins to {member.mention}.")


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='daily')
async def daily(ctx):
    user_id = str(ctx.author.id)
    if user_id in economy:
        daily = random.randint(100, 20000)
        economy[user_id]['balance'] += daily
        economie_data()
        await ctx.send(f"{ctx.author.mention}, you have received {daily} coins. Your balance is now {economy[user_id]['balance']} coins.")
    else:
        await ctx.send(f"{ctx.author.mention}, you are not registered. Use '!register' to register.")


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='shop')
async def shop(ctx):
    shop_items = {
        'wagon': {'price': 1850},
        'mine': {'price': 10000}
    }
    message = "Here are the items available in the shop:\n"
    for item, info in shop_items.items():
        message += f"{item.capitalize()} - Price : {info['price']} coins\n"
    await ctx.send(message)


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='buy')
async def buy(ctx, item: str, quantity: int = 1):
    user_id = str(ctx.author.id)
    shop_items = {
        'wagon': {'price': 1850},
        'mine': {'price': 10000}
    }

    if item.lower() in shop_items:
        cost = shop_items[item.lower()]['price'] * quantity

        if user_id in economy and economy[user_id]['balance'] >= cost:
            if item.lower() == 'mine' and (economy[user_id]['mines'] + quantity) > 3:
                await ctx.send(f"{ctx.author.mention}, you can only own a maximum of 3 mines.")
                return

            if item.lower() == 'wagon' and (economy[user_id]['wagons'] + quantity) > (10 * economy[user_id]['mines']):
                await ctx.send(f"{ctx.author.mention}, you can only own {10 * economy[user_id]['mines']} wagons.")
                return

            economy[user_id]['balance'] -= cost
            economy[user_id][item.lower() + 's'] += quantity
            economie_data()
            await ctx.send(
                f"{ctx.author.mention}, you just buy {quantity} {item} for {cost} coins. Your balance is now {economy[user_id]['balance']} coins.")
        else:
            await ctx.send(f"{ctx.author.mention}, you don't have enough coins to buy {quantity} {item}.")
    else:
        await ctx.send(f"{ctx.author.mention}, this item is not available in the shop.")


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='withdraw')
async def withdraw(ctx, amount: int):
    user_id = str(ctx.author.id)
    if user_id in economy:
        if economy[user_id]['balance'] >= amount:
            economy[user_id]['balance'] -= amount
            economie_data()
            await ctx.send(f"{ctx.author.mention}, you have withdrawn {amount} coins. Your balance is now {economy[user_id]['balance']} coins.")
        else:
            await ctx.send(f"{ctx.author.mention}, you do not have enough coins to withdraw {amount} coins.")
    else:
        await ctx.send(f"{ctx.author.mention}, you are not registered. Use '!register' to register.")


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='deposit')
async def deposit(ctx, amount: int):
    user_id = str(ctx.author.id)
    if user_id in economy:
        economy[user_id]['balance'] += amount
        economie_data()
        await ctx.send(f"{ctx.author.mention}, you have deposited {amount} coins. Your balance is now {economy[user_id]['balance']} coins.")
    else:
        await ctx.send(f"{ctx.author.mention}, you are not registered. Use '!register' to register.")


@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='casino')
async def casino(ctx, game: str, bet: int):
    user_id = str(ctx.author.id)
    if user_id in blacklist:
        await ctx.send(f"{ctx.author.mention}, you are blacklisted and cannot use economy orders.")
        return

    if user_id not in economy:
        await ctx.send(f"{ctx.author.mention}, you must register before playing. Use '!register' to register.")
        return

    if bet <= 0 or bet > economy[user_id]['balance']:
        await ctx.send(f"{ctx.author.mention}, you must bet a valid amount.")
        return

    if game.lower() == 'guess':
        await play_guessing_game(ctx, user_id, bet)
    elif game.lower() == 'highlow':
        await play_highlow_game(ctx, user_id, bet)
    elif game.lower() == 'slot':
        await slots(ctx, user_id, bet)
    elif game.lower() == 'emoji_match':
        await play_emoji_match(ctx, user_id, bet)
    elif game.lower() == 'memory':
        await play_memory_game(ctx, user_id, bet)
    elif game.lower() == 'treasure':
        await play_treasure_hunt(ctx, user_id, bet)
    elif game.lower() == 'odd_even':
        await play_odd_or_even(ctx, user_id, bet)
    else:
        await ctx.send(f"{ctx.author.mention}, this game is not available. Try 'guess', 'highlow', 'slot', 'emoji_match', 'memory', 'treasure' or 'odd_even'.")


async def play_highlow_game(ctx, user_id, bet):
    points = 0
    for i in range(3):
        current_number = random.randint(1, 10)
        await ctx.send(f"{ctx.author.mention}, the current number is {current_number}. Guess whether the next number will be higher (+) or lower (-).")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ['+', '-']

        try:
            guess_msg = await bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, you have taken too long to reply. The game is cancelled.")
            return

        guess = guess_msg.content.lower()
        next_number = random.randint(1, 10)

        while next_number == current_number:
            next_number = random.randint(1, 10)

        if (guess == '+' and next_number > current_number) or (guess == '-' and next_number < current_number):
            await ctx.send(f"{ctx.author.mention}, correct. The next number was {next_number}")
            points += 1
            if points == 3:
                economy[user_id]['balance'] += bet
                await ctx.send(f"{ctx.author.mention}, you've won! You found the numbers that followed three times in a row. You now have {economy[user_id]['balance']} coins.")
                break
        else:
            economy[user_id]['balance'] -= bet
            economie_data()
            await ctx.send(f"{ctx.author.mention}, you lost. The next number was {next_number}. You now have {economy[user_id]['balance']} coins.")
            break


async def play_guessing_game(ctx, user_id, bet):
    secret_number = random.randint(1, 10)
    await ctx.send(f"{ctx.author.mention}, guess a number between 1 and 10. You have 3 tries.")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.isdigit()

    for attempt in range(3):
        try:
            guess_msg = await bot.wait_for('message', check=check, timeout=10)
            guess = int(guess_msg.content)

            if guess == secret_number:
                economy[user_id]['balance'] += bet
                economie_data()
                await ctx.send(f"{ctx.author.mention}, Congratulations! You've won {bet} coins.")
                break
            elif attempt < 2:
                await ctx.send(f"{ctx.author.mention}, wrong answer. Try again.")
            else:
                economy[user_id]['balance'] -= bet
                economie_data()
                await ctx.send(f"{ctx.author.mention}, you lost. The number was {secret_number}. You have lost {bet} coins.")
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, elapsed time. You have lost {bet} coins.")
            economy[user_id]['balance'] -= bet
            economie_data()
            break


async def slots(ctx, user_id, bet):
    if user_id in blacklist:
        await ctx.send(f"{ctx.author.mention}, you are blacklisted and cannot use economic commands.")
        return

    if user_id not in economy:
        await ctx.send(f"{ctx.author.mention}, you need to register before playing.")
        return

    if bet <= 0 or bet > economy[user_id]['balance']:
        await ctx.send(f"{ctx.author.mention}, you need to bet a valid amount.")
        return

    symbols = ['cherry', 'lemon', 'orange', 'plum', 'bell', 'bar', 'seven']
    reels = [random.choice(symbols) for i in range(3)]
    if reels.count(reels[0]) == 3:
        payout = bet * 10
    elif reels.count(reels[0]) == 2:
        payout = bet * 2
    else:
        payout = -bet

    economy[user_id]['balance'] += payout
    economie_data()
    await ctx.send(f"{ctx.author.mention}, slot machine choices are {', '.join(reels)}.\n{payout:+} coins.")


async def play_emoji_match(ctx, user_id, bet):
    emojis = ['🍎', '🍊', '🍇', '🍓', '🍒']
    chosen_emojis = random.choices(emojis, k=3)
    if len(set(chosen_emojis)) == 1:
        rdm = random.randint(18, 23)
        economy[user_id]['balance'] += bet * rdm
        economie_data()
        await ctx.send(f"{ctx.author.mention}, you won! You matched 3 {chosen_emojis[0]} and won {bet * rdm} coins.")
    else:
        economy[user_id]['balance'] -= bet
        economie_data()
        await ctx.send(f"{ctx.author.mention}, you lost. The emojis were {' '.join(chosen_emojis)}. You lost {bet} coins.")


async def play_treasure_hunt(ctx, user_id, bet):
    treasure = random.randint(1, 3)
    await ctx.send(f"{ctx.author.mention}, choose a chest (1, 2, or 3). One of them contains a treasure!")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.isdigit() and int(msg.content) in [1, 2, 3]

    try:
        guess_msg = await bot.wait_for('message', check=check, timeout=10)
        guess = int(guess_msg.content)
        if guess == treasure:
            rdm = random.randint(1, 2)
            economy[user_id]['balance'] += bet * rdm
            economie_data()
            await ctx.send(f"{ctx.author.mention}, congratulations! You found the treasure and won {bet * rdm} coins.")
        else:
            economy[user_id]['balance'] -= bet
            economie_data()
            await ctx.send(f"{ctx.author.mention}, you lost. The treasure was in chest {treasure}. You lost {bet} coins.")
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, time's up. You lost {bet} coins.")
        economy[user_id]['balance'] -= bet
        economie_data()


async def play_odd_or_even(ctx, user_id, bet):
    await ctx.send(f"{ctx.author.mention}, guess if the next number (1-10) will be odd or even.")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ['odd', 'even']

    try:
        guess_msg = await bot.wait_for('message', check=check, timeout=10)
        guess = guess_msg.content.lower()
        number = random.randint(1, 10)
        if (number % 2 == 0 and guess == 'even') or (number % 2 != 0 and guess == 'odd'):
            economy[user_id]['balance'] += bet
            economie_data()
            await ctx.send(f"{ctx.author.mention}, you won! The number was {number}. You won {bet} coins.")
        else:
            economy[user_id]['balance'] -= bet
            economie_data()
            await ctx.send(f"{ctx.author.mention}, you lost. The number was {number}. You lost {bet} coins.")
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, time's up. You lost {bet} coins.")
        economy[user_id]['balance'] -= bet
        economie_data()


async def play_memory_game(ctx, user_id, bet):
    emojis = ['🍎', '🍊', '🍇', '🍓', '🍒']
    chosen_emojis = random.choices(emojis, k=2)
    await ctx.send(f"{ctx.author.mention}, memorize the emojis: {' '.join(chosen_emojis)}")

    await asyncio.sleep(5)

    await ctx.send(f"{ctx.author.mention}, now type the emojis in the order they appeared.")

    def check(msg):
      return msg.author == ctx.author and msg.channel == ctx.channel

    try:
      guess_msg = await bot.wait_for('message', check=check, timeout=10)
      guess = guess_msg.content

      if guess == ' '.join(chosen_emojis):
        economy[user_id]['balance'] += bet
        economie_data()
        await ctx.send(f"{ctx.author.mention}, you won! You remembered the emojis correctly and won {bet} coins.")
      else:
        economy[user_id]['balance'] -= bet
        economie_data()
        await ctx.send(f"{ctx.author.mention}, you lost. The correct emojis were {' '.join(chosen_emojis)}. You lost {bet} coins.")
    except asyncio.TimeoutError:
      await ctx.send(f"{ctx.author.mention}, time's up. You lost {bet} coins.")
      economy[user_id]['balance'] -= bet
      economie_data()

bot.run('MTA4NzQyMDE4ODYzNjQ4NzY4MA.GTHbUT.cfGuYybs-PZR46rnycdVDJX5BbHcMkB6l7KwM8')

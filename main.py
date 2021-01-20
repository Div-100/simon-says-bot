# Import statements
import discord
from discord.ext import commands
from discord import Intents
from discord.ext import tasks
import time
import asyncio
import random

# Defining the client
client = commands.Bot(command_prefix="s!",
                      case_insensitive=True, intents=Intents.all())
client.remove_command('help')

# Global Vars
is_game_running = False
users = []
simon = discord.Member
game_mode = ""
can_post = True

# Bot is ready
@client.event
async def on_ready():
    channel = client.get_channel(800681690593755166)
    await channel.send("I am here Nerds!")
    print("Simon says i am ready")
    post.start()


@client.command()
async def help(ctx):
    await ctx.send(
    """
    `s!enter` - Enter a game
    `s!start auto` - start an auto game
    `s!start manual` - Start a Manual Game
    `s!end` - End a manual game
    `s!eliminate <user: discord.Member>` - Eliminate a user (Can Only be accessed in a Manual game by the Simon)
    `s!remaining` - See the remaining players
    """
    )

# The start Group
@commands.cooldown(rate=1, per=30, type=commands.cooldowns.BucketType.guild)
@client.group(name="start")
async def start(ctx):
    if ctx.invoked_subcommand == None:
        await ctx.send("Use `s!start auto` for automatic Game or `s!start manual` for a manual game \
            ||Simon would be randomly chosen amongst the contestants for the manual games||")


# Auto Start
@commands.cooldown(rate=1, per=30, type=commands.cooldowns.BucketType.guild)
@start.command(name="auto")
async def start_auto(ctx):
    # Referring the global Vars
    global is_game_running
    global game_mode
    global can_post
    responses = []

    # Checking if the game is already running
    if is_game_running:
        await ctx.send("A game is already Running ;-;")
        return

    # Checking if there are 2 or more users
    if len(users) < 2:
        await ctx.send("At least 2 users are needed to start the game.")
        return
    
    # Channel is The simon says channel
    if ctx.channel.id != 797561095547781142:
        await ctx.send("Can only be started in #simon-says")
        return

    # Telling other functions that the code has started running
    is_game_running = True
    game_mode = "AUTO"
    contestant_role = ctx.guild.get_role(800769747805405215)

    # Making Calculations
    await ctx.send("Just a second let me make some calculations.")

    # Adding roles to all the users
    for user in users:
        await user.add_roles(contestant_role)

    # Telling the contestants That the game is starting, DUH!
    await ctx.send(f"The game is starting {contestant_role.mention} ||Psst.... Capitalisation Matters||")
    # Modes 
    modes = ["+", "-"]

    # All of the responses
    mode_responses = {
        # Have to send
        "+": (
        ["Simon says Type `LOL`", lambda message: message.content == "LOL"],
        ["Don't send `lol` in the chat", lambda message: "lol" in message.content],
        ["Simon Says Send a message With an emoji in it",
            lambda message: ':' in message.content or not message.content.isascii()],
        ["Simon says Send in the chat who made the bot",
            lambda message: message.content.lower() == "div_100"],
        ["Simon says say `ok`", lambda message: message.content == "ok"],
        ["Simon Says send in the chat Who is the co-owner", lambda message: message.content.lower() == "golden"],
        ["Simon says tell me Who made Grandma's Utilities", lambda message: message.content.lower() == "soos"],
        ["Simon Says ~~Don't~~ Send in the chat who made Grandma's DJ.", lambda message: message.content.lower() == "powerunited"]
    ),

        # Don't Have to send
        "-": (
        ["Send A message with a link in it.", lambda message: "http" in message.content.lower() or "www" in message.content.lower()],
        ["Send `LOL` in chat", lambda message: "LOL" in message.content],
        ["Send in the chat Who made the bot", lambda message: message.content.lower() == "div_100"],
        ["Say `ok`", lambda message: message.content.lower() == "ok"],
        ["Send in the chat Who is the co-owner", lambda message: message.content.lower() == "golden"],
        ["Tell me Who made Grandma's Utilities", lambda message: message.content.lower() == "soos"],
        ["~~Don't~~ Send in the chat who made Grandma's DJ.", lambda message: message.content.lower() == "powerunited"]
    )
    }

    # While there is more than 1 user
    while len(users) > 1:
        # Choosing the mode
        mode = random.choice(modes)
        # Choosing the Response
        choice = random.choice(mode_responses[mode])
        await ctx.send(choice[0])
        end_time = time.time() + 10

        # If it did not timeout
        while time.time() < end_time:

            try:
                response = await client.wait_for('message', check=choice[1], timeout=2)
                responses.append(response)
            except:
                pass

        await ctx.send("Timeout... Calculating results.")

        # Global Checks
        for response in responses:
            if response.channel != ctx.channel or contestant_role not in response.author.roles:
                responses.remove(response)

        # Adding all the `message.author`s to the authors table
        authors = []
        for response in responses:
            authors.append(response.author)


        ## Win Checks
        # For the + mode

        if mode == "+":
        
            # If no one responded
            if len(responses) == 0:
                await ctx.send("Either No one responded or no one sent the correct answer ||Capitalisation Matters||. ( Match was a tie ).")
                users.clear()
                responses.clear()
                for user in contestant_role.members:
                    await user.remove_roles(contestant_role)
                is_game_running = False
                can_post = True
                return

            # if the no. of total users not equals no. of people who sent the message
            elif len(users) != len([response.author for response in responses]):
                
                # Eliminating everyone who did not respond
                for user in users:
                        if user not in [response.author for response in responses]:
                            await user.remove_roles(contestant_role)
                            await ctx.send(f"{user.mention}, You are disqualified.")
                            users.remove(user)

                # If there is only one user (They won)
                if len([response.author for response in responses]) == 1:
                    await ctx.send(f"Great {[response.author for response in responses][0].mention} You won the game.")
                    users.clear()
                    responses.clear()
                    for user in contestant_role.members:
                        await user.remove_roles(contestant_role)
                    is_game_running = False
                    can_post = True
                    responses.clear()
                    return
            
            # if everyone responded
            else:
                await ctx.send("Great Ya'll are Soooo Smart :(")
                responses.clear()

        # The - Mode
        elif mode == "-":
            # If No one responded
            if len(responses) == 0:
                await ctx.send("Great Ya'll are Soooo Smart :(")
                responses.clear()
            
            # If  the no. of people who responded not equals the no. of people who entered
            elif len(users) != len([response.author for response in responses]):
                
                # Eliminating the users who sent a message
                for user in users:
                    if user in [response.author for response in responses]:
                        await user.remove_roles(contestant_role)
                        await ctx.send(f"{user.mention}, You are disqualified.")
                        users.remove(user)
                        responses.remove([response for response in responses if response.author == user][0])
                        continue

                # If Someone Won
                if len(users) == 1:
                    await ctx.send(f"Great {users[0].mention} You won the game.")
                    users.clear()
                    responses.clear()
                    for user in contestant_role.members:
                        await user.remove_roles(contestant_role)
                    can_post = True
                    is_game_running = False
                    return

            # Everyone fell for it. 
            else:
                await ctx.send("Haha Ya'll Fell For it :)))). ||Match was a tie||")
                responses.clear()
                users.clear()
                for user in contestant_role.members:
                    await user.remove_roles(contestant_role)
                is_game_running = False
                can_post = True
                return


# Manual Game startup
@commands.cooldown(rate=1, per=30, type=commands.cooldowns.BucketType.guild)
@start.command(name="manual")
async def start_manual(ctx):

    # Defining some global vars
    global is_game_running
    global game_mode
    global simon

    # Checking if a game is already running
    if is_game_running:
        await ctx.send("A Game is already Running. ._.")
        return
    
    # Chekcing if there are enough players
    if len(users) < 3:
        await ctx.send("At least 3 users are requried for a manual game... if there are 2 users consider going for the auto games (`s!start auto`).")
        return

    # Channel is The simon says channel
    if ctx.channel.id != 797561095547781142:
        await ctx.send("Can only be started in #simon-says")
        return
    
    # Adding Contestant role to every player
    contestant_role = ctx.guild.get_role(800769747805405215)
    
    for user in users:
        await user.add_roles(contestant_role)

    # Telling other functions about these stuff
    is_game_running = True
    game_mode = "MANUAL"
    simon = random.choice(users)

    # Sending the message, DUH!
    await ctx.send(f"{contestant_role.mention} a manual game is starting, With the simon {simon.mention}")
    users.remove(simon)


# Eliminate a user
@client.command()
async def eliminate(ctx, *, user: discord.Member):
    # Globar vars
    global is_game_running 
    global can_post

    # Checking if a game is running
    if not is_game_running:
        await ctx.send("A game is not even running...")
        return
    
    # Checking if the author is the simon
    if ctx.author != simon:
        await ctx.send("You are not the simon.")
        return

    # Checking if the game mode is manual
    if game_mode != "MANUAL":
        await ctx.send("An auto Mode game is running...")
        return
    
    # Chekcing if they mentioned a valid user
    if user is None:
        await ctx.send("Next time run the command like `s!eliminate <user: discord.Member>")
        return
    
    # If the users is currently playing
    if user not in users:
        await ctx.send("That user is not Currently Playing.")
        return

    # Eliminating them
    contestant_role = ctx.guild.get_role(800769747805405215)
    await user.remove_roles(contestant_role)
    users.remove(user)
    await ctx.send(f"Eliminated {user.name}.")

    # Winning Checks
    if len(users) == 1:
        await ctx.send(f"Congrats {users[0].mention} You won the game.")
        users.clear()
        for user in contestant_role.members:
            await user.remove_roles(contestant_role)
        can_post = True
        is_game_running = False
    elif len(users) == 0:
        await ctx.send("Congrats No one won the game ;-;")
        users.clear()
        for user in contestant_role.users:
            await user.remove_roles(contestant_role)
        is_game_running = False
        can_post = True
    

# The no. of remaining Players
@client.command(aliases=["joined"])
@commands.cooldown(rate=1, per=30, type=commands.cooldowns.BucketType.user)
async def remaining(ctx):
    await ctx.send(", ".join([str(user) for user in users]))


# End the manual game
@client.command()
@commands.cooldown(rate=1, per=30, type=commands.cooldowns.BucketType.guild)
async def end_game(ctx):
    global is_game_running
    global simon
    global game_mode
    global can_post

    contestant_role = ctx.guild.get_role(800769747805405215)

    if not is_game_running:
        await ctx.send("No game is running. ;-;")
        return

    if game_mode != "MANUAL":
        await ctx.send("Only available for 'MANUAL' game mode.")
        return
    
    simon = discord.Member
    is_game_running = False
    can_post = True

    for user in contestant_role.members:
        await user.remove_roles(contestant_role)

    users.clear()
    await ctx.send("Done Ended the game...")


# Pretty Self-explanatory
@client.command()
@commands.cooldown(rate=1, per=30, type=commands.cooldowns.BucketType.user)
async def enter(ctx):
    if is_game_running:
        await ctx.send("A game is currently running.")
        return

    if ctx.author not in users:
        users.append(ctx.author)
        await ctx.send("You have been accepted in the game.")

    else:
        await ctx.send("You are already in the game. .-.")


# Ping....
@client.command()
@commands.cooldown(rate=1, per=10, type=commands.cooldowns.BucketType.channel)
async def ping(ctx):
    websocket_latency = client.latency * 1000
    start_time = time.time()
    message = await ctx.send("Ping huh?")
    await message.edit(content="Pong")
    end_time = time.time()
    message_edit_latency = (end_time - start_time) * 1000
    embed = discord.Embed(title="Ping... ", description=f"Websocket Latency: **{websocket_latency:.2f}** ms \nMessage edit latency: **{message_edit_latency:.2f}** ms",
    colour=0xF1EFE3)
     
    await message.edit(embed=embed)


# Post the message to the channel if a game is not running
@tasks.loop(seconds=60)
async def post():
    await client.wait_until_ready()
    global can_post
    global is_game_running

    if not is_game_running:
        if can_post:
            channel = client.get_channel(800776072698396722)
            await channel.send("A new Game has started, Type in `s!enter` to Participate in it.")
            can_post = False


@client.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)

    # They Didn't run a valid command
    if isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send(f"> <:Error:800689474765717516> You Are on Cool down, Try again in {ctx.command.get_cooldown_retry_after(ctx):.2f} seconds")
    elif isinstance(error, discord.ext.commands.errors.MemberNotFound):
        await ctx.send(f"> <:Error:800689474765717516> {error.argument} is not a valid member!")
    else:
        embed = discord.Embed(title="Error Occured", color=discord.Color.red(), description=str(error))
        embed.add_field(name="Member", value=f"{ctx.author.mention}")
        embed.add_field(name="Channel", value=f"{ctx.channel.mention}")
        embed.add_field(name="Command", value=f"{ctx.command.name}")
        embed.add_field(name="Arguments", value=f"{ctx.args}")

        channel = client.get_channel(800681690593755166)
        await channel.send(embed=embed)
        raise error
        

client.run("ODAwNjk1NTI4OTcwNjQ5NjAw.YAV30g.Z1usR5kl46i6-qb5_dnc85DwlZ8")

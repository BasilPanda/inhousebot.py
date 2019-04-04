import discord
import logging
import queue
from discord.ext import commands
from Player import Player

import csv
import datetime
import config

logging.basicConfig(filename='log.log',
                    format='%(asctime)s :: %(message)s',
                    level=logging.INFO)

description = '''This bot has several command functions.'''
client = commands.Bot(command_prefix='$', description=description)

TOKEN = config.bot_token

# four global lobbies
lobby1 = []
lobby2 = []
lobby3 = []
lobby4 = []
# teams for each lobby
lob1_b = []
lob1_r = []
lob2_b = []
lob2_r = []
lob3_b = []
lob3_r = []
lob4_b = []
lob4_r = []
# waiting queue
in_queue = queue.Queue(maxsize=0)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('\n')


# Create a text file version
@client.command(pass_context=True,
                name='register',
                description="Registers a player into the inhouse system.")
async def register(ctx, *args):
    if not check_database(ctx):
        with open('database.csv', 'a', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            ign = " ".join(args)
            if not ign:
                await client.say('Please enter your League IGN after the $register command!')
                return
            # Row setup as DATE,ID,ELO,IGN,WINS,LOSSES,STREAK
            currentTime = datetime.datetime.now()
            strTime = str(currentTime.month) + "-" + str(currentTime.day) + "-" + str(currentTime.year)
            logging.info("Inserting into DB... Date: " + strTime + " ID: " + ctx.message.author.id +
                          " ELO: " + str(500) + " IGN: " + ign + " WINS: 0 LOSSES: 0 STREAK: 0")
            filewriter.writerow([strTime, ctx.message.author.id, str(500), ign, '0', '0', '0'])
        logging.info("Bot sent msg: Registration complete " + ctx.message.author.mention + "!")
        await client.say('Registration complete ' + ctx.message.author.mention + "!")
        return
    else:
        logging.info("Bot sent msg: You registered already " + ctx.message.author.mention + "!")
        await client.say('You registered already ' + ctx.message.author.mention + "!")
    return


# Enter the queue
@client.command(pass_context=True,
                name='queue',
                aliases=['join'])
async def queue(ctx):
    if not check_database(ctx):
        await client.say('You are not registered yet! Use $register ign to become join inhouses!')
    else:
        if in_queue.qsize() >= 10:
            if not lobby1:  # remember to change
                start_lobby_auto(lobby1)
            elif not lobby2:
                start_lobby_auto(lobby2)
            elif not lobby3:
                start_lobby_auto(lobby3)
            elif not lobby4:
                start_lobby_auto(lobby4)
            else:
                in_queue.put(get_player(ctx))
                await client.say("All lobbies currently filled! Please wait!")
        else:
            in_queue.put(get_player(ctx))
        await client.say("Players Queued: " + str(in_queue.qsize()))


def check_database(ctx):
    with open('database.csv', 'r') as f:
        logging.info("Checking database for: " + ctx.message.author.id)
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if ctx.message.author.id == row[1]:
                logging.info(ctx.message.author.id + " exists in the DB.")
                return True
        logging.info(ctx.message.author.id + " does not exist in the DB.")
        return False


def get_player(ctx):
    logging.info("Getting player...")
    with open('database.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if ctx.message.author.id == row[1]:
                p = Player(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                return p
    logging.info("Player information retrieved.")


# This just sorts the players in lobby by elo and alternates in placing them in the teams.
# Highest player gets put on blue team. Next highest red team. Next highest blue and so on.
def start_lobby_auto(lobby):
    for x in range(10):
        lobby.append(in_queue.get())
    lobby.sort(key=lambda x: x.elo, reverse=True)
    for x in range(5):
        lob1_r.append(lobby[x * 2])
        lob1_b.append(lobby[x * 2 + 1])


# Attempt to do captain pick order
def start_lobby_cap(lobby):
    for x in range(10):
        lobby.append(in_queue.get())
    lobby.sort(key=lambda x: x.elo, reverse=True)
    temp = lobby
    lob1_r.append(temp[0])
    lob1_b.append(temp[1])
    temp.pop(0)
    temp.pop(1)

    async def _wait(future, check):
        @client.listen()
        async def on_message(msg):
            counter = 0
            if counter % 2 == 0:
                if msg.author.id == lob1_r[0].id:
                    p = check_if_on_team(msg)
                    if p:
                        lob1_r.append(p)
                        temp.remove(p)
                        counter += 1
                    else:
                        await client.say(msg + " doesn't exist in this lobby!")
            else:
                if msg.author.id == lob1_b[0].id:
                    p = check_if_on_team(msg)
                    if p:
                        lob1_b.append(p)
                        temp.remove(p)
                        counter += 1
                    else:
                        await client.say(msg + " doesn't exist in this lobby!")


def check_if_on_team(msg, temp):
    for x in temp:
        if msg == x.ign:
            return x
    return False


client.run(TOKEN)


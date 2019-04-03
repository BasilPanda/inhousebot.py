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
                    level=logging.DEBUG)

description = '''This bot has several command functions.'''
client = commands.Bot(command_prefix='$', description=description)

TOKEN = config.bot_token

lobby1 = []
lobby2 = []
lobby3 = []
lobby4 = []
in_queue = queue.Queue(maxsize = 50)


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
            
            # Row setup as DATE,ID,ELO,IGN,WINS,LOSSES,STREAK
            currentTime = datetime.datetime.now()
            strTime = str(currentTime.month) + "-" + str(currentTime.day) + "-" + str(currentTime.year)            
            logging.debug("Inserting into DB...\nDate: " + strTime + " ID: " + ctx.message.author.id +
                          " ELO: " + str(500) + " IGN: " + ign + " WINS: 0 LOSSES: 0 STREAK: 0")            
            filewriter.writerow([strTime, ctx.message.author.id, str(500), ign, '0', '0', '0'])
        logging.debug("Bot sent msg: Registration complete " + ctx.message.author.mention + "!")
        await client.say('Registration complete ' + ctx.message.author.mention + "!")
        return
    else:
        logging.debug("Bot sent msg: You registered already " + ctx.message.author.mention + "!")
        await client.say('You registered already ' + ctx.message.author.mention + "!")
    return


# Enter the queue
@client.command(pass_context=True,
                name='queue',
                aliases=['join'])
async def queue(ctx):
    if check_database(ctx):
        await client.say('You are not registered yet! Use $register ign to become join inhouses!')
    else:
        if len(in_queue) >= 10:
            if not lobby1:
                start_lobby(lobby1)
            elif not lobby2:
                start_lobby(lobby2)
            elif not lobby3:
                start_lobby(lobby3)
            elif not lobby4:
                start_lobby(lobby4)
            else:
                inqueue.put(get_player(ctx))
                await client.say("All lobbies currently filled! Please wait!")
        else:
            inqueue.put(get_player(ctx))
	await client.say("Players Queued: " + len(in_queue))


def check_database(ctx):
    with open('database.csv', 'r') as f:
        logging.debug("Checking database for: "+ ctx.message.author.id)
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if ctx.message.author.id == row[1]:
                logging.debug(ctx.message.author.id + " exists in the DB.")
                return True
        logging.debug(ctx.message.author.id + " does not exist in the DB.")
        return False


def get_player(ctx):
    p = Player()
    logging.debug("Getting player...")
    with open('database.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if ctx.message.author.id == row[1]:
                p.date = row[0]
                p.id = row[1]
                p.elo = row[2]
                p.ign = row[3]
                p.wins = row[4]
                p.losses = row[5]
                p.streak = row[6]
                break
    logging.debug("Player information retrieved")
    return p

# not finished
def start_lobby(lobby):
	for x in range(10):
		lobby.append(inqueue.get())
	lobby.sort(key=lambda x: x.elo, reverse = True)
	
  
client.run(TOKEN)



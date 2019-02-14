import discord
from discord.ext import commands
from Player import Player

import csv
import datetime

description = '''This bot has several command functions.'''
client = commands.Bot(command_prefix='$', description=description)

TOKEN = 'NTQyMTk4MTg4OTMzNjQ0Mjk4.DzrDPw.Ajg5xYwTGg5dvI7rs7Um0JFoEQE'

lobby1 = []
lobby2 = []
lobby3 = []
lobby4 = []
in_queue = 0


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
            filewriter.writerow([strTime, ctx.message.author.id, str(500), ign, '0', '0', '0'])
        await client.say('Registration complete ' + ctx.message.author.mention + "!")
        return
    else:
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
        p = Player()
        if len(lobby1) < 10:
            lobby1.append()
    return


def check_database(ctx):
    with open('database.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if ctx.message.author.id == row[1]:
                return True
        return False


def get_player(ctx):
    p = Player()
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
    return p


client.run(TOKEN)

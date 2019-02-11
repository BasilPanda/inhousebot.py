import discord
from discord.ext import commands

import csv
import datetime

description = '''This bot has several command functions.'''
client = commands.Bot(command_prefix='$', description=description)

TOKEN = 'NTQyMTk4MTg4OTMzNjQ0Mjk4.DzrDPw.Ajg5xYwTGg5dvI7rs7Um0JFoEQE'


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


def check_database(ctx):
    with open('database.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            for field in row:
                if ctx.message.author.id == field:
                    return True
        return False


client.run(TOKEN)

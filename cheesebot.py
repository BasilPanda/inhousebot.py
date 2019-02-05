import discord
from discord.ext import commands

description = '''This bot has several command functions.'''
bot = commands.Bot(command_prefix='$', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('\n')


# Create an SQL database.
@bot.command()
async def signup(username):
    if username:
        msg = 'You signed up already {0.author.mention}!'.format()
        await bot.send_message(username.channel, msg)
        return
    else:
        # Add to database
        return

bot.run('token')

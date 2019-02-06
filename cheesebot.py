import discord
from discord.ext import commands

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
                description="Registers a player into the MMR system.")
async def register(ctx):
    file = open("data.txt", "w+")
    file_s = file.read()

    if str(ctx.message.author.id) in file_s:
        await client.say('You registered already ' + ctx.message.author.mention + "!")
    else:
        # Add to text file
        file.write(str(ctx.message.author.id)+","+"0")
        await client.say('Registration complete!')
    file.close()
    return


client.run(TOKEN)

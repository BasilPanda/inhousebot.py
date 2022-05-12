"""
Main file
"""
# System imports
import json
import logging
import sys
from collections import deque

# External Imports
import requests
from discord.ext import commands

# Local Imports
import config
from database import Database as db

# Logging stuff
log = logging.getLogger('')
log.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# Globals
cmd_prefix = '!'

description = '''Inhouse Bot Help Manual:'''
client = commands.Bot(command_prefix=cmd_prefix, description=description)
client.remove_command('help')
db_connection = db.init_database()
TOKEN = config.bot_token
API_KEY = config.bot_token

startup_extensions = ["cmds.test_cmds", "cmds.user", "cmds.admin", "cmds.captain"]

# CONSTANTS
INIT_WINS = 0
INIT_LOSS = 0
INIT_STREAK = 0
INIT_ELO = 1500

# all active lobbies
lobbies = []

# waiting queue
in_queue = deque()
test_queue = deque()

# lists
lose_arr = ["lose", "loss", "l"]
win_arr = ["win", "won", "w"]


@client.event
async def on_ready():
    """
    Bot startup
    """
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('\n')

    # To check current API
    r = requests.get(
        "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Riot Phreak?api_key="
        + config.lol_token)
    response_json = r.json()
    # print(response_json)
    if 'status' in response_json:
        if 'Forbidden' in response_json['status']['message']:
            print("Please update League API key!")
            sys.exit(-1)

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    client.run(TOKEN)


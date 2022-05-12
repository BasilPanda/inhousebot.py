"""
Main file
"""
# System imports
import asyncio
from datetime import timedelta, datetime
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
INIT_ELO = 1000

# all active lobbies
lobbies = []

# waiting queue
in_queue = deque()
test_queue = deque()

# lists
lose_arr = ["lose", "loss", "l"]
win_arr = ["win", "won", "w"]

async def check_decay():
    """
    Decay Checker. Decay elo above 1500
    """
    while True:
        sql = db.check_decay(db_connection)
        for player in sql:
            time = player[0]
            temp = time.split('-')
            lastPlayed = datetime.date(int(temp[0]), int(temp[1]), int(temp[2]))
            if lastPlayed + timedelta(weeks=2) < datetime.datetime.today().date():
                elo = player[2]
                if elo > 1500:
                    print("Inactivity detected for " + player[3] + ". LP decay activated.")
                    print("Elo was: " + str(elo))
                    elo -= 0
                    if elo < 1500:
                        elo = 1500
                    print("Elo now: " + str(elo))
                    player_id = player[1]
                    db.decay_player(db_connection, elo, player_id, lastPlayed + timedelta(days=1))
        await asyncio.sleep(delay=86400)


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
            exc = f"{type(e).__name__}: {e}"
            print(f"Failed to load extension {extension}\n{exc}")
    client.run(TOKEN)


import discord
import datetime
import math
import requests
import json
import config
import sys
from discord.ext import commands
from Player import Player
from database import Database as db
import datetime

description = '''Inhouse Bot Help Manual:'''
client = commands.Bot(command_prefix='$', description=description)
client.remove_command('help')
db_connection = db.init_database()
TOKEN = config.bot_token
API_KEY = config.bot_token

startup_extensions = ["test_cmds", "user", "admin", "captain"]

#   CONSTANTS
INIT_WINS = 0
INIT_LOSS = 0
INIT_STREAK = 0
INIT_ELO = 1500

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
in_queue = []
test_queue = []
# lists
lose_arr = ["lose", "loss", "l"]
win_arr = ["win", "won", "w"]


@client.event
async def on_ready():
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


# Checks to see if user sending command is a captain
def is_captain(user_id):
    # assuming lobbies are already sorted
    if len(lobby1) > 0:
        for player in lobby1:
            # if the ID is a match and that match is either the 1st or 2nd player in an ELO-sorted lobby
            if str(player.id) == user_id and (lobby1.index(player) == 0 or lobby1.index(player) == 1):
                return 1
    elif len(lobby2) > 0:
        for player in lobby2:
            if str(player.id) == user_id and (lobby2.index(player) == 0 or lobby2.index(player) == 1):
                return 2
    elif len(lobby3) > 0:
        for player in lobby3:
            if str(player.id) == user_id and (lobby3.index(player) == 0 or lobby3.index(player) == 1):
                return 3
    elif len(lobby4) > 0:
        for player in lobby4:
            if str(player.id) == user_id and (lobby4.index(player) == 0 or lobby4.index(player) == 1):
                return 4
    return 0


# Create provider ID
def create_provider_id(region, callback_url):
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/providers?api_key=' + config.lol_token
    data = {"region": region, "url": callback_url}
    postRequest = requests.post(url, data=json.dumps(data), verify=True)
    postJson = postRequest.json()
    return postJson


# Create tournament ID
def create_tournament_id(name, provider_id):
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/tournaments?api_key=' + config.lol_token
    data = {"name": name, "providerId": provider_id}
    postRequest = requests.post(url, data=json.dumps(data), verify=True)
    postJson = postRequest.json()
    tourn = create_tournament_game(postJson)
    return tourn


def create_tournament_game(tournament_id):
    count = 10
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/codes?count=' + count + '&tournamentId=' + tournament_id + '&api_key=' + config.lol_token
    data = {"mapType": "SUMMONERS_RIFT", "pickType": "DRAFT_MODE", "spectatorType": "ALL", "teamSize": 5}
    headers = {'content-type': 'application/json'}
    postRequest = requests.post(url, data=json.dumps(data), verify=True)
    # contains list of the tournament IDs
    postJson = postRequest.json()
    return postJson


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    client.run(TOKEN)


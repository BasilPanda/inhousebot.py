
import math
import config
import sqlite3
import requests
import cassiopeia as cass
from cassiopeia import Summoner

from Player import Player
from datetime import date

cass.set_riot_api_key(config.lol_token)
API_KEY = config.lol_token
tier_dict = {"UNRANKED": 1, "IRON": 1, "BRONZE": 1, "SILVER": 1, "GOLD": 1.5, "PLATINUM": 2, "DIAMOND": 3,
             "MASTER": 3, "GRANDMASTER": 3, "CHALLENGER": 3}

rank_dict = {"I": 100, "II": 75, "III": 50, "IV": 25, "0": 0}


class Database:

    # This initializes the database.
    @classmethod
    def init_database(cls):
        # connect to database
        # creates new db file if doesn't exists
        try:
            db_connection = sqlite3.connect('inhousebot.db')
        except sqlite3.Error as e:
            print(e)
        # get cursor to execute SQL commands
        c = db_connection.cursor()
        # setup user table
        c.execute(''' CREATE TABLE IF NOT EXISTS users (discord_id int primary key, registration_date DATE) ''')
        # setup league table

        c.execute('''CREATE TABLE IF NOT EXISTS league (last_played DATE, discord_id int not null references users(
        discord_id), elo int, player_ign varchar(255) primary key, wins int, losses int, streak ints, tier varchar(
        30), rank varchar(6)) ''')
        # setup league match history tables
        c.execute(''' CREATE TABLE IF NOT EXISTS league_match (match_id INTEGER primary key, date_played DATE)''')

        c.execute('''CREATE TABLE IF NOT EXISTS league_info (match_id int non null references league_match(match_id), 
        discord_id int not null references users(discord_id), elo_change int non null, primary key (discord_id, 
        match_id))''')

        c.execute(''' CREATE TABLE IF NOT EXISTS league_ban (discord_id int not null references users(discord_id) 
        primary key, banned int)''')

        c.close()

        return db_connection


    # This will create an entry in the ban database
    @classmethod
    def ban_player(cls, db_connection, discord_id):
        # get cursor to execute SQL commands
        c = db_connection.cursor()

        # get match id
        c.execute('INSERT INTO league_ban (discord_id, banned) VALUES (?, ?)', (discord_id, 1))
        db_connection.commit()
        return

    # This will create an entry in the ban database
    @classmethod
    def check_ban(cls, db_connection, discord_id):
        # get cursor to execute SQL commands
        c = db_connection.cursor()

        # get match id
        c.execute('SELECT discord_id FROM league_ban WHERE discord_id = ?', (discord_id,))
        sql_return = c.fetchone()

        return sql_return

    # This will remove the player from the ban database
    @classmethod
    def unban_player(cls, db_connection, discord_id):
        # get cursor to execute SQL commands
        c = db_connection.cursor()
        c.execute('DELETE FROM league_ban WHERE discord_id = ?', (discord_id,))
        db_connection.commit()
        return

    # This will get all entries with given match ID
    @classmethod
    def get_match(cls, db_connection, match_id):
        # get cursor to execute SQL commands
        c = db_connection.cursor()

        # get match id 
        c.execute('SELECT * FROM league_info WHERE match_id = ?', (match_id,))

        # return array containing response from previous execute command
        sql_return = c.fetchall()

        # print(sql_return)

        # will return the match id 
        return sql_return

    # This will create a match id that will be used to identify a game in league_match table
    @classmethod
    def create_match(cls, db_connection):
        # get cursor to execute SQL commands
        c = db_connection.cursor()

        date_played = str(date.today())

        # create match 
        c.execute("INSERT INTO league_match (date_played) VALUES (?)", (date_played,))

        db_connection.commit()

        # get match id 
        c.execute('SELECT match_id FROM league_match ORDER BY match_id DESC LIMIT 1')

        # return array containing response from previous execute command
        sql_return = c.fetchone()
       
        # print(sql_return)

        # will return the match id 
        return sql_return[0]

    # This will store the match info for each player
    @classmethod
    def update_match_history(cls, db_connection, discord_id, match_id, elo_change):
        # get cursor to execute SQL commands
        c = db_connection.cursor()

        # add to match info 
        c.execute("INSERT INTO league_info (match_id, discord_id, elo_change) VALUES (?, ?, ?)",
                  (match_id, discord_id, elo_change))

        db_connection.commit()

        return


    # This checks to see if the user is in the data_base
    @classmethod
    def check_user(cls, db_connection, discord_id):
        # get cursor to execute SQL commands
        c = db_connection.cursor()
        c.execute('SELECT discord_id FROM users WHERE discord_id = ?', (discord_id,))

        # return array containing response from previous execute command
        sql_return = c.fetchall()

        return sql_return

    # This checks to see if the league user is registered
    @classmethod
    def check_league(cls, db_connection, discord_id):
        # get cursor to execute SQL commands
        c = db_connection.cursor()
        c.execute('SELECT discord_id FROM league WHERE discord_id = ?', (discord_id,))

        # return array containing response from previous execute command
        sql_return = c.fetchall()

        return sql_return

    # This checks to see if the inputted ign is a valid League IGN
    @classmethod
    def validate_player(cls, response_json):
        if 'status' in response_json:
            return False
        else:
            return True
    # This gets the player from the database.
    @classmethod
    def get_player(cls, db_connection, discord_id):
        c = db_connection.cursor()
        c.execute('SELECT * FROM league WHERE discord_id = ?', (discord_id,))

        col = c.fetchone()
        player = Player(col[0], col[1], col[2], col[3], col[4],
                        col[5], col[6], col[7], col[8])
        return player

    # This updates the database with the new player
    @classmethod
    def update_player(cls, db_connection, player):
        c = db_connection.cursor()
        c.execute('UPDATE league SET last_played = ?, elo = ?, wins = ?, losses = ?, streak = ? WHERE discord_id = ?',
                  (str(date.today()), player.elo, player.wins, player.losses, player.streak, player.id,))
        db_connection.commit()

    # Updates win
    @classmethod
    def update_win(cls, db_connection, user_id):
        c = db_connection.cursor()

        # update wins by 1
        # increase streak
        c.execute(''' UPDATE league SET wins = wins + 1, streak = streak + 1 WHERE discord_id = ?''', (user_id,))
        db_connection.commit()

    # Updates loss
    @classmethod
    def update_loss(cls, db_connection, user_id):
        c = db_connection.cursor()

        # update wins by 1
        # set streak to 0
        c.execute(''' UPDATE league SET losses = losses + 1, streak = 0 WHERE discord_id = ?''', (user_id,))
        db_connection.commit()

    # Updates elo
    @classmethod
    def update_elo(cls, db_connection, user_id, elo):
        c = db_connection.cursor()

        # update wins by 1
        c.execute(''' UPDATE league SET elo = elo + ? WHERE discord_id = ?''', (elo, user_id))
        db_connection.commit()

    # This gets the predetermined elo boost by using Cassiopeia API
    @classmethod
    def determine_initial_elo(cls, tier, rank, lp):
        bonus = 0
        try:
            tier_multiplier = tier_dict[tier]
            rank_addition = rank_dict[rank]
            bonus = tier_multiplier * 100 + rank_addition
            if tier == "MASTER" or tier == "GRANDMASTER" or tier == "CHALLENGER":
                bonus = bonus + math.ceil(lp / 15)
            return math.floor(bonus)
        except AttributeError:
            return bonus

    # fetch the leaderboard
    @classmethod
    def get_leaderboard(cls, db_connection):
        c = db_connection.cursor()
        c.execute('SELECT * FROM league')

        players = c.fetchall()
        return players

    # This checks current rank
    @classmethod
    def check_rank(cls, name):
        r = requests.get(
            "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key="
            + config.lol_token)
        response_json = r.json()
        return response_json

    @classmethod
    def get_rank(cls, response_json):
        r = requests.get(
            "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + response_json['id'] + "?api_key="
            + config.lol_token)
        response_json = r.json()
        print(response_json)
        try:
            if response_json[0]['queueType'] == 'RANKED_SOLO_5x5':
                print("Tier: " + response_json[0]['tier'])
                print("Rank: " + response_json[0]['rank'])
                return response_json[0]['tier'], response_json[0]['rank'], response_json[0]['leaguePoints']
            elif response_json[1]['queueType'] == 'RANKED_SOLO_5x5':
                print("Tier: " + response_json[1]['tier'])
                print("Rank: " + response_json[1]['rank'])
                return response_json[1]['tier'], response_json[1]['rank'], response_json[1]['leaguePoints']
            elif response_json[2]['queueType'] == 'RANKED_SOLO_5x5':
                print("Tier: " + response_json[2]['tier'])
                print("Rank: " + response_json[2]['rank'])
                return response_json[2]['tier'], response_json[2]['rank'], response_json[2]['leaguePoints']
            elif response_json[3]['queueType'] == 'RANKED_SOLO_5x5':
                print("Tier: " + response_json[2]['tier'])
                print("Rank: " + response_json[2]['rank'])
                return response_json[3]['tier'], response_json[2]['rank'], response_json[3]['leaguePoints']
        except IndexError:
            print("Tier: UNRANKED")
            print("Rank: 0")
            return "UNRANKED", '0', '0'

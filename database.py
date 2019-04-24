import config
import sqlite3
import requests
import cassiopeia as cass
from cassiopeia import Summoner
from Player import Player
from datetime import date

cass.set_riot_api_key(config.lol_token)
API_KEY = config.lol_token
elo_dict = {"Unranked": 0, "Iron": 0, "Bronze": 0, "Silver": 0, "Gold": 20, "Platinum": 50, "Diamond": 100,
            "Master": 120, "GrandMaster": 120, "Challenger": 120}


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

        c.execute(''' CREATE TABLE IF NOT EXISTS league (last_played DATE, discord_id int not null references users(discord_id), elo int, 
        player_ign varchar(255) primary key, wins int, losses int, streak ints) ''')
        # setup league match history tables
        c.execute(''' CREATE TABLE IF NOT EXISTS league_match (match_id INTEGER primary key, date_played DATE)''')

        c.execute(''' CREATE TABLE IF NOT EXISTS league_info (match_id int non null references matches(match_id),
        discord_id int not null references users(discord_id), elo_change int non null, primary key (discord_id, match_id))''')

        c.close()

        return db_connection

    # This will get all entries with given match ID
    @classmethod
    def get_match(cls, db_connection, match_id):
        # get cursor to execute SQL commands
        c = db_connection.cursor()

        # get match id 
        c.execute('SELECT * FROM league_info WHERE match_id = ?', (match_id,))

        # return array containing response from previous execute command
        sql_return = c.fetchall()

        #print(sql_return)
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

        #print(sql_return)
        # will return the match id 
        return sql_return[0]

    # This will store the match info for each player
    @classmethod
    def update_match_history(cls, db_connection, discord_id, match_id, elo_change):
        # get cursor to execute SQL commands
        c = db_connection.cursor()

        # add to match info table
        c.execute("INSERT INTO league_info (match_id, discord_id, elo_change) VALUES (?, ?, ?)", (match_id, discord_id, elo_change))

        db_connection.commit()

        return 

    # This checks to see if the inputted ign is a valid League IGN
    @classmethod
    def validate_player(cls, player_ign):
        r = requests.get(
            "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + player_ign + "?api_key="
            + config.lol_token)
        response_json = r.json()
        print(response_json)
        if 'status' in response_json:
            return False
        else:
            return True

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

    # This gets the player from the database.
    @classmethod
    def get_player(cls, db_connection, discord_id):
        c = db_connection.cursor()
        c.execute('SELECT * FROM league WHERE discord_id = ?', (discord_id,))

        col = c.fetchone()
        print(col)
        player = Player(col[0], col[1], col[2], col[3], col[4],
                        col[5], col[6])
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
    def determine_initial_elo(cls, name: str, region: str):
        summoner = Summoner(name=name, region=region)
        try:
            return elo_dict[str(summoner.rank_last_season)]
        except AttributeError:
            return 0

    # fetch the leaderboard
    @classmethod
    def get_leaderboard(cls, db_connection):
        c = db_connection.cursor()
        c.execute('SELECT * FROM league')

        players = c.fetchall()
        return players

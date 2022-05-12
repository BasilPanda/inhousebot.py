from classes.Lobby import Lobby
from datetime import date, datetime
from discord.ext import commands
from inhousebot.inhousebot import *

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,
                      name='register',
                      description="Registers your League IGN with our inhouse database",
                      help="Syncs your League account with our database")
    async def register(self, ctx):
        # check if given IGN is already in database
        # otherwise add user to database
        if db.check_user(db_connection, ctx.message.author.id):
            await self.bot.say('You registered already ' + ctx.message.author.mention + "!")
            return

        # get user Discord ID
        user_id = ctx.message.author.id
        # get user IGN from command
        try:
            command, player_ign = ctx.message.content.split(" ", 1)
        except ValueError:
            await self.bot.say(
                ctx.message.author.mention + ", please provide a valid League IGN after the command.\nEx) "
                                             "$register Stahp Doing That")
            return

        # get registration date
        registration_date = str(date.today())
        # get cursor to execute SQL commands
        c = db_connection.cursor()

        # validate IGN
        if db.validate_player(player_ign):
            pass
        else:
            await self.bot.say('Please provide a valid IGN ' + ctx.message.author.mention + "!")
            return
        elo_boost = db.determine_initial_elo(player_ign, "NA")
        # Add user to database
        c.execute(
            "INSERT INTO users (discord_id, registration_date) VALUES (?, ?)", (user_id, registration_date))
        # Add user to league 
        c.execute(
            "INSERT INTO league (player_ign, discord_id, last_played, wins, losses, elo, streak) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (player_ign, user_id, registration_date, INIT_WINS, INIT_LOSS, INIT_ELO + elo_boost, INIT_STREAK))

        db_connection.commit()
        await self.bot.say(ctx.message.author.mention + " you have been registered successfully!")
        return

    @commands.command(pass_context=True,
                      name='match',
                      description="View match details",
                      help="Reports matches stored in database")
    async def match(self, ctx):
        # get match number from input
        try:
            command, match_num = ctx.message.content.split(" ", 1)
        except ValueError:
            await self.bot.say(
                ctx.message.author.mention + ", please provide a valid match number.\nEx) $match 24")
            return

        # get cursor to execute SQL commands
        c = db_connection.cursor()

        # get all entries with the given match id
        c.execute('SELECT * FROM league_info WHERE match_id = ?', (match_num,))

        # return array containing response from previous execute command
        sql_return = c.fetchall()

        if not sql_return:
            await self.bot.say("Match doesn't exist!")
            return

        # get match timestamp
        c.execute('SELECT date_played FROM league_match WHERE match_id = ?', (match_num,))

        # return array containing response from previous execute command
        match_timestamp = ' '.join(c.fetchone())
        datetime_timestamp = datetime.datetime.strptime(match_timestamp, '%Y-%m-%d')

        # converts the triple to a list of list so can be altered. 
        sql = [list(x) for x in sql_return]
        for x in sql:
            del x[0]

        for x in sql:
            # get names instead of discord ID
            c.execute('SELECT player_ign FROM league WHERE discord_id = ?', (x[0],))
            # store it in the list
            x[0] = ' '.join(c.fetchone())

        win_team, win_elo = [], []
        lose_team, lose_elo = [], []

        # splitting into separate arrays
        for x in sql:
            if x[1] >= 0:
                win_elo.append(x[1])
                win_team.append(x[0])
            else:
                lose_elo.append(x[1])
                lose_team.append(x[0])

        map(str, win_team)
        map(str, win_elo)
        map(str, lose_team)
        map(str, lose_elo)

        # creating win display
        win_embed = discord.Embed(title="__Match " + str(match_num) + " Results:__",
                                  colour=discord.Colour(0x20ea65),
                                  timestamp=datetime_timestamp)
        win_embed.add_field(name="Winning Team",
                            value='\n'.join(win_team),
                            inline=True)
        win_embed.add_field(name="ELO GAINED",
                            value='\n'.join("+" + str(x) for x in win_elo),
                            inline=True)

        # creating lost display
        lose_embed = discord.Embed(title="__Match " + str(match_num) + " Results:__",
                                   colour=discord.Colour(0xff0000),
                                   timestamp=datetime_timestamp)
        lose_embed.add_field(name="Losing Team",
                             value='\n'.join(lose_team),
                             inline=True)
        lose_embed.add_field(name="ELO LOST",
                             value='\n'.join(str(x) for x in lose_elo),
                             inline=True)

        # print displays.
        await self.bot.say(embed=win_embed)
        await self.bot.say(embed=lose_embed)

        return

    # Enter the queue
    @commands.command(pass_context=True,
                      name='queue',
                      help="Queues up for an inhouse game",
                      aliases=['join', 'letmein'])
    async def queue(self, ctx):
        # check if user is in queue first
        for x in in_queue:
            if str(x.id) == ctx.message.author.id:
                await self.bot.say(ctx.message.author.mention + " you're already in queue!")
                return

        if not db.check_user(db_connection, ctx.message.author.id):
            await self.bot.say(
                ctx.message.author.mention + f' you are not registered yet!\nUse {cmd_prefix}register <your ign> to join the inhouse system!')
        else:
            if len(in_queue) >= 9:
                # create a new lobby
                newLobby = Lobby()
                
                lobbies.append(newLobby)
                embed = Lobby.start_lobby_auto(in_queue)
                await self.bot.say(embed=embed)
            else:
                in_queue.append(db.get_player(db_connection, ctx.message.author.id))
            await self.bot.say("Players Queued: " + str(len(in_queue)))
        return

    # Exit the queue
    @commands.command(pass_context=True,
                      name='dequeue',
                      help="Leaves the inhouse queue",
                      aliases=['leave', 'letmeout'])
    async def dequeue(self, ctx):
        for x in in_queue:
            if str(x.id) == ctx.message.author.id:
                in_queue.remove(x)
                await self.bot.say("Players Queued: " + str(len(in_queue)))
                return
        await self.bot.say(ctx.message.author.mention + " you aren't in queue!")
        return

    # List the players in a specified lobby
    @commands.command(pass_context=True,
                      help="Prints out the player stats. If no mention is given then it will send the stats of user who sent the command.",
                      name='stats',
                      aliases=['mmr'])
    async def print_player(self, ctx):
        if len(ctx.message.mentions) == 1:
            if not db.check_user(db_connection, ctx.message.mentions[0].id):
                await self.bot.say(ctx.message.author.mention + " the user mentioned does not exist in the system!")
                return
            else:
                p = db.get_player(db_connection, ctx.message.mentions[0].id)
                embed = player_embed(p)
                await self.bot.say(embed=embed)
                return
        else:
            if db.check_user(db_connection, ctx.message.author.id):
                p = db.get_player(db_connection, ctx.message.author.id)
                embed = player_embed(p)
                await self.bot.say(embed=embed)
                return
            else:
                await self.bot.say(ctx.message.author.mention + " you're not in our system!")
                return

    @commands.command(pass_context=True,
                      help="Shows this help menu!")
    async def help(self, ctx, *args: str):
        return await commands.bot._default_help_command(ctx, *args)

    # Print the inhouse leaderboard
    @commands.command(pass_context=True,
                      help="Prints the top 20 players in the community.",
                      name='leaderboard',
                      aliases=['rank', 'ranks', 'rankings'])
    async def leaderboard(self):
        player_list = db.get_leaderboard(db_connection)
        embed = leaderboard_embed(player_list)
        await self.bot.say(embed=embed)
        return

    # Print the inhouse leaderboard
    @commands.command(pass_context=True,
                      help="Generates an op.gg link of the ign. Allows only one ign.",
                      name='opgg')
    async def opgg(self, ctx):
        try:
            command, player_ign = ctx.message.content.split(" ", 1)
        except ValueError:
            await self.bot.say(ctx.message.author.mention + " need an ign!")
            return
        name_list = player_ign.split()
        temp = ""
        for word in name_list:
            temp += word + "+"
        embed = discord.Embed(title="OP.GG LINK GENERATOR", colour=discord.Colour(0xffffff),
                              description="[CLICK ON ME FOR OP.GG!](https://na.op.gg/summoner/userName=" + temp + ")",
                              timestamp=datetime.datetime.today())
        await self.bot.say(embed=embed)

    # update league name
    @commands.command(pass_context=True,
                      help="Updates your ign!",
                      name='updateign')
    async def update_ign(self, ctx):
        # check that they have an account in the database
        if db.check_league(db_connection, ctx.message.author.id):
            pass
        else:
            await self.bot.say('You must register your account ' + ctx.message.author.mention + "!")
            return

        # get user Discord ID
        user_id = ctx.message.author.id

        try:
            command, player_ign = ctx.message.content.split(" ", 1)
        except ValueError:
            await self.bot.say(
               f"{ctx.message.author.mention} please provide a valid League IGN after the command.\nEx)  {cmd_prefix}updateign Stahp Doing That")
            return

        # validate IGN
        if db.validate_player(player_ign):
            pass
        else:
            await self.bot.say('Please provide a valid IGN ' + ctx.message.author.mention + "!")
            return

        # update IGN

        # get cursor to execute SQL commands
        c = db_connection.cursor()

        c.execute(''' UPDATE league SET player_ign = ? WHERE discord_id = ?''', (player_ign, user_id))
        db_connection.commit()

        await self.bot.say(ctx.message.author.mention + " your IGN has been successfully updated!")
        return


def setup(bot):
    bot.add_cog(User(bot))

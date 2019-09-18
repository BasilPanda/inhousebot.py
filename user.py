from datetime import date
from lobby import *

restrict = ["UNRANKED", "IRON", "BRONZE", "SILVER"]


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
            await ctx.send('You registered already ' + ctx.message.author.mention + "!")
            return

        # get user Discord ID
        user_id = ctx.message.author.id
        # get user IGN from command
        try:
            command, player_ign = ctx.message.content.split(" ", 1)
        except ValueError:
            await ctx.send(
                ctx.message.author.mention + ", please provide a valid League IGN after the command.\nEx) "
                                             "!register Stahp Doing That")
            return

        # get registration date
        registration_date = str(date.today())
        # get cursor to execute SQL commands
        c = db_connection.cursor()
        response = db.check_rank(player_ign)
        # validate IGN
        if db.validate_player(response):
            pass
        else:
            await ctx.send('Please provide a valid IGN ' + ctx.message.author.mention + "!")
            return
        tier, rank, lp = db.get_rank(response)
        elo_boost = db.determine_initial_elo(tier, rank, lp)
        if tier in restrict:
            await ctx.send(ctx.message.author.mention + " you must be Gold+ to register!\nThe inhouse system is "
                                                        "designed with competitive integrity in mind.")
            return
        # Add user to database
        c.execute(
            "INSERT INTO users (discord_id, registration_date) VALUES (?, ?)", (user_id, registration_date))
        # Add user to league 
        c.execute(
            "INSERT INTO league (player_ign, discord_id, last_played, wins, losses, elo, streak, tier, rank)"
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (player_ign, user_id, registration_date, INIT_WINS, INIT_LOSS, INIT_ELO + elo_boost, INIT_STREAK,
             tier, rank))

        db_connection.commit()
        await ctx.send(ctx.message.author.mention + " you have been registered successfully!")
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
            await ctx.send(
                ctx.message.author.mention + ", please provide a valid match number.\nEx) !match 24")
            return

        # get cursor to execute SQL commands
        c = db_connection.cursor()

        # get all entries with the given match id
        c.execute('SELECT * FROM league_info WHERE match_id = ?', (match_num,))

        # return array containing response from previous execute command
        sql_return = c.fetchall()

        if not sql_return:
            await ctx.send("Match doesn't exist!")
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

        # splitting into seperate arrays
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
        await ctx.send(embed=win_embed)
        await ctx.send(embed=lose_embed)
        return

    # Enter the queue
    @commands.command(pass_context=True,
                      name='queue',
                      help="Queues up for an inhouse game",
                      aliases=['join', 'letmein'])
    async def queue(self, ctx):
        if db.check_ban(db_connection, ctx.message.author.id):
            await ctx.send(ctx.message.author.mention + " you are currently banned from playing inhouses.", delete_after=3)
            return
        # check if user is in queue first
        for x in in_queue:
            if x.id == ctx.message.author.id:
                await ctx.send(ctx.message.author.mention + " you're already in queue!")
                return
        # Checks to see if user is in a lobby

        if not db.check_user(db_connection, ctx.message.author.id):
            await ctx.send(
                ctx.message.author.mention + ' you are not registered yet! Use !register <your ign> to join the '
                                             'inhouse system!')
        else:
            p = db.get_player(db_connection, ctx.message.author.id)
            if check_lobbies(p):
                await ctx.send(ctx.message.author.mention + " you're already in a lobby!")
                return
            if len(in_queue) >= 9:
                if not lobby1:
                    in_queue.append(p)
                    embed = start_lobby_auto(lobby1, lob1_b, lob1_r)
                    channel = self.bot.get_channel(613862942873485333)
                    await ctx.send('Match generated! Check #inhouse-lol-matches!')
                    await channel.send(embed=embed)
                    await channel.send(mention_players(lobby1), delete_after=30)
                elif not lobby2:
                    in_queue.append(p)
                    embed = start_lobby_auto(lobby2, lob2_b, lob2_r)
                    channel = self.bot.get_channel(613862942873485333)
                    await ctx.send('Match generated! Check #inhouse-lol-matches!')
                    await channel.send(embed=embed)
                    await channel.send(mention_players(lobby2), delete_after=30)
                elif not lobby3:
                    in_queue.append(p)
                    embed = start_lobby_auto(lobby3, lob3_b, lob3_r)
                    channel = self.bot.get_channel(613862942873485333)
                    await ctx.send('Match generated! Check #inhouse-lol-matches!')
                    await channel.send(embed=embed)
                    await channel.send(mention_players(lobby3), delete_after=30)
                elif not lobby4:
                    in_queue.append(p)
                    embed = start_lobby_auto(lobby4, lob4_b, lob4_r)
                    channel = self.bot.get_channel(613862942873485333)
                    await ctx.send('Match generated! Check #inhouse-lol-matches!')
                    await channel.send(embed=embed)
                    await channel.send(mention_players(lobby4), delete_after=30)
                else:
                    in_queue.append(p)
                    await ctx.send("All lobbies currently filled! Please wait!")
            else:
                in_queue.append(p)
            await ctx.send(embed=players_queued(in_queue))
        return

    # Exit the queue
    @commands.command(pass_context=True,
                      name='dequeue',
                      help="Leaves the inhouse queue",
                      aliases=['leave', 'letmeout'])
    async def dequeue(self, ctx):
        for x in in_queue:
            if x.id == ctx.message.author.id:
                in_queue.remove(x)
                await ctx.send(embed=players_queued(in_queue))
                return
        await ctx.send(ctx.message.author.mention + " you aren't in queue!")
        return

    # List the players in a specified lobby
    @commands.command(pass_context=True,
                      name="stats",
                      brief="Prints out the player stats.",
                      description="Prints out the player stats. If no mention is given then it will send the stats of "
                                  "user who sent the command.",
                      aliases=['mmr'])
    async def print_player(self, ctx):
        if len(ctx.message.mentions) == 1:
            if not db.check_user(db_connection, ctx.message.mentions[0].id):
                await ctx.send(ctx.message.author.mention + " the user mentioned does not exist in the system!")
                return
            else:
                p = db.get_player(db_connection, ctx.message.mentions[0].id)
                embed = player_embed(p)
                await ctx.send(embed=embed)
                return
        else:
            if db.check_user(db_connection, ctx.message.author.id):
                p = db.get_player(db_connection, ctx.message.author.id)
                embed = player_embed(p)
                await ctx.send(embed=embed)
                return
            else:
                await ctx.send(ctx.message.author.mention + " you're not in our system!")
                return

    @commands.command(pass_context=True,
                      help="Shows this help menu!")
    async def help(self, ctx):
        help_msg = "```\nInhouse Bot Help Manual:\n" \
                   "Admin:\n" \
                   "    elo       Change elo for a user. !elo @user 5\n" \
                   "    forceend  End the given lobby number. !forceend 1\n" \
                   "    remove    Remove specified player from the queue. !remove @user\n" \
                   "    clearq    Clears out the queue entirely. !clearq\n" \
                   "    ban       Bans a player. Do !unban to unban. !ban @user.\n" \
                   "Captain:\n" \
                   "    report    Report match results. Must be a captain of a team. !report w/l\n" \
                   "User:\n" \
                   "    dequeue   Leaves the inhouse queue. !dequeue\n" \
                   "    match     Reports matches stored in database. !match #\n" \
                   "    opgg      Generates an op.gg link of the ign. Allows only one ign. !opgg Omnix\n" \
                   "    queue     Queues up for an inhouse game. !queue\n" \
                   "    rank      Prints the top 50 players in the community. !rank/!ranks\n" \
                   "    register  Syncs your League account with our database. !register Omnix\n" \
                   "    stats     Prints out the player stats. !stats @user\n" \
                   "    updateign Updates your ign! !updateign Omnix\n" \
                   "    help      Shows this message !help```"
        return await ctx.send(help_msg)

    # Print the inhouse leaderboard
    @commands.command(pass_context=True,
                      name="rank",
                      help="Prints the top 50 players in the community.",
                      aliases=['leaderboard', 'ranks', 'rankings'])
    async def leaderboard(self, ctx):
        player_list = db.get_leaderboard(db_connection)
        embed = leaderboard_embed(player_list)
        await ctx.send(embed=embed)
        return

    # Print the inhouse leaderboard
    @commands.command(pass_context=True,
                      help="Generates an op.gg link of the ign. Allows only one ign.",
                      name='opgg')
    async def opgg(self, ctx):
        try:
            command, player_ign = ctx.message.content.split(" ", 1)
        except ValueError:
            await ctx.send(ctx.message.author.mention + " need an ign!")
            return
        name_list = player_ign.split()
        temp = ""
        for word in name_list:
            temp += word + "+"
        embed = discord.Embed(title="OP.GG LINK GENERATOR", colour=discord.Colour(0xffffff),
                              description="[CLICK ON ME FOR OP.GG!](https://na.op.gg/summoner/userName=" + temp + ")",
                              timestamp=datetime.datetime.today())
        await ctx.send(embed=embed)

    # update league name
    @commands.command(pass_context=True,
                      help="Updates your ign!",
                      name='updateign')
    async def update_ign(self, ctx):
        # temp disabled
        # check that they have an account in the database
        if db.check_league(db_connection, ctx.message.author.id):
            pass
        else:
            await ctx.send('You must register your account ' + ctx.message.author.mention + "!")
            return

        # get user Discord ID
        user_id = ctx.message.author.id

        try:
            command, player_ign = ctx.message.content.split(" ", 1)
        except ValueError:
            await ctx.send(
                ctx.message.author.mention + ", please provide a valid League IGN after the command.\nEx) "
                                             "!updateign Stahp Doing That")
            return

        # validate IGN
        if db.validate_player(db.check_rank(player_ign)):
            pass
        else:
            await ctx.send('Please provide a valid IGN ' + ctx.message.author.mention + "!")
            return

        # update IGN

        # get cursor to execute SQL commands
        c = db_connection.cursor()

        c.execute(''' UPDATE league SET player_ign = ? WHERE discord_id = ?''', (player_ign, user_id))
        db_connection.commit()

        await ctx.send(ctx.message.author.mention + " your IGN has been successfully updated!")
        return


def setup(bot):
    bot.add_cog(User(bot))

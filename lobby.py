from inhousebot import *


# This just sorts the players in lobby by elo and alternates in placing them in the teams.
# Highest player gets put on blue team. Next highest red team. Next highest blue and so on.
def start_lobby_auto(lobby, team1, team2):
    for x in range(10):
        lobby.append(in_queue.pop(0))
    lobby.sort(key=lambda x: x.elo, reverse=True)
    place_players(lobby, team1, team2)
    return lobby_embed(team1, team2)


# This is just the test method
def start_lobby_test(queue, lobby, team1, team2):
    for x in range(4):
        lobby.append(queue.pop(0))
    lobby.sort(key=lambda x: x.elo, reverse=True)
    place_players(lobby, team1, team2)
    return lobby_embed(team1, team2)


# Puts the players onto teams
def place_players(lobby, team1, team2):
    for x in range(int(len(lobby)/2)):
        team1.append(lobby[x * 2])
        team2.append(lobby[x * 2 + 1])
    return


# This tells the players what the teams are and what the team op.gg's
def lobby_embed(team1, team2):
    t1_names = []
    t2_names = []
    t1_opgg = []
    t2_opgg = []
    for p in team1:
        t1_names.append(p.ign + "\n")
        t1_opgg.append("".join(p.ign.split()) + "%2C")
    for p in team2:
        t2_names.append(p.ign + "\n")
        t2_opgg.append("".join(p.ign.split()) + "%2C")
    embed = discord.Embed(title="Match Created!", colour=discord.Colour(0xffffff),
                          description="Match generated! Captains are responsible for making lobbies and inviting everyone!",
                          timestamp=datetime.datetime.today())
    embed.add_field(name="Team 1 AVG ELO: " + str(math.floor(calc_avg_elo(team2))),
                    value=''.join(t1_names),
                    inline=True)
    embed.add_field(name="Team 2 AVG ELO: " + str(math.floor(calc_avg_elo(team1))),
                    value=''.join(t2_names),
                    inline=True)
    embed.add_field(name="OP.GG LINKS", value="[TEAM 1 OP.GG](https://na.op.gg/multi/query=" + ''.join(t1_opgg) +
                                              ")\n[TEAM 2 OP.GG](https://na.op.gg/multi/query=" + ''.join(t2_opgg) + ")")
    return embed


def pending_lobby_embed(lobby):
    if len(lobby) == 0:
        return 0
    t1_names = []
    t1_opgg = []
    for p in lobby:
        t1_names.append(p.ign + "\n")
        t1_opgg.append("".join(p.ign.split()) + "%2C")

    embed = discord.Embed(title="========== LOBBY 1 ==========", colour=discord.Colour(0xffffff),
                          timestamp=datetime.datetime.today())
    embed.add_field(name="Players:",
                    value=''.join(t1_names),
                    inline=True)
    return embed


# This generates an embed of elo changes
def post_embed(team, change, score, match_id):
    t_names = []
    elo = []
    for p in team:
        t_names.append(p.ign + "\n")
    if score:
        for x in change:
            elo.append("+" + str(x) + "\n")
    else:
        for x in change:
            elo.append(str(x) + "\n")
    if score:
        embed = discord.Embed(title="__Match " + str(match_id) + " Results:__",
                              colour=discord.Colour(0x20ea65),
                              timestamp=datetime.datetime.today())
        embed.add_field(name="Winning Team",
                        value=''.join(t_names),
                        inline=True)
        embed.add_field(name="ELO GAINED",
                        value=''.join(elo),
                        inline=True)
    else:
        embed = discord.Embed(title="__Match " + str(match_id) + " Results:__",
                              colour=discord.Colour(0xff0000),
                              timestamp=datetime.datetime.today())
        embed.add_field(name="Losing Team",
                        value=''.join(t_names),
                        inline=True)
        embed.add_field(name="ELO LOST",
                        value=''.join(elo),
                        inline=True)
    return embed


def leaderboard_embed(players):
    desc_string = "```css\nRank IGN               Elo  W  L``````fix\n"
    # turn SQL object into iterable list, sorted by ELO
    charts = list(players)
    charts.sort(key=lambda x: x[2], reverse=False)

    # iterate through that list
    for i in range(len(charts)):
        player = charts.pop()
        desc_string += str(i + 1) + ". " + str(player[3])
        for j in range(0, 20 - len(str(player[3]))):
            desc_string += " "
        desc_string += str(player[2]) + " " + str(player[4]) + "  " + str(player[5]) + "\n"
        if i == 20:
            break

    desc_string += "\n```"
    embed = discord.Embed(title=":trophy:     Top 20 Leaderboards     :trophy:", colour=discord.Colour(0xffcd00),
                          description=desc_string,
                          timestamp=datetime.datetime.today())
    return embed


# Returns an embed of a player
def player_embed(p):
    embed = discord.Embed(
        title="INHOUSE STATS FOR:",
        description=str(p.ign),
        colour=discord.Colour(0xffcd00),
        timestamp=datetime.datetime.today())

    embed.add_field(name="ELO: ",
                    value=str(p.elo),
                    inline=True)

    embed.add_field(name="WINS: ",
                    value=str(p.wins),
                    inline=True)

    embed.add_field(name="LOSSES: ",
                    value=str(p.losses),
                    inline=True)

    embed.add_field(name="STREAK: ",
                    value=str(p.streak),
                    inline=True)
    return embed


# Calculates the avg elo of a team
def calc_avg_elo(team):
    if len(team) == 0:
        return 0
    total = 0
    for player in team:
        total += player.elo
    return total / len(team)


# This adjusts the elo of the teams
def adjust_teams(win_t, lose_t, match_id):
    win_t_elo = calc_avg_elo(win_t)
    lose_t_elo = calc_avg_elo(lose_t)
    lose_change = []
    win_change = []
    for p in win_t:
        win_change.append(str(elo_change(p, lose_t_elo, 1, match_id)))
    for p in lose_t:
        lose_change.append(str(elo_change(p, win_t_elo, 0, match_id)))
    win_embed = post_embed(win_t, win_change, 1, match_id)
    lose_embed = post_embed(lose_t, lose_change, 0, match_id)
    return win_embed, lose_embed


# This calculates elo change
def elo_change(player, enemy_avg, score, match_id):
    expected = 1 / (1 + 10 ** ((enemy_avg - player.elo)/140))
    change = 0
    # Loss
    if score == 0:
        change = math.floor(30 * (0 - expected))
        player.elo = player.elo + change
        player.losses = player.losses + 1
        if player.streak >= 0:
            player.streak = -1
        else:
            player.streak = player.streak - 1
    # Win
    else:
        change = math.floor(30 * (1 - expected))
        player.elo = player.elo + change
        player.wins = player.wins + 1
        if player.streak <= 0:
            player.streak = 1
        else:
            player.streak = player.streak + 1
    db.update_match_history(db_connection, player.id, match_id, change)
    return change

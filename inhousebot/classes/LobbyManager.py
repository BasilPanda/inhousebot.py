"""
LobbyManager.py manages lobbies created from the Lobby class
"""
# System imports
import math
from collections import deque
from datetime import datetime
from typing import List

# External Imports
import discord

# Local Imports
import Lobby
import Player
from inhousebot.database import Database as db # pylint: disable=import-error
from inhousebot.inhousebot import log, db_connection # pylint: disable=import-error

class LobbyManager:
    """
    LobbyManager.py manages lobbies...
    """
    @staticmethod
    def start_lobby_auto(lobby: Lobby, in_queue: deque):
        """
        This just sorts the players in lobby by elo and alternates in placing them in the teams.
        Highest player gets put on blue team. Next highest red team. Next highest blue and so on.
        """
        lobby.players = [in_queue.popleft() for i in range(10)]
        log.debug(f"Lobby created! Length: {len(lobby.players)}")

        lobby.players.sort(key=lambda x: x.elo, reverse=True)
        LobbyManager.place_players(lobby)
        return LobbyManager.lobby_embed(lobby)

    @staticmethod
    def start_lobby_test(lobby:Lobby, test_queue:deque):
        """
        Test function for starting a lobby
        """
        lobby.players = [test_queue.popleft() for player in range(2)]
        log.debug(f"Lobby created! Length: {len(lobby.players)}")

        lobby.players.sort(key=lambda x: x.elo, reverse=True)
        LobbyManager.place_players(lobby)
        return LobbyManager.lobby_embed(lobby)

    @staticmethod
    def place_players(lobby: Lobby):
        """
        Puts players into teams
        """
        for x in range(int(len(lobby)/2)):
            lobby.leftSide.append(lobby[x * 2])
            lobby.rightSide.append(lobby[x * 2 + 1])
        return

    @staticmethod
    def lobby_embed(lobby: Lobby):
        """
        This tells the players what the teams are and what the team op.gg's
        """
        t1_names = []
        t2_names = []
        t1_opgg = []
        t2_opgg = []
        for p in lobby.leftSide:
            t1_names.append(p.ign + "\n")
            t1_opgg.append("".join(p.ign.split()) + "%2C")
        for p in lobby.rightSide:
            t2_names.append(p.ign + "\n")
            t2_opgg.append("".join(p.ign.split()) + "%2C")
        embed = discord.Embed(
            title="Match Created!", colour=discord.Colour(0xffffff),
            description="Match generated! Captains are responsible for making lobbies and "
                        "inviting everyone!",
            timestamp=datetime.datetime.today())
        embed.add_field(
            name=f"Team 1 AVG ELO: {math.floor(LobbyManager.calc_avg_elo(lobby.leftSide))}",
            value=''.join(t1_names),
            inline=True)
        embed.add_field(
            name=f"Team 2 AVG ELO: {math.floor(LobbyManager.calc_avg_elo(lobby.rightSide))}",
            value=''.join(t2_names),
            inline=True)
        embed.add_field(
            name="OP.GG LINKS", 
            value="[TEAM 1 OP.GG](https://na.op.gg/multi/query=" + ''.join(t1_opgg) +
                ")\n[TEAM 2 OP.GG](https://na.op.gg/multi/query=" + ''.join(t2_opgg) + ")")
        return embed

    @staticmethod
    def players_queued(in_queue: deque):
        """
        This generates an embed of players in queue.
        """
        t1_names = []
        for p in in_queue:
            t1_names.append(p.ign + "\n")

        embed = discord.Embed(
            title=f"Players Queued: {len(in_queue)}",
            colour=discord.Colour(0xffffff),
            timestamp=datetime.datetime.today())
        if t1_names:
            embed.add_field(
                name="Players:",
                value=''.join(t1_names),
                inline=True)
        return embed

    @staticmethod
    def players_draft_embed(lobby: Lobby):
        """
        This generates an embed of players left in lobby draft and what players are where.
        """
        t1_names = []
        team1_names = []
        team2_names = []
        if lobby:
            for p in lobby:
                t1_names.append(p.ign + "\n")
        for p in lobby.leftSide:
            team1_names.append(p.ign + "\n")
        for p in lobby.rightSide:
            team2_names.append(p.ign + "\n")

        embed = discord.Embed(
            title=f"Players left: {len(lobby)}",
            colour=discord.Colour(0xffffff),
            timestamp=datetime.datetime.today())
        if t1_names:
            embed.add_field(
                name="Players left to be chosen:",
                value=''.join(t1_names),
                inline=True)
        if lobby.leftSide:
            embed.add_field(
                name="Team 1:",
                value=''.join(team1_names),
                inline=True)
        if lobby.rightSide:
            embed.add_field(
                name="Team 2:",
                value=''.join(team2_names),
                inline=True)
        return embed


    @staticmethod
    def post_embed(team, change, score, match_id):
        """
        This generates an embed of elo changes
        """
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
            embed = discord.Embed(
                title="__Match " + str(match_id) + " Results:__",
                colour=discord.Colour(0x20ea65),
                timestamp=datetime.datetime.today())
            embed.add_field(
                name="Winning Team",
                value=''.join(t_names),
                inline=True)
            embed.add_field(
                name="ELO GAINED",
                value=''.join(elo),
                inline=True)
        else:
            embed = discord.Embed(
                title=f"__Match {match_id} Results:__",
                colour=discord.Colour(0xff0000),
                timestamp=datetime.datetime.today())
            embed.add_field(
                name="Losing Team",
                value=''.join(t_names),
                inline=True)
            embed.add_field(
                name="ELO LOST",
                value=''.join(elo),
                inline=True)
        return embed

    @staticmethod
    def leaderboard_embed(players):
        """
        Leaderboard Embed
        """
        desc_string = "```css\nRank IGN               Elo  W  L``````fix\n"
        # turn SQL object into iterable list, sorted by ELO
        charts = list(players)
        charts.sort(key=lambda x: x[2], reverse=False)

        # iterate through that list
        for i in range(len(charts)):
            player = charts.pop()
            desc_string += str(i + 1) + ". " + str(player[3])
            if i > 8:
                x = 1
            for j in range(0, 20 - x - len(str(player[3]))):
                del j
                desc_string += " "
            space = " "
            if len(str(player[4])) == 2:
                space = ""
            desc_string += str(player[2]) + " " + str(player[4]) + space + str(player[5]) + "\n"
            if i == 49:
                break

        desc_string += "\n```"
        embed = discord.Embed(
            title=":trophy:     Top 50 Leaderboards     :trophy:", 
            colour=discord.Colour(0xffcd00),
            description=desc_string,
            timestamp=datetime.datetime.today())
        return embed

    @staticmethod
    def player_embed(p):
        """
        Returns an embed of a player
        """
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

    @staticmethod
    def calc_avg_elo(team):
        """
        Calculates the avg elo of a team
        """
        if len(team) == 0:
            return 0
        total = 0
        for player in team:
            total += player.elo
        return total / len(team)

    @staticmethod
    def adjust_teams(win_t, lose_t, match_id):
        """
        This adjusts the elo of the teams
        """
        win_t_elo = LobbyManager.calc_avg_elo(win_t)
        lose_t_elo = LobbyManager.calc_avg_elo(lose_t)
        lose_change = []
        win_change = []
        for p in win_t:
            win_change.append(str(LobbyManager.elo_change(p, lose_t_elo, win_t_elo, 1, match_id)))
        for p in lose_t:
            lose_change.append(str(LobbyManager.elo_change(p, win_t_elo, lose_t_elo, 0, match_id)))
        win_embed = LobbyManager.post_embed(win_t, win_change, 1, match_id)
        lose_embed = LobbyManager.post_embed(lose_t, lose_change, 0, match_id)
        return win_embed, lose_embed

    @staticmethod
    def elo_change(player, enemy_avg, team_avg, score, match_id):
        """
        Calculates elo change
        """
        # Loss
        if score == 0:
            if player.elo > team_avg:
                expected = 1 / (1 + 10 ** ((enemy_avg - team_avg) / 120))
            else:
                expected = 1 / (1 + 10 ** ((enemy_avg - player.elo) / 120))
            change = math.floor(30 * (0 - expected))
            player.elo = player.elo + change/2
            player.losses = player.losses + 1
            if player.streak >= 0:
                player.streak = -1
            else:
                player.streak = player.streak - 1
        # Win
        else:
            if player.elo > team_avg:
                expected = 1 / (1 + 10 ** ((enemy_avg - team_avg) / 120))
            else:
                expected = 1 / (1 + 10 ** ((enemy_avg - player.elo) / 120))
            change = math.floor(30 * (1 - expected))
            player.elo = player.elo + change*2
            player.wins = player.wins + 1
            if player.streak <= 0:
                player.streak = 1
            else:
                player.streak = player.streak + 1
        db.update_match_history(db_connection, player.id, match_id, change)
        return change

    @staticmethod
    def in_lobby(player: Player, lobbies: List):
        """
        Gets the lobby a player is in. Returns None if not in any lobby.
        """
        for lobby in lobbies:
            for p in lobby:
                if player.id == p.id:
                    return lobby
        return None

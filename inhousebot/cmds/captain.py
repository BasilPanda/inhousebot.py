from inhousebot.lobby import *
from discord.ext import commands
from inhousebot.inhousebot import *

class Captain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Allows only captains to report match results
    @commands.command(pass_context=True,
                      name='report',
                      help="Report match results. Must be a captain of a team.",
                      aliases=['r'])
    async def report(self, ctx):
        # Checks to see if any lobbies are running first
        if not lobby1 and not lobby2 and not lobby3 and not lobby4:
            await ctx.send(ctx.message.author.mention + ', there are no lobbies running!')
            return

        lobby_num = is_captain(ctx.message.author.id)
        # Checks to see if the user reporting is a team captain
        if lobby_num == 0:
            await ctx.send(ctx.message.author.mention + ', only captains can report!')
            return
        try:
            command, result = ctx.message.content.split(" ", 1)
        except ValueError:
            await ctx.send(ctx.message.author.mention + ', please provide a match result!\nEx) '
                                                        '!report win or !report loss')
            return
        # Handling erroneous parameters
        if result.lower() not in lose_arr and result.lower() not in win_arr:
            await ctx.send(ctx.message.author.mention + ', please provide a correctly formatted match result!\nEx) '
                                                        '!report win or !report loss')
        channel = self.bot.get_channel(613862942873485333)
        if lobby_num == 1:
            if lobby1:
                win_embed, lose_embed = create_embeds(ctx, lob1_b, lob1_r, result)
                await channel.send(embed=win_embed)
                await channel.send(embed=lose_embed)
                lobby1.clear()
            else:
                await ctx.send(ctx.message.author.mention + ', that lobby isn\'t active!')
        elif lobby_num == 2:
            if lobby2:
                win_embed, lose_embed = create_embeds(ctx, lob2_b, lob2_r, result)
                await channel.send(embed=win_embed)
                await channel.send(embed=lose_embed)
                lobby2.clear()
            else:
                await ctx.send(ctx.message.author.mention + ', that lobby isn\'t active!')
        elif lobby_num == 3:
            if lobby1:
                win_embed, lose_embed = create_embeds(ctx, lob3_b, lob3_r, result)
                await channel.send(embed=win_embed)
                await channel.send(embed=lose_embed)
                lobby3.clear()
            else:
                await ctx.send(ctx.message.author.mention + ', that lobby isn\'t active!')
        elif lobby_num == 4:
            if lobby4:
                win_embed, lose_embed = create_embeds(ctx, lob4_b, lob4_r, result)
                await channel.send(embed=win_embed)
                await channel.send(embed=lose_embed)
                lobby4.clear()
            else:
                await ctx.send(ctx.message.author.mention + ', that lobby isn\'t active!')
        return


def create_embeds(ctx, team1, team2, result):
    # Create match ID
    match_id = db.create_match(db_connection)
    if ctx.message.author.id == team1[0].id and result.lower() in lose_arr:
        win_embed, lose_embed = adjust_teams(team2, team1, match_id)
    elif ctx.message.author.id == team1[0].id and result.lower() in win_arr:
        win_embed, lose_embed = adjust_teams(team1, team2, match_id)
    elif ctx.message.author.id == team2[0].id and result.lower() in lose_arr:
        win_embed, lose_embed = adjust_teams(team1, team2, match_id)
    elif ctx.message.author.id == team2[0].id and result.lower() in win_arr:
        win_embed, lose_embed = adjust_teams(team2, team1, match_id)
    for x in range(len(team1)):
        db.update_player(db_connection, team1[x])
        print(team1[x].to_list())
        db.update_player(db_connection, team2[x])
        print(team2[x].to_list())
    team1.clear()
    team2.clear()
    return win_embed, lose_embed


def setup(bot):
    bot.add_cog(Captain(bot))

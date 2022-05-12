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
            await self.bot.say(ctx.message.author.mention + ", there are no lobbies running!")
            return

        lobby_num = is_captain(ctx.message.author.id)
        # Checks to see if the user reporting is a team captain
        if lobby_num == 0:
            await self.bot.say(ctx.message.author.mention + ", only captains can report!")
            return
        try:
            command, result = ctx.message.content.split(" ", 1)
        except ValueError:
            await self.bot.say(ctx.message.author.mention + ", please provide a match result!\nEx) "
                                                            "$report win or %report loss")
            return
        # Handling erroneous parameters
        if result.lower() not in lose_arr and result.lower() not in win_arr:
            await self.bot.say(ctx.message.author.mention + ", please provide a correctly formatted match result!\nEx) "
                                                            "$report win or %report loss")
        if lobby_num == 1:
            if lobby1:
                # Create match ID 
                match_id = db.create_match(db_connection)
                if ctx.message.author.id == str(lob1_b[0].id) and result.lower() in lose_arr:
                    win_embed, lose_embed = adjust_teams(lob1_r, lob1_b, match_id)
                elif ctx.message.author.id == str(lob1_b[0].id) and result.lower() in win_arr:
                    win_embed, lose_embed = adjust_teams(lob1_b, lob1_r, match_id)
                elif ctx.message.author.id == str(lob1_r[0].id) and result.lower() in lose_arr:
                    win_embed, lose_embed = adjust_teams(lob1_b, lob1_r, match_id)
                elif ctx.message.author.id == str(lob1_r[0].id) and result.lower() in win_arr:
                    win_embed, lose_embed = adjust_teams(lob1_r, lob1_b, match_id)                
                for x in range(len(lob1_b)):
                    db.update_player(db_connection, lob1_b[x])
                    db.update_player(db_connection, lob1_r[x])
                lob1_b.clear()
                lob1_r.clear()
                await self.bot.say(embed=win_embed)
                await self.bot.say(embed=lose_embed)
                lobby1.clear()
            else:
                await self.bot.say(ctx.message.author.mention + ", that lobby isn't active!")

    # ADD OTHER LOBBIES


def setup(bot):
    bot.add_cog(Captain(bot))

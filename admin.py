from inhousebot import *


# All admin related commands go here
class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # removes player from the queue
    @commands.command(pass_context=True,
                      help="Remove specified player from queue.",
                      name='remove')
    async def remove_player(self, ctx):
        await ctx.message.delete()
        if ctx.message.author.id not in config.admins:
            await ctx.send(ctx.message.author.mention + ", you're not an admin!", delete_after=3)
            return

        if len(ctx.message.mentions) != 1:
            await ctx.send(ctx.message.author.mention + ", you need to @ the user you wish to remove from "
                                                        "queue!", delete_after=3)
            return
        else:
            for p in in_queue:
                if p.id == ctx.message.mentions[0].id:
                    in_queue.remove(p)
                    await ctx.send(ctx.message.author.mention + ", you have removed " +
                                   ctx.message.mentions[0].mention + " from the queue.")
                    await ctx.send("Players Queued: " + str(len(in_queue)))
                    return
        await ctx.send(ctx.message.author.mention + ", the player is currently not in queue...", delete_after=3)
        return

    # Admin end a lobby
    @commands.command(pass_context=True,
                      help="End the current lobby.",
                      name='forceend')
    async def force_end(self, ctx):
        await ctx.message.delete()
        if ctx.message.author.id not in config.admins:
            await ctx.send(ctx.message.author.mention + ", you're not an admin!", delete_after=3)
            return
        try:
            command, lobby_num = ctx.message.content.split(" ", 1)
        except ValueError:
            await ctx.send("Need a number argument!", delete_after=3)
            return
        if not 0 < int(lobby_num) < 5:
            await ctx.send("There's only 4 numbered lobbies!", delete_after=3)
            return
        if lobby_num == 1:
            lobby1.clear()
            lob1_b.clear()
            lob1_r.clear()
        elif lobby_num == 2:
            lobby2.clear()
            lob2_b.clear()
            lob2_r.clear()
        elif lobby_num == 3:
            lobby3.clear()
            lob3_b.clear()
            lob3_r.clear()
        elif lobby_num == 4:
            lobby4.clear()
            lob4_b.clear()
            lob4_r.clear()
        await ctx.send("Lobby " + lobby_num + " cleared!")
        return

    # Admin update elo
    @commands.command(pass_context=True,
                      help="Change elo for a user.",
                      name='elo')
    async def force_elo(self, ctx):
        if ctx.message.author.id not in config.admins:
            await ctx.send(ctx.message.author.mention + ", you're not an admin!")
            return
        try:
            command, mention, elo = ctx.message.content.split(" ", 2)
        except ValueError:
            await ctx.send("Need a mention and number argument!")
            return
        if len(ctx.message.mentions) == 1:
            if db.check_user(db_connection, ctx.message.mentions[0].id):
                p = db.get_player(db_connection, ctx.message.mentions[0].id)
                p.elo = int(elo)
                db.update_elo(db_connection, ctx.message.mentions[0].id, p.elo)
                await ctx.send("Elo updated!")
                return
            else:
                await ctx.send("User doesn't exist in database!")
                return

    # Clears out entire queue
    @commands.command(pass_context=True,
                      help="Clears out entire queue.",
                      name='clearq')
    async def clear_queue(self, ctx):
        await ctx.message.delete()
        if ctx.message.author.id not in config.admins:
            await ctx.send(ctx.message.author.mention + ", you're not an admin!", delete_after=3)
            return

        if in_queue:
            for i in range(len(in_queue)):
                in_queue.pop(0)
            await ctx.send(ctx.message.author.mention + ", the queue has been cleared!")
        else:
            await ctx.send(ctx.message.author.mention + ", there's no one in queue...", delete_after=3)
        return

    # Bans a player
    @commands.command(pass_context=True,
                      help="Bans a player.",
                      name='ban')
    async def ban(self, ctx):
        await ctx.message.delete()
        if ctx.message.author.id not in config.admins:
            await ctx.send(ctx.message.author.mention + ", you're not an admin!", delete_after=6)
            return
        if len(ctx.message.mentions) != 1:
            await ctx.send(ctx.message.author.mention + ", you need to @ the user you wish to remove from "
                                                        "queue!", delete_after=6)
            return
        if not db.check_ban(db_connection, ctx.message.mentions[0].id):
            db.ban_player(db_connection, ctx.message.mentions[0].id)
            await ctx.send(ctx.message.author.mention + ", player banned.", delete_after=12)
        else:
            await ctx.send(ctx.message.author.mention + ", that player is already banned.", delete_after=6)
        return

    # Unbans a player
    @commands.command(pass_context=True,
                      help="Unbans a player.",
                      name='unban')
    async def unban(self, ctx):
        await ctx.message.delete()
        if ctx.message.author.id not in config.admins:
            await ctx.send(ctx.message.author.mention + ", you're not an admin!", delete_after=6)
            return
        if len(ctx.message.mentions) != 1:
            await ctx.send(ctx.message.author.mention + ", you need to @ the user you wish to remove from "
                                                        "queue!", delete_after=6)
            return
        if db.check_ban(db_connection, ctx.message.mentions[0].id):
            db.unban_player(db_connection, ctx.message.mentions[0].id)
            await ctx.send(ctx.message.author.mention + ", player unbanned.", delete_after=12)
        else:
            await ctx.send(ctx.message.author.mention + ", that player isn't banned.", delete_after=6)
        return

    # Checks a players rank.
    @commands.command(pass_context=True,
                      help="Checks player rank.",
                      name='check')
    async def check_rank(self, ctx):
        if ctx.message.author.id not in config.admins:
            await ctx.send(ctx.message.author.mention + ", you're not an admin!", delete_after=6)
            return
        try:
            command, name = ctx.message.content.split(" ", 1)
        except ValueError:
            await ctx.send("Need a mention argument!")
            return
        db.check_rank(name)
        return


def setup(bot):
    bot.add_cog(Admin(bot))

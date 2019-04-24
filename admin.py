import asyncio
from inhousebot import *


# All admin related commands go here
class Admin:
    def __init__(self, bot):
        self.bot = bot

    # removes player from the queue
    @commands.command(pass_context=True,
                      help="Remove specified player from your lobby.",
                      name='remove')
    async def remove_player(self, ctx):
        await self.bot.delete_message(ctx.message)
        if ctx.message.author.id not in config.admins:
            msg = await self.bot.say(ctx.message.author.mention + ", you're not an admin!")
            await asyncio.sleep(3)
            await self.bot.delete_message(msg)
            return

        if len(ctx.message.mentions) != 1:
            msg = await self.bot.say(ctx.message.author.mention + ", you need to @ the user you wish to remove from "
                                                                  "queue!")
            await asyncio.sleep(3)
            await self.bot.delete_message(msg)
            return
        else:
            for p in in_queue:
                if str(p.id) == ctx.message.mentions[0].id:
                    in_queue.remove(p)
                    await self.bot.say(ctx.message.author.mention + ", you have removed " +
                                       ctx.message.mentions[0].mention + " from the queue.")
                    await self.bot.say("Players Queued: " + str(len(in_queue)))
                    return
        msg = await self.bot.say(ctx.message.author.mention + ", the player is currently not in queue...")
        await asyncio.sleep(3)
        await self.bot.delete_message(msg)
        return

    # Admin end a lobby
    @commands.command(pass_context=True,
                      help="End the current lobby.",
                      name='forceend')
    async def force_end(self, ctx):
        await self.bot.delete_message(ctx.message)
        if ctx.message.author.id not in config.admins:
            msg = await self.bot.say(ctx.message.author.mention + ", you're not an admin!")
            await asyncio.sleep(3)
            await self.bot.delete_message(msg)
            return
        try:
            command, lobby_num = ctx.message.content.split(" ", 1)
        except ValueError:
            msg = await self.bot.say("Need a number argument!")
            await asyncio.sleep(3)
            await self.bot.delete_message(msg)
            return
        if not 0 < lobby_num < 5:
            msg = await self.bot.say("There's only 4 numbered lobbies!")
            await asyncio.sleep(3)
            await self.bot.delete_message(msg)
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
        await self.bot.say("Lobby " + lobby_num + " cleared!")
        return


def setup(bot):
    bot.add_cog(Admin(bot))

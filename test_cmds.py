from lobby import *


class Test:
    def __init__(self, bot):
        self.bot = bot

    # Exit the queue
    @commands.command(pass_context=True,
                      name='testdq',
                      help="Leaves the test queue",
                      aliases=['tdq'])
    async def dequeue_test(self, ctx):
        for x in test_queue:
            if str(x.id) == ctx.message.author.id:
                test_queue.remove(x)
                await self.bot.say("Players in Test Queue: " + str(len(test_queue)))
                return
        await self.bot.say(ctx.message.author.mention + " you aren't in queue!")
        return

    # Enter the queue
    @commands.command(pass_context=True,
                      name='testqueue',
                      help="Enter the test queue",
                      aliases=['tq'])
    async def queue_test(self, ctx):
        # check if user is in queue first
        for x in in_queue:
            if str(x.id) == ctx.message.author.id:
                await self.bot.say(ctx.message.author.mention + " you're already in queue!")
                return

        if not db.check_user(db_connection, ctx.message.author.id):
            await self.bot.say('You are not registered yet! Use $register <your ign> to join the inhouse system!')
        else:
            if len(test_queue) >= 3:
                if not lobby4:
                    test_queue.append(db.get_player(db_connection, ctx.message.author.id))
                    embed = start_lobby_test(test_queue, lobby4, lob4_b, lob4_r)
                    await self.bot.say(embed=embed)
                else:
                    test_queue.append(db.get_player(db_connection, ctx.message.author.id))
                    await self.bot.say("All lobbies currently filled! Please wait!")
            else:
                test_queue.append(db.get_player(db_connection, ctx.message.author.id))
            await self.bot.say("Players in Test Queue: " + str(len(test_queue)))
        return


def setup(bot):
    bot.add_cog(Test(bot))


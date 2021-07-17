"""This is a cog for a discord.py bot.
It adds the purge command to the bot that can be used to delete messages

Commands:
    purge <n>               Delete the last n messages
    purge_user <User> [n]   Delete all messages of <User> within the last
                            [n] Messages (Default 100)

Only users that have an admin role can use the commands.
"""

import typing
import discord
embed_color = 0x738ADB
from discord.ext import commands
from discord import User, errors


class Purge(commands.Cog, name='Purge'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return commands.has_permissions(manage_messages=True)

    # ----------------------------------------------
    # Function Group to clear channel of messages
    # ----------------------------------------------
    @commands.command(
        name="purge",
        description="A command which purges the channel it is called in",
        usage="[amount]",
    )
    async def purge(
        self, ctx,
        num_messages: int,
    ):
        channel = ctx.message.channel
        await ctx.message.delete()
        await channel.purge(limit=num_messages, check=None, before=None)
        embed=discord.Embed(title='Chat Purged!', description=f'{num_messages} message(s) has been deleted by {ctx.author.mention}', color=embed_color)
        embed.set_footer(text='This message will delete in 5 seconds...')
        await ctx.send(embed=embed, delete_after=5)
        return True

    @commands.command(
        name='purge_until',
        description="A command which purges the until a specific message",
        usuage="[message id]",
        hidden=False,
    )
    async def purge_until(
        self, ctx,
        message_id: int,
    ):
        channel = ctx.message.channel
        try:
            message = await channel.fetch_message(message_id)
        except errors.NotFound:
            await ctx.send("Message could not be found in this channel")
            return

        await ctx.message.delete()
        await channel.purge(after=message)
        embed = discord.Embed(title='Chat Purged!',
                              description=f'Messages has been deleted by {ctx.author.mention}',
                              color=embed_color)
        embed.set_footer(text='This message will delete in 5 seconds...')
        await ctx.send(embed=embed, delete_after=5)
        return True

    @commands.command(
        name='purge_user',
        description="A command which purges a specific user's message",
        usuage="<user> [amount]",
        aliases=['purgeu', 'purgeuser'],
    )
    async def purge_user(
        self, ctx,
        user: User,
        num_messages: typing.Optional[int] = 100,
    ):
        channel = ctx.message.channel

        def check(msg):
            return msg.author.id == user.id

        await ctx.message.delete()
        await channel.purge(limit=num_messages, check=check, before=None)
        embed = discord.Embed(title='Chat Purged!',
                              description=f'{num_messages} message(s) has been deleted by {ctx.author.mention}',
                              color=embed_color)
        embed.set_footer(text='This message will delete in 5 seconds...')
        await ctx.send(embed=embed, delete_after=5)
        
    @commands.command(
        name='purge_all',
        description='A command which purges an entire channel',
    )
    async def purge_all(self, ctx):
        channel = ctx.message.channel
        await ctx.message.delete()
        await channel.purge(limit=9999999, check=None, before=None)
        embed=discord.Embed(title='Chat Purged!', description=f'All messages have been deleted by {ctx.author.mention}', color=embed_color)
        embed.set_footer(text='This message will delete in 5 seconds...')
        await ctx.send(embed=embed, delete_after=5)
    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(title='**❌ Error**', description='Incorrect command usuage.\n Correct usuage: `.warn @user [reason]`, example: `.warn {self.bot.user} testing`', color=embed_color)
            await ctx.send(embed=embed, delete_after=5)
        
def setup(bot):
    bot.add_cog(Purge(bot))
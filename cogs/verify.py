import discord
from discord.ext import commands
from discord.utils import get
import asyncio
embed_color = 0x738ADB

class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(pass_context=True)
    async def verify(self, ctx):
        verify_role = get(ctx.guild.roles, name='Members')
        if ctx.channel.id == 853801190612271138 and ctx.author.roles != 853500656446341130:
            await ctx.author.add_roles(verify_role)
            embed = discord.Embed(title='Welcome!', description='You\'ve successfully verified into the server.', color=embed_color)
            await ctx.author.send(embed=embed)
            await asyncio.sleep(3)
            await ctx.message.delete()

        elif ctx.channel.id != 853801190612271138:
            embed=discord.Embed(title="**❌ Error**", description='You\'re already verified!', color=embed_color)
            
            await ctx.send(embed=embed, delete_after=3)
            await asyncio.sleep(3)
            await ctx.message.delete()

def setup(bot):
    bot.add_cog(verify(bot))

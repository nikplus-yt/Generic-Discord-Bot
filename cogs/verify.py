import discord
from discord.ext import commands
from discord.utils import get
import asyncio
embed_color = 0x738ADB
verify_channel = 853801190612271138
class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(pass_context=True)
    async def agree(self, ctx):
        verify_role = get(ctx.guild.roles, name='Peasants')
        if ctx.channel.id == verify_channel and ctx.author.roles != 853500656446341130:
            await ctx.author.add_roles(verify_role)
            embed = discord.Embed(title=f'Welcome {ctx.author}!', description=f'**<a:PenguinWalk:854189751556243496> Welcome to {ctx.guild.name}! <a:PenguinWalk:854189751556243496>**\n\n Welcome {ctx.author.mention}! Please make sure to read the <#853500885207482418> and get your roles here <#855632692166393868>!', color=embed_color)
            await ctx.author.send(embed=embed)
            await asyncio.sleep(1)
            await ctx.message.delete()

        elif ctx.channel.id != verify_channel:
            embed=discord.Embed(title="**❌ Error**", description='You\'re already verified!', color=embed_color)
            
            await ctx.send(embed=embed, delete_after=3)
            await asyncio.sleep(3)
            await ctx.message.delete()

def setup(bot):
    bot.add_cog(verify(bot))

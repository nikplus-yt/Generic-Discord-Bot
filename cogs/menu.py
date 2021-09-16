import discord
import DiscordUtils
from discord.ext import commands
from discord_components import *

class Menus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    async def menu1(self, ctx):
        await ctx.send("Just select the roles you're interested in below.", components = [Select(placeholder="Make a selection"), options=[SelectOption(label="Dead Chat Ping", value='A')SelectOption(label="test", value='B')]])
        interaction = await self.bot.wait_for("select_option", check = lambda i: i.component[0].value == "A")
        await interaction.respond(content = f"You have selected `{interaction.component[0].label}`")






        
def setup(bot):
    bot.add_cog(Menus(bot))

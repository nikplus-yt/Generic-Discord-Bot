import discord
import DiscordUtils
from discord.ext import commands
from discord_components import *

class Menus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='select-test')
        async def menu1(self, ctx):
            await ctx.send("Just select the roles you're interested in below."
            components=
            [Select(placeholder="Make a selection",
                                options=[
                                    SelectOption(
                                        label="Dead Chat Ping",
                                        value="option1",
                                        emoji="�☠" # you can use discord.Parti ... emoji to use a custom one (i dont know what its called)
                                    ),
                                    SelectOption(
                                        label="Giveaway Ping",
                                        value="option2",
                                        emoji="�🎁" # you can use discord.Parti ... emoji to use a custom one (i dont know what its called)
                                    ),
                                    SelectOption(
                                        label="Event Ping",
                                        value="option3",
                                        emoji="�📅" # you can use discord.Parti ... emoji to use a custom one (i dont know what its called)
                                    ),
                                ])]
                                ) 
            e1 = Embed(title="Role Given!", description="You were given the <@&854187482806616064> role")
            e2 = Embed(title="Role Given!", description="You were given the <@&854187970386853889> role")
            e3 = Embed(title="Role Given", description="You were given the <@&854186313829580832> role")

            while True:
                try: # try except is not required but i would recommend using it
                    event = await self.bot.wait_for("select_option", check=None)

                    label = event.component[0].label

                    if label == "Dead Chat Ping":
                        await event.respond(
                            type=InteractionType.ChannelMessageWithSource,
                            ephemeral=True, # we dont want to spam someone
                            embed=e1
                        )

                    elif label == "Giveaway Ping":
                        await event.respond(
                            type=InteractionType.ChannelMessageWithSource,
                            ephemeral=True, # we dont want to spam someone
                            embed=e2
                        )
                    elif label == "Event Ping":
                        await event.respond(
                            type=InteractionType.ChannelMessageWithSource,
                            ephemeral=False, # we dont want to spam
                            embed=e3 
                        )


                except discord.NotFound:
                    print("error.") # since this is bugged, we cant send an error. this error raises every time you use a select, but if this is fixed you can send what ever you want.





        
def setup(bot):
    bot.add_cog(Menus(bot))

import re
import random
import asyncio

import discord
from discord.ext import commands

from utils.util import GetMessage

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


def convert(argument):
    args = argument.lower()
    matches = re.findall(time_regex, args)
    time = 0
    for key, value in matches:
        try:
            time += time_dict[value] * float(key)
        except KeyError:
            raise commands.BadArgument(
                f"{value} is an invalid time key! h|m|s|d are valid arguments"
            )
        except ValueError:
            raise commands.BadArgument(f"{key} is not a number!")
    return round(time)


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="giveaway",
        description="Create a full giveaway!",
        aliases=['gstart']
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def giveaway(self, ctx):
        embed = discord.Embed(title='Giveaway Setup!',description="Lets start this giveaway, answer the questions I ask and we shall proceed.",color=0xADD8E6)
        await ctx.send(embed=embed)

        questionList = [
            ["What channel should it be in?", "Mention the channel"],
            ["How long should this giveaway last?", "`d|h|m|s`"],
            ["What are you giving away?", "I.E. Discord Nitro"]
        ]
        answers = {}

        for i, question in enumerate(questionList):
            answer = await GetMessage(self.bot, ctx, question[0], question[1])

            if not answer:
                embed = discord.Embed(title="Error!",description="You failed to answer, please answer quicker next time.",color=0xb5180d)
                await ctx.send(embed=embed)
                return

            answers[i] = answer

        embed = discord.Embed(name="Giveaway content", color=0x0d8eb5)
        for key, value in answers.items():
            embed.add_field(name=f"Question: `{questionList[key][0]}`", value=f"Answer: `{value}`", inline=False)

        m = await ctx.send("Are these all valid?", embed=embed)
        await m.add_reaction("✅")
        await m.add_reaction("🇽")

        try:
            reaction, member = await self.bot.wait_for(
                "reaction_add",
                timeout=60,
                check=lambda reaction, user: user == ctx.author
                and reaction.message.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            embed = discord.Embed(title="Error!", description="Confirmation Failure. Please try again.",
                                  color=0xb5180d)
            await ctx.send(embed=embed)
            return

        if str(reaction.emoji) not in ["✅", "🇽"] or str(reaction.emoji) == "🇽":
            await ctx.send("Cancelling giveaway!")
            return

        channelId = re.findall(r"[0-9]+", answers[0])[0]
        channel = self.bot.get_channel(int(channelId))

        time = convert(answers[1])

        giveawayEmbed = discord.Embed(
            title="__**Giveaway**!__",
            description=f'{ctx.author.mention} is giving away **{answers[2]}**!\n\n React with 🎉 to enter!',
            color=0xc98308
        )
        if time >= 3600 and time < 86400:

            new_time = f'{str(time / 3600)} hours'
        elif time >= 86400:

            new_time = f'{str(time / 86400)} days'
        elif time < 3600 and time >= 60:

            new_time = f'{str(time / 60)} minutes'
        else:
            new_time = f'{time} seconds'
        giveawayEmbed.set_footer(text=f"This giveaway ends {new_time} from this message.")
        giveawayMessage = await channel.send(embed=giveawayEmbed)
        await giveawayMessage.add_reaction("🎉")

        await asyncio.sleep(time)

        message = await channel.fetch_message(giveawayMessage.id)
        users = await message.reactions[0].users().flatten()
        users.pop(users.index(ctx.guild.me))
        users.pop(users.index(ctx.author))

        if len(users) == 0:
            embed = discord.Embed(title='So sad', description="No winner was decided")
            await channel.send(embed=embed)
            return

        winner = random.choice(users)

        await channel.send(
            f"**Congrats {winner.mention}, you won {answers[2]}!**\nPlease contact {ctx.author.mention} about your prize.")

    @commands.command(
        name='reroll',
        description='Reroll a giveaway\'s winner.')

    @commands.has_permissions(manage_guild=True)
    async def reroll(self, ctx, channel: discord.TextChannel, id_: int):
        try:
            new_msg = await channel.fetch_message(id_)
        except:
            embed = discord.Embed(title="Error!", description=f"The message ID `{channel}` was entered incorrectly",
                                  color=0xdb040f)
            await ctx.send(embed=embed)
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))

        winner = random.choice(users)
        await channel.send(f'Congratulations! the new winner is {winner.mention}; you won the reroll!')

def setup(bot):
    bot.add_cog(Giveaway(bot))

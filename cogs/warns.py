import discord
from discord.ext import commands
import asyncio
from utils.util import Pag
embed_red=discord.Colour.red()

class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        if member.id in [ctx.author.id, self.bot.user.id]:
            embed = discord.Embed(title='**❌ Error**', description='You can\'t warn yourself!', color=discord.Colour.red())
            embed.set_footer(text='This message will delete in 5 seconds...')
            return await ctx.send(embed=embed, delete_after=5)
            await asyncio.sleep(5)
            await ctx.message.delete()
            
        
        current_warn_count = len(
            await self.bot.warns.find_many_by_custom(
                {
                    "user_id": member.id,
                    "guild_id": member.guild.id
                }
            )
        ) + 1
        
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id, "number": current_warn_count}
        warn_data = {"reason": reason, "timestamp": ctx.message.created_at, "warned_by": ctx.author.id}
        
        await self.bot.warns.upsert_custom(warn_filter, warn_data)
        
        embed = discord.Embed(title=f"**You've been warned in {ctx.guild.name}**",description=f"**Reason**\n{reason}\n**Moderator**\n{ctx.author.mention}",colour=0xE2F706,timestamp=ctx.message.created_at)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=f"Warns: {current_warn_count}")
        
        try:
            await member.send(embed=embed)
            embed = discord.Embed(
                title="User Warned!",
                description=f"**{member}** was warned by **{ctx.message.author}**!",
                color=0x30f706
            )
            embed.add_field(
                name="Reason:",
                value=reason
            )
            await ctx.send(embed=embed, delete_after=5)
            await asyncio.sleep(5)
            await ctx.message.delete()
            embed=discord.Embed(title='warn case', description=f'**Offender**: {member} | {member.mention}\n **Reason:** {reason}\n **Moderator:** {ctx.author} | {ctx.author.mention}', color=embed_red)
            embed.set_footer(text=f'Offender ID: {member.id} | Moderator ID: {ctx.author.id}')
            channel = self.bot.get_channel(865809356032573450)
            await channel.send(embed=embed)
        except discord.HTTPException:
            await ctx.send(member.mention, embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx, member: discord.Member):
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id}
        warns = await self.bot.warns.find_many_by_custom(warn_filter)
        
        if not bool(warns):
            embed=discord.Embed(title='**❌ Error**', description=f"Couldn't find any warns for: `{member.display_name}`", color=embed_red)
            return await ctx.send(embed=embed)
        
        warns = sorted(warns, key=lambda x: x["number"])
        
        pages = []
        for warn in warns:
            description = f"""
            Warn Number: `{warn['number']}`
            Warn Reason: `{warn['reason']}`
            Warned By: <@{warn['warned_by']}>
            Warn Date: {warn['timestamp'].strftime("%I:%M %p %B %d, %Y")}
            """
            pages.append(description)
        
        await Pag(
            title=f"Warns for `{member.display_name}`",
            colour=0xCE2029,
            entries=pages,
            length=1
        ).start(ctx)

    @commands.command(aliases=["delwarn", "dw"])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def deletewarn(self, ctx, member: discord.Member, warn: int = None):
        """Delete a warn / all warns from a given member"""
        filter_dict = {"user_id": member.id, "guild_id": member.guild.id}
        if warn:
            filter_dict["number"] = warn

        was_deleted = await self.bot.warns.delete_by_custom(filter_dict)
        if was_deleted and was_deleted.acknowledged:
            if warn:
                embed=discord.Embed(title='warn delete case', description=f'**Offender**: {member} | {member.mention}\n**Moderator:** {ctx.author} | {ctx.author.mention}', color=embed_red)
                embed.set_footer(text=f'Offender ID: {member.id} | Moderator ID: {ctx.author.id}')
                channel = self.bot.get_channel(865809356032573450)
                await channel.send(embed=embed)
                embed=discord.Embed(title="Warn Deleted", description=f"I deleted warn number `{warn}` for `{member.display_name}`", color=0x30f706)
                return await ctx.send(embed=embed)
            embed=discord.Embed(title="Warns Deleted", description=f"I deleted `{was_deleted.deleted_count}` warns for `{member.display_name}`", color=0x30f706)
            return await ctx.send(embed=embed)
            

        await ctx.send(f"I could not find any warns for `{member.display_name}` to delete matching your input")


def setup(bot):
    bot.add_cog(Warns(bot))

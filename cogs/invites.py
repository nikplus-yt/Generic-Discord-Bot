import discord
import DiscordUtils
from discord.ext import commands

# Requires: pip install DiscordUtils


class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
        await self.tracker.cache_invites()

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.tracker.update_invite_cache(invite)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.tracker.remove_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.tracker.update_guild_cache(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.tracker.remove_guild_cache(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        inviter = await self.tracker.fetch_inviter(member)
        data = await self.bot.invites.find_by_custom(
            {"guild_id": member.guild.id, "inviter_id": inviter.id}
        )
        if data is None:
            data = {
                "guild_id": member.guild.id,
                "inviter_id": inviter.id,
                "count": 0,
                "invited_users": []
            }

        data["count"] += 1
        data["invited_users"].append(member.id)
        await self.bot.invites.upsert_custom(
            {"guild_id": member.guild.id, "inviter_id": inviter.id}, data
        )

        channel = discord.utils.get(member.guild.text_channels, name="welcome")
        embed = discord.Embed(
            title=f"<a:PenguinWalk:854189751556243496> Welcome {member.display_name} <a:PenguinWalk:854189751556243496>!",
            description=f"Welcome {member.mention}! Please read the <#853500885207482418> and get your roles here <#855632692166393868>\n\nInvited by: {inviter.mention}\nInvites: {data['count']}", color=0xc71c10,
            timestamp=member.joined_at,
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Invites(bot))

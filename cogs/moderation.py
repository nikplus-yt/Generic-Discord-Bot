import re
import datetime
from copy import deepcopy
import random
import asyncio
import discord
import string
embed_color = 0x738ADB
from discord.ext import commands, tasks
from dateutil.relativedelta import relativedelta

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

staff_list = str([633025959221788676, 853437257800089610, 853808640506462208])

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
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


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_task = self.check_current_mutes.start()

    def cog_unload(self):
        self.mute_task.cancel()

    @tasks.loop(minutes=5)
    async def check_current_mutes(self):
        currentTime = datetime.datetime.now()
        mutes = deepcopy(self.bot.muted_users)
        for key, value in mutes.items():
            if value['muteDuration'] is None:
                continue

            unmuteTime = value['mutedAt'] + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                guild = self.bot.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])

                role = discord.utils.get(guild.roles, name="Muted")
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Unmuted: {member.display_name}")

                await self.bot.mutes.delete(member.id)
                try:
                    self.bot.muted_users.pop(member.id)
                except KeyError:
                    pass

    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bot.wait_until_ready()

    @commands.command(
        name='mute',
        description="Mutes a given user for x time!",
        ussage='<user> [time] [reason]'
    )
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, time: TimeConverter=None, *, reason=None):
        if member.id in staff_list:
            embed = discord.Embed(title='**❌ Error**', description='You can\'t mute yourself!', color=discord.Colour.red())
            embed.set_footer(text='This message will delete in 5 seconds...')
            return await ctx.send(embed=embed, delete_after=5)
            await asyncio.sleep(5)
            await ctx.message.delete()

        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        try:
            if self.bot.muted_users[member.id]:
                await ctx.send("This user is already muted")
                return
        except KeyError:
            pass

        data = {
            '_id': member.id,
            'mutedAt': datetime.datetime.now(),
            'muteDuration': time or None,
            'mutedBy': ctx.author.id,
            'guildId': ctx.guild.id,
        }
        await self.bot.mutes.upsert(data)
        self.bot.muted_users[member.id] = data

        await member.add_roles(role)
        embed = discord.Embed(title="muted!", description=f"{member.mention} has been muted ", colour=embed_color)
        embed.add_field(name="time left for the mute:", value=f"{time}s", inline=False)
        await ctx.send(embed=embed, delete_after=5)
        await asyncio.sleep(5)
        await ctx.message.delete()
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        embed = discord.Embed(title=f"**You've been muted in {ctx.guild.name}**",description=f"**Duration:**\n{hours} hours, {minutes} minutes, and {seconds} seconds\n**Reason**\n {reason}\n**Moderator**\n{ctx.author.mention}", colour=0xE2F706,timestamp=ctx.message.created_at)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await member.send(embed=embed)
        if not time:
            embed=discord.Embed(title='mute case', description=f'**Offender**: {member} | {member.mention}\n **Reason:** {reason} \n  **Moderator:** {ctx.author} | {ctx.author.mention}', color=embed_color)
            embed.set_footer(text=f'Offender ID: {member.id} | Moderator ID: {ctx.author.id}')
            channel = self.bot.get_channel(865809356032573450)
            await channel.send(embed=embed)
        else:
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            if int(hours):
                embed=discord.Embed(title='mute case', description=f'**Offender**: {member} | {member.mention}\n **Reason:** {reason} \n**Moderator:** {ctx.author} | {ctx.author.mention}', color=embed_color)
                embed.set_footer(text=f'Offender ID: {member.id} | Moderator ID: {ctx.author.id}')
                embed.add_field(name="time left for the mute:", value=f"{hours} hours, {minutes} minutes and {seconds} seconds", inline=False)
                channel = self.bot.get_channel(865809356032573450)
                await channel.send(embed=embed)
            elif int(minutes):
                embed=discord.Embed(title='mute case', description=f'**Offender**: {member} | {member.mention}\n **Reason:** {reason} \n**Moderator:** {ctx.author} | {ctx.author.mention}', color=embed_color)
                embed.set_footer(text=f'Offender ID: {member.id} | Moderator ID: {ctx.author.id}')
                embed.add_field(name="time left for the mute:", value=f"{minutes} minutes and {seconds} seconds", inline=False)
                channel = self.bot.get_channel(865809356032573450)
                await channel.send(embed=embed)
            elif int(seconds):
                embed=discord.Embed(title='mute case', description=f'**Offender**: {member} | {member.mention}\n **Reason:** {reason} \n**Moderator:** {ctx.author} | {ctx.author.mention}', color=embed_color)
                embed.set_footer(text=f'Offender ID: {member.id} | Moderator ID: {ctx.author.id}')
                embed.add_field(name="time left for the mute:", value=f"{seconds} seconds", inline=False)
                channel = self.bot.get_channel(865809356032573450)
                await channel.send(embed=embed)
                

        if time and time < 300:
            await asyncio.sleep(time)

            if role in member.roles:
                await member.remove_roles(role)
                minutes, seconds = divmod(time, 60)
                hours, minutes = divmod(minutes, 60)
                embed=discord.Embed(title='unmute case', description=f'**Offender**: {member} | {member.mention}\n**Duration:** {hours} hours, {minutes} minutes, and {seconds} seconds\n**Reason:** `Time expired`\n **Moderator:** {ctx.author} | {ctx.author.mention}', color=embed_color)
                embed.set_footer(text=f'Offender ID: {member.id} | Moderator ID: {ctx.author.id}')
                channel = self.bot.get_channel(865809356032573450)
                await channel.send(embed=embed)

            await self.bot.mutes.delete(member.id)
            try:
                self.bot.muted_users.pop(member.id)
            except KeyError:
                pass
                
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass
        if isinstance(error, commands.BadArgument):
            await ctx.send(error)
        else:
            error = getattr(error, 'original', error)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            
    @commands.command(
        name='unmute',
        description="Unmuted a member!",
        usage='<user> [reason]'
    )
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        await self.bot.mutes.delete(member.id)
        try:
            self.bot.muted_users.pop(member.id)
        except KeyError:
            pass

        if role not in member.roles:
            await ctx.send("This member is not muted.")
            return

        await member.remove_roles(role)
        embed = discord.Embed(title=f'User Unmuted', description=f"{member.mention} was unmuted by {ctx.author.mention}.",color=embed_color)
        await ctx.send(embed=embed, delete_after=5)
        await asyncio.sleep(5)
        await ctx.message.delete()
        embed=discord.Embed(title='unmute case', description=f'**Offender**: {member} | {member.mention}\n**Reason:** {reason}\n **Moderator:** {ctx.author} | {ctx.author.mention}', color=embed_color)
        embed.set_footer(text=f'Offender ID: {member.id} | Moderator ID: {ctx.author.id}')
        channel = self.bot.get_channel(865809356032573450)
        await channel.send(embed=embed)

    @commands.command(
        name="kick",
        description="A command which kicks a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member.id in staff_list:
            embed = discord.Embed(title='**❌ Error**', description='You can\'t kick a staff member!', color=discord.Colour.red())
            embed.set_footer(text='This message will delete in 5 seconds...')
            await ctx.send(embed=embed)
            
        else:
            await ctx.send('test')
            # await member.kick(reason=reason)
        if reason == None:
            embed = discord.Embed(title="User kicked successfully",description=f'{member.mention} was kicked  by {ctx.author.mention}!\n No reason added.',color=embed_color)
            await ctx.send(embed=embed, delete_after=5)
            await asyncio.sleep(5)
            await ctx.message.delete()
            channel = self.client.get_channel(865809356032573450)
            await channel.send(embed=embed)
        else:
            embed = discord.Embed(title="User kicked successfully", description=f'{member.mention} was kicked by {ctx.author.mention}!\n User was kicked for: `{reason}`', color=embed_color)
            await ctx.send(embed=embed, delete_after=5)
            await asyncio.sleep(5)
            await ctx.message.delete()
            channel = self.client.get_channel(865809356032573450)
            await channel.send(embed=embed)

    @commands.command(
        name="ban",
        description="A command which bans a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        if reason == None:
            embed = discord.Embed(title="User banned successfully",description=f'{member.mention} was banned by {ctx.author.mention}!\n User was banned for no reason.',color=embed_color)
            await ctx.send(embed=embed, delete_after=5)
            embed=discord.Embed(title='ban case', description=f'**Offender**: {member} | {member.mention}\n **Reason:** None specified\n **Moderator:** {ctx.author} | {ctx.author.mention}', color=embed_color)
            embed.set_footer(text=f'Offender ID: {member.id} | Moderator ID: {ctx.author.id}')
            await asyncio.sleep(5)
            await ctx.message.delete()
            channel = self.bot.get_channel(865809356032573450)
            await channel.send(embed=embed)
        else:
            embed = discord.Embed(title="User banned successfully", description=f'{member.mention} was banned by {ctx.author.mention}!\n User was banned for: `{reason}`', color=embed_color)
            await ctx.send(embed=embed, delete_after=5)
            await asyncio.sleep(5)
            await ctx.message.delete()
            channel = self.bot.get_channel(865809356032573450)
            await channel.send(embed=embed)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="**❌ Error**",description=f"You don't have correct permissions to run `ban`.", color=embed_color)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title='No user was banned',description=f'Incorrect command usuage.\n Correct usuage: `>ban @user [reason]`, example: `>ban {self.bot.user} testing`', color=embed_color)
            await ctx.send(embed=embed)


    @commands.command(
        name="unban",
        description="A command which unbans a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, member, *, reason=None):
        member = await self.bot.fetch_user(int(member))
        await ctx.guild.unban(member, reason=reason)
        embed = discord.Embed(title=f'**{user}** has been unbanned', description=f"{user} was unbanned.",color=embed_color)
        embed.set_footer(text=f'{user} was unbanned by {ctx.author}')
        await ctx.send(embed=embed, delete_after=5)
        await asyncio.sleep(5)
        await ctx.message.delete()
        channel = self.client.get_channel(865809356032573450)
        await channel.send(embed=embed)
    @commands.command(
        name="moderate",
        description="This moderates a user's nickname",
        usage="<user>",
    )
    @commands.has_permissions(manage_messages=True)
    async def moderate(self, ctx, member:discord.Member):
        N = 7
        mod_nick = ''.join(random.choices(string.ascii_lowercase + string.digits, k = N))
        await member.edit(nick="Moderated Nickname " + mod_nick)
        await ctx.send(f'{member} nickname has successfully changed to `\'{mod_nick}\'`')
        await member.send('Your Discord username/nickname was changed due to it violating the rules. Please make sure that moderators can ping you without using your id.\n Please contact the staff team to have it changed.')
        
    @moderate.error
    async def nick(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="**❌ Error**",description=f"You don't have correct permissions to run `moderate`.", color=embed_color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            embed = discord.Embed(title="**❌ Error**",description=f"error:\n `{error}`",color=embed_color)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Moderation(bot))

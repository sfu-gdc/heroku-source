import asyncio
import discord
from discord.ext import commands, tasks

from myconstants import bulbasaur_green, gameboy_yellow
import myconstants

# For the notification roles

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx): # This was inside '__init__' before
        await ctx.send("pong!\n{}ms".format(round(self.bot.latency * 1000)))

    @commands.command(aliases=['colour'])
    async def color(self, ctx):
        # If the user is part of notification squad then they have a wider variety of possible colours.
        message = await ctx.send("Choose a colour by reacting to this message")
        if "Notification Squad" in [y.name for y in ctx.message.author.roles]:
            color_emote_list = myconstants.extended_color_emote_list 
            color_emote_name_list = myconstants.extended_color_emote_name_list
            color_list = myconstants.extended_color_list
        else:
            color_emote_list = myconstants.color_emote_list 
            color_emote_name_list = myconstants.color_emote_name_list
            color_list = myconstants.color_list

        # doesn't feel like parallel...
        # https://stackoverflow.com/questions/53324404/delay-when-adding-emojis-to-a-message-on-discord-python
        futures = [message.add_reaction(emoji=emoji) for emoji in color_emote_list]
        await asyncio.gather(*futures)

        # TODO: check for reactions here.

        check = lambda reaction, user: user == ctx.message.author and str(reaction.emoji) in color_emote_list

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
            user = ctx.message.author

            if reaction.emoji.name in color_emote_name_list:
                index_of = color_emote_name_list.index(reaction.emoji.name)
                await remove_all_color_roles(user)
                await add_role(user, ctx.guild.roles, color_list[index_of])
                
        except asyncio.TimeoutError:
            await ctx.send("You took too long to pick a colour, try `,color` again if you'd like to claim one.")
        else:
            await ctx.send("Enjoy {}!".format(reaction.emoji))

        # TODO: remove the emotes from the message.

    @commands.command()
    async def notify(self, ctx, activate):
        val = str(activate).lower()
        if val == "true":
            await ctx.send("You will now recieve notifications")
            await add_role(ctx.message.author, ctx.guild.roles, "Notification Squad")

            message = await ctx.send("Choose a colour by reacting to this message")
            await message.add_reaction(emoji=bulbasaur_green)
            await message.add_reaction(emoji=gameboy_yellow)
            is_bulbasaur = lambda reaction, user: user == ctx.message.author and str(reaction.emoji) == bulbasaur_green
            is_gameboy = lambda reaction, user: user == ctx.message.author and str(reaction.emoji) == gameboy_yellow
            check = lambda r, u: is_gameboy(r,u) or is_bulbasaur(r,u)

            # wait for reponse or timeout
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
                user = ctx.message.author

                if reaction.emoji.name == "bulbasaur":
                    await remove_all_color_roles(user)
                    await add_role(user, ctx.guild.roles, "Bulbasaur Green")
                elif reaction.emoji.name == "gameboy":
                    await remove_all_color_roles(user)
                    await add_role(user, ctx.guild.roles, "Gameboy Yellow")
                    
            except asyncio.TimeoutError:
                await ctx.send("You took too long to pick a colour, try again if you'd like to claim one.")
            else:
                await ctx.send("Enjoy {}!".format(reaction.emoji))

        elif val == "false":
            # remove roles if possible
            user = ctx.message.author

            await remove_role(user, "Bulbasaur Green")
            await remove_role(user, "Gameboy Yellow")
            await remove_role(user, "Notification Squad")

            await ctx.send("You will no longer recieve notifications")
        else:
            await ctx.send("Error: please type `,notify true` or `,notify false`")
    
    @notify.error
    async def notify_error(self, ctx, error):
        print("error: {}".format(repr(error)))
        await ctx.send("Oops, something went wrong. Call the function like this: `,notify true`")
    
    
# --------------------------------------------------------------------------- #

async def remove_all_color_roles(user):
    for role in myconstants.extended_color_list:
        if role in [y.name for y in user.roles]:
            await remove_role(user, role)

async def remove_role(user, name):
    r = discord.utils.get(user.roles, name=name)
    if r: await user.remove_roles(r)

async def add_role(user, roles, name):
    r = discord.utils.get(roles, name=name)
    if r: await user.add_roles(r)


# --------------------------------------------------------------------------- #

def setup(bot):
    bot.add_cog(Roles(bot))
import os, random

import discord
from discord.ext import commands, tasks

from myconstants import greetings, mynames

# --------------------------------------------------------------------------- #
# Bot Init

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=',', intents=intents)
bot.remove_command('help')

# --------------------------------------------------------------------------- #
# Cog Loading

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

bot.load_extension("cogs.roles")

# --------------------------------------------------------------------------- #
# Misc Setup

@bot.command()
async def help(ctx):
    help_str = "Commands:\n\t,notify <true|false>\n\t,ping\n\n"
    help_str += "Interaction:\n\tTry saying hi to CubeBot"
    await ctx.send("```{}```".format(help_str))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="conway's game of life"))
    print("CubeBot is ready")

@bot.event
async def on_member_join(member):
    # TODO: give basic role?
    pass

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    val = await bot.process_commands(message)
    print("did process cmd: {}".format(val))

    cleaned_msg = message.content.replace("!", "").replace("?", "").lower().strip()
    ends_with_myname = cleaned_msg.endswith(mynames[0].lower()) or cleaned_msg.endswith(mynames[1].lower())
    if ends_with_myname and len(cleaned_msg) > 9 and cleaned_msg[:-8].strip() in greetings:
        end_char = "!" if random.randint(0, 1) == 1 else ""
        await message.channel.send("{} {}{}".format(random.choice(greetings), message.author.mention, end_char))
    elif "linux" in cleaned_msg and not "gnu linux" in cleaned_msg:
        await message.channel.send("you mean GNU linux, right?")    

# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    print("about to run bot")
    bot.run(os.environ['TOKEN']) # this token is set in the heroku environment
else:
    print("ran the file in lint mode, exiting gracefully.")
import discord
from discord import Embed, Color, Member, Intents, Activity, ActivityType, ApplicationContext, DiscordException, Guild
from discord.ext import commands, tasks
from discord.errors import Forbidden
from discord.ext.commands import errors, Context

import json
import logging
from dotenv import load_dotenv
from os import listdir, getenv

from customs import time_now, get_parameter, MyBot


load_dotenv()
bot = MyBot()


@bot.slash_command(name="ping")
async def ping(ctx: ApplicationContext):
    latency = round(bot.latency * 1000)
    await ctx.respond(f"🏓 Pong! ({latency}ms)", ephemeral=True)

    limit = get_parameter('ping_limit')

    if latency > limit:
        bot.log_action(txt=f"Bot ping is at {latency} ms", level=30)


@bot.slash_command(name="reload", description="Redémarre une cog", brief="Reload a cog", hidden=True, guild_ids=bot.debug_guilds)
@commands.is_owner()
async def reload(ctx: ApplicationContext, extension=None):
    if not extension:
        for filename_ in listdir('./cogs'):
            if filename_.endswith('.py'):
                try:
                    bot.reload_extension(f"cogs.{filename_[:-3]}")
                    await ctx.respond(f"> Cog `{filename_[:-3]}` successfully reloaded", ephemeral=True)

                except discord.ExtensionNotLoaded:
                    bot.load_extension(f"cogs.{filename_[:-3]}")
                    await ctx.respond(f"> Cog `{filename_[:-3]}` successfully loaded", ephemeral=True)

    else:
        try:
            bot.reload_extension(f"cogs.{extension}")
            await ctx.respond(f"> Cog `{extension}` successfully reloaded", ephemeral=True)

        except discord.ExtensionNotLoaded:
            try:
                bot.load_extension(f"cogs.{extension}")
                await ctx.respond(f"> Cog `{extension}` successfully loaded", ephemeral=True)

            except discord.ExtensionNotFound:
                await ctx.respond(f"> Cog `{extension}` not found", ephemeral=True)


@bot.slash_command(name="load", description="Charge une cog", brief="Load a cog", hidden=True, guild_ids=bot.debug_guilds)
@commands.is_owner()
async def load(ctx: ApplicationContext, extension=None):
    try:
        bot.load_extension(f"cogs.{extension}")
        await ctx.respond(f"> Cog `{extension}` successfully loaded", ephemeral=True)

    except discord.ExtensionNotFound:
        await ctx.respond(f"> Cog `{extension}` not found", ephemeral=True)

    except discord.ExtensionAlreadyLoaded:
        await ctx.respond(f"> Cog `{extension}` already loaded", ephemeral=True)


@bot.slash_command(name="unload", description="Décharge une cog", brief="Unload a cog", hidden=True, guild_ids=bot.debug_guilds)
@commands.is_owner()
async def unload(ctx: ApplicationContext, extension=None):
    try:
        bot.unload_extension(f"cogs.{extension}")
        await ctx.respond(f"> Cog `{extension}` successfully unloaded", ephemeral=True)

    except discord.ExtensionNotLoaded:
        await ctx.respond(f"> Cog `{extension}` not loaded", ephemeral=True)

    except discord.ExtensionNotFound:
        await ctx.respond(f"> Cog `{extension}` not found", ephemeral=True)


if __name__ == '__main__':
    bot.run(getenv("BOT_TOKEN"))
    bot.log_action(txt="[BOT] Bot closed.")

import discord
from discord import Embed, Color, Member, Intents, Activity, ActivityType, ApplicationContext, DiscordException, \
    Guild, AutocompleteContext
from discord.ext import commands, tasks
from discord.errors import Forbidden
from discord.ext.commands import errors, Context

from pytz import timezone
from datetime import datetime

import logging
from dotenv import load_dotenv
from os import listdir, getenv
from json import load as json_load


def time_now():
    return datetime.now(tz=timezone("Europe/Paris"))


def get_parameter(param):
    with open("json/bot_config.json", "r", encoding="utf-8") as config_file:
        config = json_load(config_file)

    if isinstance(param, str):
        try:
            return config[param]
        except KeyError:
            return "KeyError"

    else:
        items = []
        for item in param:
            if item in config:
                items.append(config[item])
            else:
                items.append(None)
        return items


class MyBot(commands.Bot):
    def __init__(self):
        intents = Intents.all()

        with open("json/bot_config.json", "r", encoding="utf-8") as config_file:
            config = json_load(config_file)

        super().__init__(
            command_prefix=commands.when_mentioned_or(config['prefix']),
            intents=intents,
            owner_ids=config['owners'],
            debug_servers=config['debug_server_list'],
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                users=True,
                roles=False,
                replied_user=True
            ),
            slash_commands=True,
            activity=Activity(name="Starting ..."),
            status=discord.Status.idle
        )

        self.ignored_errors = [errors.CommandNotFound, errors.NoPrivateMessage, TimeoutError]

        self.log_file_name = time_now().strftime('%Y-%m-%d_%H.%M.%S')
        logging.basicConfig(filename=f"logs/{self.log_file_name}.log", level=0)
        logging.addLevelName(25, "CMD")
        logging.addLevelName(26, "MAILBOT")

        self.logger = logging.getLogger('bot')
        self.logmail = logging.getLogger('mailbot')
        # self.logger.handlers = [LogtailHandler(source_token=getenv("LOGTAIL_TOKEN"))]

        for filename in listdir('./cogs'):
            if filename.endswith('.py'):
                self.load_extension(f"cogs.{filename[:-3]}")

    def log_action(self, txt: str, level: int = 20, logger: logging.Logger = None):
        if logger is None:
            logger = self.logger

        logger.log(msg=txt, level=level)
        color_code = {
            20: "\033[0;34m",
            30: "\033[0;33m",
            40: "\033[7m\033[1;31m",
            50: "\033[7m\033[1;31m"
        }
        if level in color_code:
            txt = color_code[level] + txt + "\033[0m"
        print(txt)

    async def on_ready(self):
        start_msg = f"[BOT] Bot connected as {self.user}"
        self.log_action(txt=start_msg)

    async def on_guild_join(self, guild: Guild):
        text = f"Guild {guild.name} joined. [id: {guild.id}, owner: {guild.owner}|{guild.owner_id}]"
        self.log_action(text)

    async def on_application_command_completion(self, ctx: ApplicationContext):
        args = " ".join([f"[{option['name']}:{option['value']}]" for option in
                         ctx.selected_options]) if ctx.selected_options is not None else ''
        log_msg = f"{ctx.author} ({ctx.author.id}) used app_command '{ctx.command}' {args}"
        self.log_action(txt=log_msg, level=25)

    async def on_command_error(self, ctx: Context, exception: errors.CommandError):
        if exception in self.ignored_errors:
            pass

        elif isinstance(exception, errors.NotOwner):
            emb = Embed(color=Color.red(), description="You are not my owner")
            await ctx.reply(embed=emb, delete_after=5)

        elif isinstance(exception, errors.MissingRequiredArgument):
            emb = Embed(color=Color.red(), description=f"{ctx.command.brief}")
            emb.set_author(name="Please respect the following syntax :")
            await ctx.reply(embed=emb)

        else:
            self.log_action(txt=f"Unhandled error occurred ({type(exception)})", level=50)

    async def on_application_command_error(self, ctx: ApplicationContext, exception: errors.CommandError):
        if exception in self.ignored_errors:
            return

        if isinstance(exception, errors.NotOwner):
            emb = Embed(color=Color.red(), description="command.owner_only")

        elif isinstance(exception, errors.CommandOnCooldown):
            emb = Embed(color=Color.red(), description="command.on_cooldown")

        elif isinstance(exception, Forbidden):
            emb = Embed(color=Color.red(), description="command.missing_permission")

        else:
            emb = Embed(color=Color.red(), description="commands.unexpected_error")
            self.log_action(txt=f"Unhandled error occurred ({type(exception)}) : {exception}", level=50)
            # raise exception  # used when debugging

        await ctx.respond(embed=emb, ephemeral=True)


async def config_key_autocomplete(ctx: AutocompleteContext):
    with open("json/server_config.json", "r", encoding="utf-8") as config_file:
        config = json_load(config_file)

    return [key for key in config if ctx.options['parameter'] in key]

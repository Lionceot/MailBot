from discord import Embed, Color, Message, ApplicationContext, option, DMChannel
from discord.ext import commands
from discord.commands import SlashCommandGroup

from json import load as json_load, dump as json_dump

from customs import MyBot, config_key_autocomplete, time_now


class MailCog(commands.Cog):

    def __init__(self, bot_: MyBot):
        self.bot = bot_
        self.shop_items = None

    @commands.Cog.listener()
    async def on_ready(self):
        log_msg = "[COG] 'MailCog' has been loaded"
        self.bot.log_action(txt=log_msg)

    config_group = SlashCommandGroup("config", "Commands related to bot configuration.")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if isinstance(message.channel, DMChannel):
            if not message.author.bot:

                with open("json/server_config.json", "r", encoding="utf-8") as s_file:
                    config = json_load(s_file)

                if config['server_id'] is None:
                    self.bot.log_action("No value for `server_id`", 50, self.bot.logmail)
                    return

                if config['staff_channel_id'] is None:
                    self.bot.log_action("No value for `staff_channel_id`", 50, self.bot.logmail)
                    return

                if config['emergency_contact'] is None:
                    self.bot.log_action("No value for `emergency_contact`", 50, self.bot.logmail)
                    return

                guild = self.bot.get_guild(config['server_id'])

                if guild is None:
                    self.bot.log_action("Value for `server_id` is invalid.", 50, self.bot.logmail)
                    return

                staff_channel = guild.get_channel(config['staff_channel_id'])

                if message.author in guild.members:
                    if staff_channel is None:
                        rep_emb = Embed(color=Color.red(), description="Something went wrong and staff has been warned."
                                                                       " Please try again later.")
                        rep_emb.set_author(name="Error !")

                        emergency_contact = self.bot.get_user(config['emergency_contact'])
                        if emergency_contact is not None:
                            emer_emb = Embed(color=Color.red(), description="The `staff_channel` parameter is invalid.",
                                             timestamp=time_now())
                            emer_emb.set_author(name="Configuration error")
                            emer_emb.set_footer(text="MailBot")
                            await emergency_contact.send(embed=emer_emb)

                        self.bot.log_action("Value for `staff_channel_id` is invalid.", 50, self.bot.logmail)

                    else:
                        rep_emb = Embed(color=Color.dark_green(), description="Your message was successfully sent !")
                        rep_emb.add_field(name="Message :", value=message.content)

                        staff_emb = Embed(color=Color.blurple(), description=f"**From:** <@{message.author.id}>",
                                          timestamp=time_now())
                        staff_emb.add_field(name="Message :", value=message.content)
                        staff_emb.set_footer(text="MailBot")

                        await staff_channel.send(embed=staff_emb,
                                                 files=[await file.to_file() for file in message.attachments])
                        self.bot.log_action(f"{message.author} ({message.author.id}) used mailbot", 26)

                    await message.reply(embed=rep_emb)

    @config_group.command(name="edit")
    @option(name="parameter", description="The parameter you want to change.", autocomplete=config_key_autocomplete)
    @option(name="value", description="The new value of the parameter")
    @commands.has_permissions(administrator=True)
    async def config_edit(self, ctx: ApplicationContext, parameter: str, value):
        with open("json/server_config.json", "r", encoding="utf-8") as config_file:
            config = json_load(config_file)

        old_value = config[parameter]

        try:
            value = int(value)

        except ValueError:
            await ctx.respond("Invalid value.", ephemeral=True)
            return

        config[parameter] = value

        with open("json/server_config.json", "w", encoding="utf-8") as config_file:
            json_dump(config, config_file, indent=2)

        res_emb = Embed(color=Color.dark_green(), description=f"Parameter `{parameter}`'s value successfully updated.\n"
                                                              f"`{old_value}` -> `{value}`")
        await ctx.respond(embed=res_emb)

    # TODO :
    #   - config_view ?
    #   - reply button under msg in staff_channel
    #       - btn open modal
    #       - modal cb -> send embed w/ reply content
    #       - btn 'send reply', 'edit reply', 'cancel'


def setup(bot_):
    bot_.add_cog(MailCog(bot_))

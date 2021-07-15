from asyncio import sleep
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument)
from discord.ext.commands import Context
from discord.ext.commands import when_mentioned_or
from ..db import db


OWNER_IDS = [217422560097206272]
COGS = [path.split("/")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    if not prefix:
        prefix = '?'
    return when_mentioned_or(prefix)(bot, message)


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)
    
    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()
      
        db.autosave(self.scheduler)
        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS)


    def setup(self):
        print('Loading COGS')
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")
        print("Setup complete")


    def update_db(self):
        print ("Updating database")
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                    ((guild.id,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
                    ((member.id,) for guild in self.guilds for member in guild.members if not member.bot))

        to_remove = []
        stored_members = db.column("SELECT UserID FROM exp")
        for id_ in stored_members:
            if not self.guild.get_member(id_):
                to_remove.append(id_)

        db.multiexec("DELETE FROM exp WHERE UserID = ?", ((id_,) for id_ in to_remove))
        db.commit()
        print('Database updated!')

    def run(self, version):
        self.VERSION = version

        print("Running setup...")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding="utf-8") as f:
            self.TOKEN = f.read()

        print("Running bot...")
        super().run(self.TOKEN, reconnect=True)


    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if self.ready:
            if ctx.command is not None and ctx.guild is not None:
                await self.invoke(ctx)

        else:
            await ctx.send("I'am not ready to  receive commands! Please wait a few seconds.")


# Testing task
    # async def print_message(self):
    #     await self.stdout.send("Iam a timed notification!")


    async def on_connect(self):
        print(" Bot connected")


    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong")


        raise


    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more arguments are missing.")

        elif isinstance(exc.original, HTTPException):
            await ctx.send("Unable to send message.")

        elif isinstance(exc.original, Forbidden):
            await ctx.send("I do not have to do that.")
        else:
            raise exc.original


    async def on_disconnect(self):
        print("Bot disconnected")

    
    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(217422811533148161)
            self.stdout = self.get_channel(740705433844449351)
            # Testing task
            # self.scheduler.add_job(self.print_message, CronTrigger(second="0,15,38,45"))
            self.scheduler.start()
            self.update_db()
            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print("Bot ready")
        else:
            print("Bot reconnected")
        await self.stdout.send("Bot online!")


    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
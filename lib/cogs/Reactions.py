from discord.ext.commands import Cog
from discord.ext.commands.core import has_permissions, command
from discord import Embed
from datetime import datetime, timedelta



numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
		   "6⃣", "7⃣", "8⃣", "9⃣", "🔟")

class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.polls = []

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.reactions = {
                "<:__:561483799599382540>": self.bot.guild.get_role(819265587933872158), # Minecraft
                "<:liga:819272813205913643>": self.bot.guild.get_role(819265536860356669), # LoL
                "<:rust:863850118666780682>": self.bot.guild.get_role(863850118666780682), # Rust
                "♟️": self.bot.guild.get_role(863855268239900732), # Chess
                "<:report:863852277243314196>": self.bot.guild.get_role(863855716997529600), # Among 
}
            self.reaction_message = await self.bot.get_channel(819261643699388457).fetch_message(863850225961926717)
            self.bot.cogs_ready.ready_up("Reactions")


    @command(name="createpoll", aliases=["mkpoll"])
    @has_permissions(manage_guild=True)
    async def create_poll(self, ctx, hours: int, question: str, *options):
        if len(options) > 10:
            await ctx.send("You can only supply 10 options!")
        embed = Embed(title="Poll",
                      description=question,
                      colout=ctx.author.colour,
                      timestamp=datetime.utcnow())

        fields = [("Options", "\n".join([f"{numbers[idx]} {options[idx]}" for idx, option in enumerate(options)]), False),
                  ("Insctructions", "React to case and vote!", False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        message = await ctx.send(embed=embed)

        for emoji in numbers[:len(options)]:
            await message.add_reaction(emoji)

        self.polls.append((message.channel.id, message.id))

        self.bot.scheduler.add_jon(self.complete_poll, "date", run_date=datetime.now() + timedelta(seconds=hours),
                                  args=[message.channel.id, message.id])


    async def complete_poll(self, ctx, channel_id, message_id):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)

        most_voted = max(message.reactions, key=lambda r: r.count)

        if most_voted == 1:
            await message.channel.send("There was no votes!")
        else:
            await message.channel.send(f"The results are in and option {most_voted.emoji} was the most popular with {most_voted.count-1:,} votes!")

        self.polls.remove((message.channel.id, message_id))


    # @Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     pass

    # @Cog.listener()
    # async def on_reaction_remove(self, reaction, user):
    #     pass

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_message.id:
            await payload.member.add_roles(self.reactions[f"<:{payload.emoji.name}:{payload.emoji.id}>"], reason="Role assigment")
            await self.reaction_message.remove_reaction(payload.emoji, payload.member)

        elif payload.message_id in (poll[1] for poll in self.polls):
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            for reaction in message.reactions:
                if (not payload.member.bot
                and payload.member in await reaction.users().flatten()
                and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)

    # @Cog.listener()
    # async def on_raw_reaction_remove(self, payload):
    #     if self.bot.ready and payload.message_id == self.reaction_message.id:
    #         member = self.bot.guild.get_member(payload.user_id)
    #         await payload.member.remove_roles(self.reactions[payload.emoji.name], reason="Role assigment")


def setup(bot):
    bot.add_cog(Reactions(bot))
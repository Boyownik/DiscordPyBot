from discord.ext.commands import Cog


class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot

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

    # @Cog.listener()
    # async def on_raw_reaction_remove(self, payload):
    #     if self.bot.ready and payload.message_id == self.reaction_message.id:
    #         member = self.bot.guild.get_member(payload.user_id)
    #         await payload.member.remove_roles(self.reactions[payload.emoji.name], reason="Role assigment")


def setup(bot):
    bot.add_cog(Reactions(bot))
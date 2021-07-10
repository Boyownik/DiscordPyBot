from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command

def log_embed(self, title, description, color, thumbnail=None, fields=None):
    embed = Embed(title=title,
                  description=description,
                  color=color,
                  timestamp=datetime.utcnow())
    embed.set_thumbnail(url=thumbnail or self.bot.guild.me.avatar_url)
    if fields is not None:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed

    
class Log(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(741634626359132251)
            self.bot.cogs_ready.ready_up("Log")

    @Cog.listener()
    async def on_user_update(self, before, after):
        if before.username != after.name:
            fields =[("Before", before.name, False),
                     ("After", after.name, False)]

            embed = log_embed(self, "User update", "Nickname change", after.colour, None,  fields)
            await self.log_channel.send(embed=embed)

        if before.username != after.name:
            fields = [("Before", before.discriminator, False),
                      ("After", after.discriminator, False)]

            embed = log_embed(self, "User update", "Discriminator change", after.colour, None,  fields)
            await self.log_channel.send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = log_embed(self, "Userr update", "Avatar update", after.colour)

            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            await self.log_channel.send(embed=embed)


    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            fields =[("Before", before.display_name, False),
                     ("After", after.display_name, False)]

            embed = log_embed(self, "Member update", "Nickname change", after.colour, None,  fields)
            await self.log_channel.send(embed=embed)

        elif before.roles != after.roles:
            fields =[("Before", ",".join([r.mention for r in before.roles]), False),
                     ("After", ",".join([r.mention for r in after.roles]), False)]

            embed = log_embed(self, "Member update", "Role update", after.colour, None, fields)
            await self.log_channel.send(embed=embed)


    @Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            if before.content != after.content:
                fields =[("Before", before.content, False),
                     ("After", after.content, False)]

                embed = log_embed(self, "Message edit", f"Edit by {after.author.display_name}.", after.author.colour, None, fields)
                await self.log_channel.send(embed=embed)


    @Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            fields =[("Content", message.content, False)]

            embed = log_embed(self, "Message deletion", f"Action by {message.author.display_name}.", message.author.colour, None, fields)
            await self.log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Log(bot))
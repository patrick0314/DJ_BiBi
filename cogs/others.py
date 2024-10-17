import asyncio
import discord

from discord.ext import commands
from utility.embed import COLOR, embed_base

class Others(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="card")
    async def card(self, ctx, name, title="Happy Birth Day", description="All the best on your special day!", url="https://www.foretblanc.com/site_media/img/664ec879cf3dc.jpg"):
        try:
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.purple(),
            )
            embed.set_author(name=name)
            embed.set_image(url=url)
            embed.set_footer(text=f"by BiBi & {ctx.message.author.name}")
        except Exception as e:
            print(e)

    @commands.command(name="others_help")
    async def others_help(self, ctx):
        try:
            help_message = """
# Others Command (`;`)
```
-card <name> [title] [descirption] [url] : send the embedded card to <name> with [title] [description] [image url]

<> = required information, [] = optional information
```
            """
            await ctx.send(embed=embed_base(ctx, description=help_message, color="orange", author=False))
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Others(bot))
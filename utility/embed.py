import datetime
import discord

COLOR = {
    "orange":discord.Color.orange(),
    "red":discord.Color.red(),
    "green":discord.Color.green()
}

def embed_base(ctx, title="", description="", color="green", author=True):
    embed = discord.Embed(
        title=title,
        description=description,
        color=COLOR[color],
        #timestamp=datetime.datetime.now()
    )
    if author: embed.set_author(name=ctx.message.author.name, url=ctx.message.author.avatar)
    return embed
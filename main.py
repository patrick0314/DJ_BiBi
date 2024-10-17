import os
import asyncio
import discord

from dotenv import load_dotenv
from discord.ext import commands
from utility.embed import embed_base

# Discord Bot Params
load_dotenv(dotenv_path="./env/password.env")
TOKEN=os.getenv("discord_token")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=";", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"{bot.user} is now ready!!!")

@bot.command(name="load")
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(embed=embed_base(ctx, title=f"Loaded {extension} done.", color="green", author=False))

@bot.command(name="unload")
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(embed=embed_base(ctx, title=f"Unloaded {extension} done.", color="red", author=False))

@bot.command(name="reload")
async def reload(ctx, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(embed=embed_base(ctx, title=f"Reloaded {extension} done.", color="green", author=False))

@bot.command(name="help")
async def help(ctx):
    try:
        help_message = """
# Game Command (`;`)
```
-music_help      : help for music commands
-playlist_help   : help for playlist commands
-game_help       : help for game commands
-others_help     : help for others commands
-midjourney_help : help for midjourney commands
```
        """
        await ctx.send(embed=embed_base(ctx, description=help_message, color="orange", author=False))
    except Exception as e:
        print(e)

# Load all extensions
async def loadAll():
    for filename in os.listdir("./cogs"):
        if not filename.endswith(".py"): continue
        await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await loadAll()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main=main())
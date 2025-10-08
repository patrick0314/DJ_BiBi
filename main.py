import os
import discord

from discord.ext import commands
from config import DISCORD_TOKEN

# --- Main Discord Bot Class ---
class DJ_BiBi(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True # required to get member information
        intents.message_content = True # required to read command content
        intents.voice_states = True # required to monitor and join voice channel

        super().__init__(command_prefix="!", intents=intents)

        # List of extentions (cogs) to be loaded on startup
        self.initial_extensions = ['cogs.music']
    
    async def setup_hook(self):
        # Called before the bot starts connecting, used to load extensions
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                print(f"Successfully loaded extension: {ext}")
            except Exception as e:
                print(f"Failed to load extension {ext}: {e}")
    
    async def on_ready(self):
        # Called when the bot successfully connects to Discord
        print("-----------------------------------")
        print(f"Bot is logged in as: {self.user}")
        print(f"User ID: {self.user.id}")
        print("-----------------------------------")

if __name__ == "__main__":
    if DISCORD_TOKEN == "":
        print("ERROR: Please update DISCORD_TOKEN in config.py before running")
    else:
        bot = DJ_BiBi()
        bot.run(DISCORD_TOKEN)
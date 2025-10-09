import os
import discord

from discord import app_commands
from discord.ext import commands
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from utils.embed import error_embed

class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = None

        if GEMINI_API_KEY:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
        else:
            print("WARNING: GEMINI_API_KEY not found. AI chat will be disabled")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore message by myself
        if message.author.bot:
            return
        
        # Check if direct message or not
        if message.guild is not None:
            return
        
        if not self.client:
            return
        
        prompt = message.content.strip()
        if not prompt:
            return
        
        try:
            await message.channel.typing()
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            await message.channel.send(response.text)
        except Exception as e:
            print(f"Gemini API Error in DM: {e}")
            await message.channel.send(embed=error_embed(
                title="❌ AI 服務錯誤",
                description="抱歉，AI 服務目前無法回應您的私訊請求。"
            ))

async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))
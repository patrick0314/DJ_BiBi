import discord
from discord.ext import commands

# --- Standard Colors ---
# Success (Green/Aqua) - For successful commands, status updates.
COLOR_SUCCESS = 0x57F287 
# Error (Red) - For failed commands, missing permissions, or general errors.
COLOR_ERROR = 0xED4245 
# General/Information (Blue/Blurple) - For general information, queues, etc.
COLOR_INFO = 0x5865F2 

# --- Basic Embed ---
def create_embed(title: str, description: str, color: int = COLOR_INFO):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
    )
    return embed

def success_embed(description: str, title: str = "✅ Success"):
    return create_embed(title=title, description=description, color=COLOR_SUCCESS)

def error_embed(description: str, title: str = "❌ Error"):
    return create_embed(title=title, description=description, color=COLOR_ERROR)

def info_embed(description: str, title: str = "💡 Information"):
    return create_embed(title=title, description=description, color=COLOR_INFO)
import os
import json
import discord

from discord.ext import commands
from discord.ui import Button, View
from utility.embed import embed_base
from utility.pokemon_const import playerStatus, initPokemons

class Pokemon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        if os.path.isfile("./data/pokemon.json"): self.playlist = json.load(open("./data/pokemon.json", "r"))
        else: self.playlist = {}

    
    @commands.command(name="mainmenu")
    async def mainmenu(self, ctx):
        try:
            class MainMenuView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=60)
                
                async def disableAll(self):
                    for item in self.children: item.disabled = True

                @discord.ui.button(label = "1", row=0, style = discord.ButtonStyle.success)
                async def first_button_callback(self, interaction: discord.Interaction, button):
                    await self.disableAll() # disable all buttons
                    await interaction.response.send_message("1")
                
                @discord.ui.button(label="2", row=0, style=discord.ButtonStyle.success)
                async def second_button_callback(self, interaction: discord.Interaction, button):
                    await self.disableAll() # disable all buttons
                    await interaction.response.send_message("2")
                
                @discord.ui.button(label="3", row=0, style=discord.ButtonStyle.success)
                async def third_button_callback(self, interaction: discord.Interaction, button):
                    await self.disableAll() # disable all buttons
                    await interaction.response.send_message("3")
                
                @discord.ui.button(label="4", row=0, style=discord.ButtonStyle.success)
                async def fourth_button_callback(self, interaction: discord.Interaction, button):
                    await self.disableAll() # disable all buttons
                    await interaction.response.send_message("4")

            await ctx.send(embed=embed_base(ctx, title="Main Menu:", description="1. Create a new character\n2. Check your own pokemons\n3. Check your own bag\n4. Play Roguelike", color="green", author=False), view=MainMenuView())
        except Exception as e:
            print(e)

    @commands.command(name="pokemon_help")
    async def game_help(self, ctx):
        try:
            help_message = """
# Pokemon Command (`;`)
```
<> = required information, [] = optional information
```
            """
            await ctx.send(embed=embed_base(ctx, description=help_message, color="orange", author=False))
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Pokemon(bot))
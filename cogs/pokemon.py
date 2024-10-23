import os
import json
import discord

from textwrap import dedent
from discord.ui import View
from discord.ext import commands
from utility.embed import embed_base
from utility.pokemon_const import Pokemons, Items
from utility.pokemon_utility import playerStatus, printList, printBoard

class Pokemon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        if os.path.isfile("./data/pokemon.json"): self.playlist = json.load(open("./data/pokemon.json", "r"))
        else: self.playlist = {}

        self.pokemon_idx = dict.fromkeys(self.playlist.keys(), 0)
        self.item_idx = dict.fromkeys(self.playlist.keys(), 0)

    @commands.command(name="pokemon")        
    async def pokemon(self, ctx):
        try:
            class MainMenuView(View):
                def __init__(self, parent):
                    super().__init__(timeout=60)
                    self.parent = parent # outside class (Pokemon)

                async def disableAll(self):
                    for item in self.children:
                        item.disabled = True

                # Create new character
                @discord.ui.button(label="1", row=0, style=discord.ButtonStyle.success)
                async def first_button(self, interaction: discord.Interaction, button):
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)
                    await self.parent.createCharacter(interaction)

                # Check user's pokemons
                @discord.ui.button(label="2", row=0, style=discord.ButtonStyle.success)
                async def second_button(self, interaction: discord.Interaction, button):
                    self.parent.pokemon_idx[str(interaction.user.id)] = 0
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)
                    await self.parent.checkPokemonMenu(interaction)

                # Check user's item
                @discord.ui.button(label="3", row=0, style=discord.ButtonStyle.success)
                async def third_button(self, interaction: discord.Interaction, button):
                    self.parent.item_idx[str(interaction.user.id)] = 0
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)
                    await interaction.response.checkItemMenu(interaction)

                # Play Roguelike
                @discord.ui.button(label="4", row=0, style=discord.ButtonStyle.success)
                async def fourth_button(self, interaction: discord.Interaction, button):
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)
                    await interaction.response.playRoguelike(interaction)

            description = """
            1. Create a new character
            2. Check your own pokemons
            3. Check your own item
            4. Play Roguelike
            """
            await ctx.send(embed=embed_base(ctx,
                title="Main Menu:",
                description=dedent(description),
                color="green", author=False), view=MainMenuView(self)
            )
        except Exception as e:
            print(e)

    async def createCharacter(self, interaction):
        try:
            class CreateCharacterView(View):
                def __init__(self, parent):
                    super().__init__(timeout=60)
                    self.parent = parent # outside class (Pokemon)

                async def disableAll(self):
                    for item in self.children:
                        item.disabled = True

                @discord.ui.button(label="Bulbasaur", row=0, style=discord.ButtonStyle.success)
                async def first_button(self, interaction: discord.Interaction, button):
                    self.parent.playlist[str(interaction.user.id)]["pokemon"].append(Pokemons["Bulbasaur"])
                    json.dump(self.parent.playlist, open("./data/pokemon.json", "w"), indent=2)
                    await self.disableAll()
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title="You and Bulbasaur are about to embark on an exciting adventure.",
                        description="", color="green", author=False), view=self)

                @discord.ui.button(label="Charmander", row=0, style=discord.ButtonStyle.success)
                async def second_button(self, interaction: discord.Interaction, button):
                    self.parent.playlist[str(interaction.user.id)]["pokemon"].append(Pokemons["Charmander"])
                    json.dump(self.parent.playlist, open("./data/pokemon.json", "w"), indent=2)
                    await self.disableAll()
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title="You and Charmander are about to embark on an exciting adventure.",
                        description="", color="green", author=False), view=self)

                @discord.ui.button(label="Squirtle", row=0, style=discord.ButtonStyle.success)
                async def third_button(self, interaction: discord.Interaction, button):
                    self.parent.playlist[str(interaction.user.id)]["pokemon"].append(Pokemons["Squirtle"])
                    json.dump(self.parent.playlist, open("./data/pokemon.json", "w"), indent=2)
                    await self.disableAll()
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title="You and BulbaSquirtlesaur are about to embark on an exciting adventure.",
                        description="", color="green", author=False), view=self)

            if str(interaction.user.id) in self.playlist:
                await interaction.followup.send(embed=embed_base(interaction, title="You have created a character.", color="red", author=False))
                raise

            # Init Player
            self.playlist[str(interaction.user.id)] = playerStatus.copy()
            self.playlist[str(interaction.user.id)]["name"] = interaction.user.name
            self.pokemon_idx[str(interaction.user.id)] = 0
            self.item_idx[str(interaction.user.id)] = 0

            await interaction.followup.send(embed=embed_base(interaction,
                title=f"Hi! {interaction.user.name}",
                description="Welcome to this world. Please choose your initial adventure partner:",
                color="green", author=False), view=CreateCharacterView(self)
            )
        except Exception as e:
            print(e)

    async def checkPokemonMenu(self, interaction: discord.Interaction):
        try:
            class CheckPokemonMenuView(View):
                def __init__(self, parent, interaction: discord.Interaction, idx):
                    super().__init__(timeout=60)
                    self.parent = parent
                    self.idx = idx
                    self.checkButton(interaction)

                def checkButton(self, interaction: discord.Interaction):
                    # Check next/previous-page button
                    n_pokemon = len(self.parent.playlist[str(interaction.user.id)]["pokemon"])
                    if (self.idx == 0): self.prev_page_button.disabled = True
                    else: self.prev_page_button.disabled = False
                    if (self.idx + 1 >= n_pokemon): self.second_button.disabled = True
                    else: self.second_button.disabled = False
                    if (self.idx + 2 >= n_pokemon): self.third_button.disabled = True
                    else: self.third_button.disabled = False
                    if (self.idx + 3 >= n_pokemon): self.fourth_button.disabled = True
                    else: self.fourth_button.disabled = False
                    if (self.idx + 4 >= n_pokemon): self.fifth_button.disabled = True
                    else: self.fifth_button.disabled = False
                    if (self.idx + 5 >= n_pokemon): self.next_page_button.disabled = True
                    else: self.next_page_button.disabled = False

                async def disableAll(self):
                    for item in self.children:
                        item.disabled = True

                @discord.ui.button(label="1", row=0, style=discord.ButtonStyle.success)
                async def first_button(self, interaction: discord.Interaction, button):
                    await self.parent.checkPokemon(interaction, self.idx)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="2", row=0, style=discord.ButtonStyle.success)
                async def second_button(self, interaction: discord.Interaction, button):
                    await self.parent.checkPokemon(interaction, self.idx + 1)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="3", row=0, style=discord.ButtonStyle.success)
                async def third_button(self, interaction: discord.Interaction, button):
                    await self.parent.checkPokemon(interaction, self.idx + 2)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="4", row=0, style=discord.ButtonStyle.success)
                async def fourth_button(self, interaction: discord.Interaction, button):
                    await self.parent.checkPokemon(interaction, self.idx + 3)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="5", row=0, style=discord.ButtonStyle.success)
                async def fifth_button(self, interaction: discord.Interaction, button):
                    await self.parent.checkPokemon(interaction, self.idx + 4)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="← Previous Page", row=1, style=discord.ButtonStyle.secondary)
                async def prev_page_button(self, interaction: discord.Interaction, button):
                    self.idx -= 5
                    self.checkButton(interaction)
                    msg = printList(idx=self.idx, li=self.parent.playlist[str(interaction.user.id)]["pokemon"])
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title="Pokemon Menu:",
                        description=dedent(msg),
                        color="green", author=False), view=self
                    )

                @discord.ui.button(label="Next Page →", row=1, style=discord.ButtonStyle.secondary)
                async def next_page_button(self, interaction: discord.Interaction, button):
                    self.idx += 5
                    self.checkButton(interaction)
                    msg = printList(idx=self.idx, li=self.parent.playlist[str(interaction.user.id)]["pokemon"])
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title="Pokemon Menu:",
                        description=dedent(msg),
                        color="green", author=False), view=self
                    )

            # Display
            msg = printList(idx=self.pokemon_idx[str(interaction.user.id)], li=self.playlist[str(interaction.user.id)]["pokemon"])
            await interaction.followup.send(embed=embed_base(interaction,
                title="Pokemon Menu:",
                description=dedent(msg),
                color="green", author=False), view=CheckPokemonMenuView(self, interaction, self.pokemon_idx[str(interaction.user.id)])
            )
        except Exception as e:
            print(e)
    
    async def checkPokemon(self, interaction: discord.Interaction, idx):
        try:
            class CheckPokemonView(View):
                def __init__(self, parent, interaction: discord.Interaction, idx):
                    super().__init__(timeout=60)
                    self.parent = parent
                    self.idx = idx
                    self.checkButton(interaction)

                def checkButton(self, interaction: discord.Interaction):
                    # Check next/previous button
                    n_pokemon = len(self.parent.playlist[str(interaction.user.id)]["pokemon"])
                    if (self.idx == n_pokemon - 1): self.next_pokemon_button.disabled = True
                    else: self.next_pokemon_button.disabled = False
                    if (self.idx == 0): self.prev_pokemon_button.disabled = True
                    else: self.prev_pokemon_button.disabled = False

                async def disableAll(self):
                    for item in self.children:
                        item.disabled = True

                @discord.ui.button(label = "← previous", row=0, style = discord.ButtonStyle.success)
                async def prev_pokemon_button(self, interaction: discord.Interaction, button):
                    if ((self.idx - 1) % 5 == 4): self.parent.pokemon_idx[str(interaction.user.id)] -= 5
                    self.idx -= 1
                    self.checkButton(interaction)
                    
                    msg = printBoard(idx=self.idx, dt=self.parent.playlist[str(interaction.user.id)]["pokemon"], ignore={"name", "id"})
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title=f"{self.parent.playlist[str(interaction.user.id)]['pokemon'][self.idx]['name']}",
                        description=dedent(msg),
                        color="green", author=False), view=self
                    )

                @discord.ui.button(label="next →", row=0, style=discord.ButtonStyle.success)
                async def next_pokemon_button(self, interaction: discord.Interaction, button):
                    if ((self.idx + 1) % 5 == 0): self.parent.pokemon_idx[str(interaction.user.id)] += 5
                    self.idx += 1
                    self.checkButton(interaction)
                    
                    msg = printBoard(idx=self.idx, dt=self.parent.playlist[str(interaction.user.id)]["pokemon"], ignore={"name", "id"})
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title=f"{self.parent.playlist[str(interaction.user.id)]['pokemon'][self.idx]['name']}",
                        description=dedent(msg),
                        color="green", author=False), view=self
                    )

            msg = printBoard(idx=idx, dt=self.playlist[str(interaction.user.id)]["pokemon"], ignore={"name", "id"})
            await interaction.response.defer()
            await interaction.followup.send(embed=embed_base(interaction,
                title=f"{self.playlist[str(interaction.user.id)]['pokemon'][idx]['name']}",
                description=dedent(msg),
                color="green", author=False), view=CheckPokemonView(self, interaction, idx=idx)
            )
        except Exception as e:
            print(e)

    async def checkItemMenu(self, interaction: discord.Interaction):
        try:
            class CheckItemMenuView(View):
                def __init__(self, parent, interaction: discord.Interaction, idx):
                    super().__init__(timeout=60)
                    self.parent = parent
                    self.idx = idx
                    self.checkButton(interaction)

                def checkButton(self, interaction: discord.Interaction):
                    # Check next/previous-page button
                    n_item = len(self.parent.playlist[str(interaction.user.id)]["item"])
                    if (self.idx == 0): self.prev_page_button.disabled = True
                    else: self.prev_page_button.disabled = False
                    if (self.idx + 1 >= n_item): self.second_button.disabled = True
                    else: self.second_button.disabled = False
                    if (self.idx + 2 >= n_item): self.third_button.disabled = True
                    else: self.third_button.disabled = False
                    if (self.idx + 3 >= n_item): self.fourth_button.disabled = True
                    else: self.fourth_button.disabled = False
                    if (self.idx + 4 >= n_item): self.fifth_button.disabled = True
                    else: self.fifth_button.disabled = False
                    if (self.idx + 5 >= n_item): self.next_page_button.disabled = True
                    else: self.next_page_button.disabled = False

                async def disableAll(self):
                    for item in self.children:
                        item.disabled = True

                @discord.ui.button(label="1", row=0, style=discord.ButtonStyle.success)
                async def first_button(self, interaction: discord.Interaction, button):
                    await self.parent.checkItem(interaction, self.idx)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="2", row=0, style=discord.ButtonStyle.success)
                async def second_button(self, interaction: discord.Interaction, button):
                    await self.parent.checkItem(interaction, self.idx + 1)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="3", row=0, style=discord.ButtonStyle.success)
                async def third_button(self, interaction: discord.Interaction, button):
                    await self.parent.checkItem(interaction, self.idx + 2)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="4", row=0, style=discord.ButtonStyle.success)
                async def fourth_button(self, interaction: discord.Interaction, button):
                    await self.parent.checkItem(interaction, self.idx + 3)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="5", row=0, style=discord.ButtonStyle.success)
                async def fifth_button(self, interaction: discord.Interaction, button):
                    await self.parent.checkItem(interaction, self.idx + 4)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="← Previous Page", row=1, style=discord.ButtonStyle.secondary)
                async def prev_page_button(self, interaction: discord.Interaction, button):
                    self.idx -= 5
                    self.checkButton(interaction)
                    msg = printList(idx=self.idx, li=self.parent.playlist[str(interaction.user.id)]["item"])
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title="Item Menu:",
                        description=dedent(msg),
                        color="green", author=False), view=self
                    )

                @discord.ui.button(label="Next Page →", row=1, style=discord.ButtonStyle.secondary)
                async def next_page_button(self, interaction: discord.Interaction, button):
                    self.idx += 5
                    self.checkButton(interaction)
                    msg = printList(idx=self.idx, li=self.parent.playlist[str(interaction.user.id)]["item"])
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title="Item Menu:",
                        description=dedent(msg),
                        color="green", author=False), view=self
                    )

            # Display
            msg = printList(idx=self.pokemon_idx[str(interaction.user.id)], li=self.playlist[str(interaction.user.id)]["item"])
            await interaction.followup.send(embed=embed_base(interaction,
                title="Item Menu:",
                description=dedent(msg),
                color="green", author=False), view=CheckItemMenuView(self, interaction, self.pokemon_idx[str(interaction.user.id)])
            )
        except Exception as e:
            print(e)

    async def checkItem(self, interaction: discord.Interaction, idx):
        try:
            class CheckItemView(View):
                def __init__(self, parent, interaction: discord.Interaction, idx):
                    super().__init__(timeout=60)
                    self.parent = parent
                    self.idx = idx
                    self.checkButton(interaction)

                def checkButton(self, interaction: discord.Interaction):
                    # Check next/previous button
                    n_item = len(self.parent.playlist[str(interaction.user.id)]["item"])
                    if (self.idx == n_item - 1): self.next_item_button.disabled = True
                    else: self.next_item_button.disabled = False
                    if (self.idx == 0): self.prev_item_button.disabled = True
                    else: self.prev_item_button.disabled = False

                async def disableAll(self):
                    for item in self.children:
                        item.disabled = True

                @discord.ui.button(label = "← previous", row=0, style = discord.ButtonStyle.success)
                async def prev_item_button(self, interaction: discord.Interaction, button):
                    if ((self.idx - 1) % 5 == 4): self.parent.item_idx[str(interaction.user.id)] -= 5
                    self.idx -= 1
                    self.checkButton(interaction)
                    
                    msg = printBoard(idx=self.idx, dt=self.parent.playlist[str(interaction.user.id)]["item"], ignore={"name", "id"})
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title=f"{self.parent.playlist[str(interaction.user.id)]['item'][self.idx]['name']}", 
                        description=dedent(msg),
                        color="green", author=False), view=self
                    )

                @discord.ui.button(label="next →", row=0, style=discord.ButtonStyle.success)
                async def next_item_button(self, interaction: discord.Interaction, button):
                    if ((self.idx + 1) % 5 == 0): self.parent.item_idx[str(interaction.user.id)] += 5
                    self.idx += 1
                    self.checkButton(interaction)
                    
                    msg = printBoard(idx=self.idx, dt=self.parent.playlist[str(interaction.user.id)]["item"], ignore={"name", "id"})
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title=f"{self.parent.playlist[str(interaction.user.id)]['item'][self.idx]['name']}",
                        description=dedent(msg),
                        color="green", author=False), view=self
                    )

            msg = printBoard(idx=idx, dt=self.playlist[str(interaction.user.id)]["item"], ignore={"name", "id"})
            await interaction.response.defer()
            await interaction.followup.send(embed=embed_base(interaction,
                title=f"{self.playlist[str(interaction.user.id)]['item'][idx]['name']}",
                description=dedent(msg),
                color="green", author=False), view=CheckItemView(self, interaction, idx=idx)
            )
        except Exception as e:
            print(e)

    async def playRoguelike(self, interaction):
        try:
            pass
        except Exception as e:
            print(e)
    
    @commands.command(name="getPokemon")
    async def getPokemon(self, ctx, pokemon):
        if (str(ctx.author.id) != "645961777317675019"):
            raise
        self.playlist[str(ctx.author.id)]["pokemon"].append(Pokemons[pokemon])
        json.dump(self.playlist, open("./data/pokemon.json", "w"), indent=2)
        await ctx.send(embed=embed_base(ctx, title=f"You get {pokemon}!", color="green", author=False))

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
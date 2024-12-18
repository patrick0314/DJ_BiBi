import os
import copy
import json
import math
import heapq
import random
import discord
import discord.ext

from textwrap import dedent
import discord.context_managers
import discord.ext.commands
from discord.ui import View
from discord.ext import commands
from utility.embed import embed_base
from utility.pokemon_const import Pokemons, Minions, Bosses
from utility.pokemon_utility import playerStatus, RoguelikeDungeon, DungeonRoom, printList, printBoard

class Pokemon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Load data
        if os.path.isfile("./data/pokemon.json"): self.playerList = json.load(open("./data/pokemon.json", "r"))
        else: self.playerList = {}; json.dump(open("./data/pokemon.json", "w"), indent=2)
        if os.path.isfile("./data/leaderboard.json"): self.leaderboard = json.load(open("./data/leaderboard.json", "r"))
        else: self.leaderboard = {"roguelike": []}; json.dump(open("./data/leaderboard.json", "w"), indent=2)

        for i, (value, name) in enumerate(self.leaderboard["roguelike"]):
            self.leaderboard["roguelike"][i] = (value, name)

        self.pokemonId = dict.fromkeys(self.playerList.keys(), 0)

    @commands.command(name="pokemon")        
    async def pokemon(self, ctx: discord.ext.commands.Context):
        try:
            # Button view
            class MainMenuView(View):
                def __init__(self, parent: Pokemon):
                    super().__init__(timeout=60)
                    self.parent = parent # outside class (Pokemon)

                async def disableAll(self):
                    # Disable all buttons
                    for item in self.children: # discord.ui.button
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
                    self.parent.pokemonId[str(interaction.user.id)] = 0
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)
                    await self.parent.checkPokemonMenu(interaction)

                # Play Roguelike
                @discord.ui.button(label="3", row=0, style=discord.ButtonStyle.success)
                async def third_button(self, interaction: discord.Interaction, button):
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)
                    await self.parent.RoguelikeMenu(interaction)
                
                # Show leaderboard
                @discord.ui.button(label="4", row=0, style=discord.ButtonStyle.success)
                async def fourth_button(self, interaction: discord.Interaction, button):
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)
                    await self.parent.showLeaderboard(interaction)

            description = """
            1. Create a new character
            2. Check your own pokemons
            3. Play Roguelike
            4. Show leader-board
            """
            await ctx.send(embed=embed_base(ctx, title="Main Menu:", description=dedent(description), color="green", author=False), view=MainMenuView(self))
        except Exception as e:
            print(e)

    async def createCharacter(self, interaction: discord.Interaction):
        try:
            # Check if player has created a character
            if str(interaction.user.id) in self.playerList:
                await interaction.followup.send(embed=embed_base(interaction, title="You have created a character.", color="red", author=False))
                raise

            # Button view
            class CreateCharacterView(View):
                def __init__(self, parent: Pokemon, interaction: discord.Interaction):
                    super().__init__(timeout=60)
                    self.parent = parent # outside class (Pokemon)

                async def disableAll(self):
                    # Disable all buttons
                    for item in self.children: # discord.ui.button
                        item.disabled = True

                @discord.ui.button(label="Bulbasaur", row=0, style=discord.ButtonStyle.success)
                async def first_button(self, interaction: discord.Interaction, button):
                    self.parent.playerList[str(interaction.user.id)]["pokemon"].append(Pokemons["Bulbasaur"])
                    json.dump(self.parent.playerList, open("./data/pokemon.json", "w"), indent=2)
                    await self.disableAll()
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title="You and Bulbasaur are about to embark on an exciting adventure.", color="green", author=False), view=self
                    )

                @discord.ui.button(label="Charmander", row=0, style=discord.ButtonStyle.success)
                async def second_button(self, interaction: discord.Interaction, button):
                    self.parent.playerList[str(interaction.user.id)]["pokemon"].append(Pokemons["Charmander"])
                    json.dump(self.parent.playerList, open("./data/pokemon.json", "w"), indent=2)
                    await self.disableAll()
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title="You and Charmander are about to embark on an exciting adventure.", color="green", author=False), view=self
                    )

                @discord.ui.button(label="Squirtle", row=0, style=discord.ButtonStyle.success)
                async def third_button(self, interaction: discord.Interaction, button):
                    self.parent.playerList[str(interaction.user.id)]["pokemon"].append(Pokemons["Squirtle"])
                    json.dump(self.parent.playerList, open("./data/pokemon.json", "w"), indent=2)
                    await self.disableAll()
                    await interaction.response.edit_message(embed=embed_base(interaction,
                        title="You and Squirtle are about to embark on an exciting adventure.", color="green", author=False), view=self
                    )

            # Init character
            self.playerList[str(interaction.user.id)] = playerStatus.copy()
            self.playerList[str(interaction.user.id)]["name"] = interaction.user.name
            self.pokemonId[str(interaction.user.id)] = 0
            await interaction.followup.send(embed=embed_base(interaction,
                title=f"Hi! {interaction.user.name}", description="Welcome to this world.\n\nPlease choose your initial adventure partner:",
                color="green", author=False), view=CreateCharacterView(self, interaction), ephemeral=True
            )
        except Exception as e:
            print(e)

    async def checkPokemonMenu(self, interaction: discord.Interaction):
        try:
            # Button view
            class CheckPokemonMenuView(View):
                def __init__(self, parent: Pokemon, interaction: discord.Interaction, idx):
                    super().__init__(timeout=60)
                    self.parent = parent
                    self.idx = idx
                    self.checkButton(interaction)

                def checkButton(self, interaction: discord.Interaction):
                    # Check if each button should be disabled or not
                    n_pokemon = len(self.parent.playerList[str(interaction.user.id)]["pokemon"])
                    self.prev_page_button.disabled = True if (self.idx == 0) else False
                    self.second_button.disabled    = True if (self.idx + 1 >= n_pokemon) else False
                    self.third_button.disabled     = True if (self.idx + 2 >= n_pokemon) else False
                    self.fourth_button.disabled    = True if (self.idx + 3 >= n_pokemon) else False
                    self.fifth_button.disabled     = True if (self.idx + 4 >= n_pokemon) else False
                    self.next_page_button.disabled = True if (self.idx + 5 >= n_pokemon) else False

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
                    msg = printList(idx=self.idx, li=self.parent.playerList[str(interaction.user.id)]["pokemon"])
                    await interaction.response.edit_message(embed=embed_base(interaction, title="Pokemon Menu:", description=dedent(msg), color="green", author=False), view=self)

                @discord.ui.button(label="Next Page →", row=1, style=discord.ButtonStyle.secondary)
                async def next_page_button(self, interaction: discord.Interaction, button):
                    self.idx += 5
                    self.checkButton(interaction)
                    msg = printList(idx=self.idx, li=self.parent.playerList[str(interaction.user.id)]["pokemon"])
                    await interaction.response.edit_message(embed=embed_base(interaction, title="Pokemon Menu:", description=dedent(msg), color="green", author=False), view=self)

            # Display
            msg = printList(idx=0, li=self.playerList[str(interaction.user.id)]["pokemon"])
            await interaction.followup.send(embed=embed_base(interaction, title="Pokemon Menu:", description=dedent(msg), color="green", author=False),
                view=CheckPokemonMenuView(self, interaction, self.pokemonId[str(interaction.user.id)]), ephemeral=True
            )
        except Exception as e:
            print(e)
    
    async def checkPokemon(self, interaction: discord.Interaction, idx):
        try:
            class CheckPokemonView(View):
                def __init__(self, parent: Pokemon, interaction: discord.Interaction, idx):
                    super().__init__(timeout=60)
                    self.parent = parent
                    self.idx = idx
                    self.checkButton(interaction)

                def checkButton(self, interaction: discord.Interaction):
                    # Check if each button should be disabled or not
                    n_pokemon = len(self.parent.playerList[str(interaction.user.id)]["pokemon"])
                    self.next_pokemon_button.disabled = True if (self.idx == n_pokemon - 1) else False
                    self.prev_pokemon_button.disabled = True if (self.idx == 0) else False

                async def disableAll(self):
                    for item in self.children:
                        item.disabled = True

                @discord.ui.button(label = "← previous", row=0, style = discord.ButtonStyle.success)
                async def prev_pokemon_button(self, interaction: discord.Interaction, button):
                    if ((self.idx - 1) % 5 == 4): self.parent.pokemonId[str(interaction.user.id)] -= 5
                    self.idx -= 1
                    self.checkButton(interaction)
                    
                    msg = printBoard(idx=self.idx, dt=self.parent.playerList[str(interaction.user.id)]["pokemon"], ignore={"name", "id"})
                    await interaction.response.edit_message(embed=embed_base(interaction, title=f"{self.parent.playerList[str(interaction.user.id)]['pokemon'][self.idx]['name']}",
                        description=dedent(msg), color="green", author=False), view=self
                    )

                @discord.ui.button(label="next →", row=0, style=discord.ButtonStyle.success)
                async def next_pokemon_button(self, interaction: discord.Interaction, button):
                    if ((self.idx + 1) % 5 == 0): self.parent.pokemonId[str(interaction.user.id)] += 5
                    self.idx += 1
                    self.checkButton(interaction)
                    
                    msg = printBoard(idx=self.idx, dt=self.parent.playerList[str(interaction.user.id)]["pokemon"], ignore={"name", "id"})
                    await interaction.response.edit_message(embed=embed_base(interaction, title=f"{self.parent.playerList[str(interaction.user.id)]['pokemon'][self.idx]['name']}",
                        description=dedent(msg), color="green", author=False), view=self
                    )

            msg = printBoard(idx=idx, dt=self.playerList[str(interaction.user.id)]["pokemon"], ignore={"name", "id"})
            await interaction.response.defer()
            await interaction.followup.send(embed=embed_base(interaction, title=f"{self.playerList[str(interaction.user.id)]['pokemon'][idx]['name']}",
                description=dedent(msg), color="green", author=False), view=CheckPokemonView(self, interaction, idx=idx), ephemeral=True
            )
        except Exception as e:
            print(e)
    
    async def RoguelikeMenu(self, interaction: discord.Interaction):
        try:
            class RoguelikeMenuView(View):
                def __init__(self, parent: Pokemon, interaction: discord.Interaction, idx):
                    super().__init__(timeout=60)
                    self.parent = parent
                    self.idx = idx
                    #self.checkButton(interaction)

                def checkButton(self, interaction: discord.Interaction):
                    # Check if each button should be disabled or not
                    n_pokemon = len(self.parent.playerList[str(interaction.user.id)]["pokemon"])
                    self.prev_page_button.disabled = True if (self.idx == 0) else False
                    self.second_button.disabled    = True if (self.idx + 1 >= n_pokemon) else False
                    self.third_button.disabled     = True if (self.idx + 2 >= n_pokemon) else False
                    self.fourth_button.disabled    = True if (self.idx + 3 >= n_pokemon) else False
                    self.fifth_button.disabled     = True if (self.idx + 4 >= n_pokemon) else False
                    self.next_page_button.disabled = True if (self.idx + 5 >= n_pokemon) else False

                async def disableAll(self):
                    for item in self.children:
                        item.disabled = True

                @discord.ui.button(label="1", row=0, style=discord.ButtonStyle.success)
                async def first_button(self, interaction: discord.Interaction, button):
                    await self.parent.Roguelike(interaction, self.idx)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="2", row=0, style=discord.ButtonStyle.success)
                async def second_button(self, interaction: discord.Interaction, button):
                    await self.parent.Roguelike(interaction, self.idx + 1)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="3", row=0, style=discord.ButtonStyle.success)
                async def third_button(self, interaction: discord.Interaction, button):
                    await self.parent.Roguelike(interaction, self.idx + 2)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="4", row=0, style=discord.ButtonStyle.success)
                async def fourth_button(self, interaction: discord.Interaction, button):
                    await self.parent.Roguelike(interaction, self.idx + 3)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="5", row=0, style=discord.ButtonStyle.success)
                async def fifth_button(self, interaction: discord.Interaction, button):
                    await self.parent.Roguelike(interaction, self.idx + 4)
                    await self.disableAll()
                    await interaction.response.edit_message(view=self)

                @discord.ui.button(label="← Previous Page", row=1, style=discord.ButtonStyle.secondary)
                async def prev_page_button(self, interaction: discord.Interaction, button):
                    self.idx -= 5
                    self.checkButton(interaction)
                    msg = "You can choose one of your Pokémon to accompany you on this dungeon adventure.\n"
                    msg = printList(idx=self.idx, li=self.parent.playerList[str(interaction.user.id)]["pokemon"])
                    await interaction.response.edit_message(embed=embed_base(interaction, title="Welcome to the dungeon!", description=dedent(msg), color="green", author=False), view=self)

                @discord.ui.button(label="Next Page →", row=1, style=discord.ButtonStyle.secondary)
                async def next_page_button(self, interaction: discord.Interaction, button):
                    self.idx += 5
                    self.checkButton(interaction)
                    msg = "You can choose one of your Pokémon to accompany you on this dungeon adventure.\n"
                    msg = printList(idx=self.idx, li=self.parent.playerList[str(interaction.user.id)]["pokemon"])
                    await interaction.response.edit_message(embed=embed_base(interaction, title="Welcome to the dungeon!", description=dedent(msg), color="green", author=False), view=self)

            # Display
            msg = "You can choose one of your Pokémon to accompany you on this dungeon adventure.\n"
            msg += printList(idx=0, li=self.playerList[str(interaction.user.id)]["pokemon"])
            await interaction.followup.send(embed=embed_base(interaction, title="Welcome to the dungeon!", description=dedent(msg), color="green", author=False),
                view=RoguelikeMenuView(self, interaction, self.pokemonId[str(interaction.user.id)]), ephemeral=True
            )
        except Exception as e:
            print(e)

    async def Roguelike(self, interaction: discord.Interaction, idx):
        try:
            class RoguelikeView(View):
                def __init__(self, parent: Pokemon, player, dungeon: RoguelikeDungeon, idx):
                    super().__init__(timeout=60)
                    self.parent = parent
                    self.player = player
                    self.idx = idx
                    self.dungeon = dungeon

                    self.layer = 0
                    self.room = None
                    self.mode = None

                    # Button Init
                    self.rock.disabled = self.paper.disabled = self.scissors.disabled = True
                    self.next_room_button.disabled = False
                    self.exit_button.disabled = True

                    # Battle Info
                    self.enemy = None
                    self.maxHP = self.player["pokemon"][self.idx]["hp"] # player max HP
                    self.deHP_player = 0 # player decreased HP
                    self.deHP_enemy  = 0 # enemy  decreased HP

                    # Treasure Info
                    self.HPbuff   = None
                    self.ATKbuff  = None
                    self.bothbuff = None
                
                async def disableAll(self):
                    for item in self.children:
                        item.disabled = True
                
                async def disableMode(self, mode=True):
                    # mode=True : cannot choose rock-paper-scissors and exit, can    choose next
                    # mode=False: can    choose rock-paper-scissors and exit, cannot choose next
                    self.rock.disabled = self.paper.disabled = self.scissors.disabled = True if mode else False
                    self.next_room_button.disabled = False if mode else True
                    self.exit_button.disabled = True if mode else False

                def battle(self, res=""):
                    if res == "It's a tie!": emoji = "(ง ･ω･)=○ ○=(ಠ_ಠ)ᕤ"
                    elif res == "You lost!": emoji = "(ง`ε(○=(ಠ_ಠ)ᕤ"
                    elif res == "You won!":  emoji = "(ง ･ω･)=○)ﾟoﾟ)╯"
                    else: emoji = "(ง ･ω･)ง ᕦ(ಠ_ಠ)ᕤ"
                    numEnemy = (self.enemy["hp"] - self.deHP_enemy) * 10 // self.enemy["hp"]
                    numPlayer = (self.maxHP - self.deHP_player) * 10 // self.maxHP
                    msg = f"""
{self.enemy['name']} [{'●'*numEnemy}{'○'*(10-numEnemy)}] {self.enemy["hp"]-self.deHP_enemy} / {self.enemy["hp"]}

{emoji}

{self.player["pokemon"][self.idx]["name"]} [{'●'*numPlayer}{'○'*(10-numPlayer)}] {self.maxHP-self.deHP_player} / {self.maxHP}
                    """
                    return msg
                
                @discord.ui.button(label="rock", row=0, style=discord.ButtonStyle.success)
                async def rock(self, interaction: discord.Interaction, button):
                    try:
                        if self.mode == "battle" or self.mode == "boss":
                            enemy_moves = random.randint(0, 2)
                            if enemy_moves == 0: pass; title = "It's a tie!"
                            elif enemy_moves == 1: self.deHP_player += self.enemy["atk"]; title = "You lost!"
                            elif enemy_moves == 2: self.deHP_enemy += self.player["pokemon"][self.idx]["atk"]; title = "You won!"

                            # Display
                            if self.deHP_player >= self.maxHP:
                                # Update
                                if len(self.parent.leaderboard["roguelike"]) > 10: heapq.heappushpop(self.parent.leaderboard["roguelike"], (-self.layer, interaction.user.name))
                                else: heapq.heappush(self.parent.leaderboard["roguelike"], (-self.layer, interaction.user.name))
                                json.dump(self.parent.leaderboard, open("./data/leaderboard.json", "w"), indent=2)
                                await self.disableAll()
                                title = "Game over"
                                await interaction.response.edit_message(embed=embed_base(interaction, title=title, color="red", author=False), view=self)
                            elif self.deHP_enemy >= self.enemy["hp"]:
                                await self.disableMode(mode=True)
                                title = f"You defeat {self.enemy['name']}"
                                await interaction.response.edit_message(embed=embed_base(interaction, title=title, color="red", author=False), view=self)
                            else:
                                msg = self.battle(title)
                                await interaction.response.edit_message(embed=embed_base(interaction, title=title, description=msg, color="green", author=False), view=self)
                        elif self.mode == "treasure":
                            await self.disableMode(mode=True)
                            self.maxHP += self.HPbuff
                            title = f"{self.player['pokemon'][self.idx]['name']} receives a HP ({self.HPbuff}) buff."
                            await interaction.response.edit_message(embed=embed_base(interaction, title=title, color="green", author=False), view=self)
                    except Exception as e:
                        print(e)

                @discord.ui.button(label="paper", row=0, style=discord.ButtonStyle.success)
                async def paper(self, interaction: discord.Interaction, button):
                    try:
                        if self.mode == "battle" or self.mode == "boss":
                            # Check results
                            enemy_moves = random.randint(0, 2)
                            if enemy_moves == 0: self.deHP_enemy += self.player["pokemon"][self.idx]["atk"]; title = "You won!"
                            elif enemy_moves == 1: pass; title = "It's a tie!"
                            elif enemy_moves == 2: self.deHP_player += self.enemy["atk"]; title = "You lost!"

                            # Display
                            if self.deHP_player >= self.maxHP:
                                # Update
                                if len(self.parent.leaderboard["roguelike"]) > 10: heapq.heappushpop(self.parent.leaderboard["roguelike"], (-self.layer, interaction.user.name))
                                else: heapq.heappush(self.parent.leaderboard["roguelike"], (-self.layer, interaction.user.name))
                                json.dump(self.parent.leaderboard, open("./data/leaderboard.json", "w"), indent=2)
                                await self.disableAll()
                                title = "Game over"
                                await interaction.response.edit_message(embed=embed_base(interaction, title=title, color="red", author=False), view=self)
                            elif self.deHP_enemy >= self.enemy["hp"]:
                                await self.disableMode(mode=True)
                                title = f"You defeat {self.enemy['name']}"
                                await interaction.response.edit_message(embed=embed_base(interaction, title=title, color="red", author=False), view=self)
                            else:
                                msg = self.battle(title)
                                await interaction.response.edit_message(embed=embed_base(interaction, title=title, description=msg, color="green", author=False), view=self)
                        elif self.mode == "treasure":
                            await self.disableMode(mode=True)
                            self.player["pokemon"][self.idx]["atk"] += self.ATKbuff
                            title = f"{self.player['pokemon'][self.idx]['name']} receives a ATK ({self.ATKbuff}) buff."
                            await interaction.response.edit_message(embed=embed_base(interaction, title=title, color="green", author=False), view=self)
                    except Exception as e:
                        print(e)

                @discord.ui.button(label="scissors", row=0, style=discord.ButtonStyle.success)
                async def scissors(self, interaction: discord.Interaction, button):
                    try:
                        if self.mode == "battle" or self.mode == "boss":
                            enemy_moves = random.randint(0, 2)
                            if enemy_moves == 0: self.deHP_enemy += self.player["pokemon"][self.idx]["atk"]; title = "You won!"
                            elif enemy_moves == 1: self.deHP_player += self.enemy["atk"]; title = "You lost!"
                            elif enemy_moves == 2: pass; title = "It's a tie!"

                            # Display
                            if self.deHP_player >= self.maxHP:
                                # Update
                                if len(self.parent.leaderboard["roguelike"]) > 10: heapq.heappushpop(self.parent.leaderboard["roguelike"], (-self.layer, interaction.user.name))
                                else: heapq.heappush(self.parent.leaderboard["roguelike"], (-self.layer, interaction.user.name))
                                json.dump(self.parent.leaderboard, open("./data/leaderboard.json", "w"), indent=2)
                                await self.disableAll()
                                title = "Game over"
                                await interaction.response.edit_message(embed=embed_base(interaction, title=title, color="red", author=False), view=self)
                            elif self.deHP_enemy >= self.enemy["hp"]:
                                await self.disableMode(mode=True)
                                title = f"You defeat {self.enemy['name']}"
                                await interaction.response.edit_message(embed=embed_base(interaction, title=title, color="red", author=False), view=self)
                            else:
                                msg = self.battle(title)
                                await interaction.response.edit_message(embed=embed_base(interaction, title=title, description=msg, color="green", author=False), view=self)
                        elif self.mode == "treasure":
                            await self.disableMode(mode=True)
                            self.maxHP += self.bothbuff
                            self.player["pokemon"][self.idx]["atk"] += self.bothbuff
                            title = f"{self.player['pokemon'][self.idx]['name']} receives a HP & ATK ({self.bothbuff}) buff."
                            await interaction.response.edit_message(embed=embed_base(interaction, title=title, color="green", author=False), view=self)
                    except Exception as e:
                        print(e)
                        
                @discord.ui.button(label="Next Room", row=1, style=discord.ButtonStyle.secondary)
                async def next_room_button(self, interaction: discord.Interaction, button):
                    try:
                        # Init
                        self.layer += 1
                        self.room = self.dungeon.get_next_room()
                        self.mode = self.room.trigger_event()
                        self.deHP_enemy = 0

                        # Update
                        self.parent.playerList[str(interaction.user.id)]["pokemon"][self.idx]["exp"] += int(math.sqrt(self.layer))
                        if self.parent.playerList[str(interaction.user.id)]["pokemon"][self.idx]["exp"] > 100:
                            self.parent.playerList[str(interaction.user.id)]["pokemon"][self.idx]["level"] += 1
                            self.parent.playerList[str(interaction.user.id)]["pokemon"][self.idx]["exp"] -= 100
                            self.parent.playerList[str(interaction.user.id)]["pokemon"][self.idx]["hp"] += 10
                            self.parent.playerList[str(interaction.user.id)]["pokemon"][self.idx]["atk"] += 5
                        json.dump(self.parent.playerList, open("./data/pokemon.json", "w"), indent=2)
                        print("===> update done")

                        # Start
                        if self.mode == "battle":
                            await self.disableMode(mode=False)
                            self.enemy = Minions[random.choice(list(Minions.keys()))]
                            self.enemy["hp"] += self.layer * 2
                            self.enemy["atk"] += self.layer * 2
                            msg = self.battle()
                            await interaction.response.edit_message(embed=embed_base(interaction, description=msg, color="green", author=False), view=self)
                        elif self.mode == "treasure":
                            await self.disableMode(mode=False)
                            self.HPbuff = random.randint(self.layer+15, self.layer+20)
                            self.ATKbuff = random.randint(self.layer+5, self.layer+10)
                            self.bothbuff = random.randint(self.layer, self.layer+5)
                            msg = f"""
                            1. HP buffer : {self.HPbuff} → rock
                            2. ATK buffer : {self.ATKbuff} → paper
                            3. HP + ATK buffer : {self.bothbuff} → scissors
                            """
                            await interaction.response.edit_message(embed=embed_base(interaction, description=dedent(msg), color="green", author=False), view=self)
                        elif self.mode == "boss":
                            await self.disableMode(mode=False)
                            self.enemy = Bosses[random.choice(list(Bosses.keys()))]
                            self.enemy["hp"] += self.layer * 5
                            self.enemy["atk"] += self.layer * 5
                            msg = self.battle()
                            await interaction.response.edit_message(embed=embed_base(interaction, description=msg, color="green", author=False), view=self)
                    except Exception as e:
                        print(e)
                
                @discord.ui.button(label="Exit", row=1, style=discord.ButtonStyle.secondary)
                async def exit_button(self, interaction: discord.Interaction, button):
                    try:
                        # Update
                        if len(self.parent.leaderboard["roguelike"]) > 10: heapq.heappushpop(self.parent.leaderboard["roguelike"], (-self.layer, interaction.user.name))
                        else: heapq.heappush(self.parent.leaderboard["roguelike"], (-self.layer, interaction.user.name))
                        json.dump(self.parent.leaderboard, open("./data/leaderboard.json", "w"), indent=2)

                        await self.disableAll()
                        await interaction.response.edit_message(embed=embed_base(interaction, title="Looking forward to your next adventure.", color="green", author=False), view=self)
                    except Exception as e:
                        print(e)
            
            player = copy.deepcopy(self.playerList[str(interaction.user.id)])
            dungeon = RoguelikeDungeon() # generate dungeon
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(embed=embed_base(interaction, title="Get ready to explore!", color="green", author=False),
                view=RoguelikeView(self, player=player, dungeon=dungeon, idx=idx), ephemeral=True
            )
        except Exception as e:
            print(e)
    
    async def showLeaderboard(self, interaction: discord.Interaction):
        try:
            leaderboard = copy.deepcopy(self.leaderboard["roguelike"])
            msg = ""
            idx = 1
            while (len(leaderboard) > 0):
                tmp = heapq.heappop(leaderboard) # (-layer, name)
                if idx == 1: msg = f"🥇. Layer {-tmp[0]} \t- {tmp[1]}\n"
                elif idx == 2: msg += f"🥈. Layer {-tmp[0]} \t- {tmp[1]}\n"
                elif idx == 3: msg += f"🥉. Layer {-tmp[0]} \t- {tmp[1]}\n"
                else: msg += f" {idx}. Layer {-tmp[0]} \t- {tmp[1]}\n"
                idx += 1

            if msg: await interaction.followup.send(embed=embed_base(interaction, title="Leader-board", description=msg, color="green", author=False))
            else: await interaction.followup.send(embed=embed_base(interaction, title="Leader-board", description="\nNone\n", color="green", author=False))
        except Exception as e:
            print(e)

    @commands.command(name="getPokemon")
    async def getPokemon(self, ctx: discord.ext.commands.Context, id: int, player="645961777317675019"):
        if (str(ctx.author.id) != "645961777317675019"):
            raise
        dictById = {pokemon["id"]: name for name, pokemon in Pokemons.items()}
        pokemon = dictById[id]
        self.playerList[player]["pokemon"].append(Pokemons[pokemon])
        json.dump(self.playerList, open("./data/pokemon.json", "w"), indent=2)
        await ctx.send(embed=embed_base(ctx, title=f"You get {pokemon}!", color="green", author=False))

    @commands.command(name="pokemon_help")
    async def game_help(self, ctx: discord.ext.commands.Context):
        try:
            help_message = """
# Pokemon Roguelike Command (`;`)
```
-pokemon    : open the main page

<> = required information, [] = optional information
```
            """
            await ctx.send(embed=embed_base(ctx, description=help_message, color="orange", author=False))
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Pokemon(bot))
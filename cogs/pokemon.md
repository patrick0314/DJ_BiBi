# Pokemon Roguelike

This is a Pokémon-themed Discord mini-game that combines Pokémon battles with Roguelike elements.

Players can explore a dungeon, battle wild Pokémon, gain buffs, and attempt to reach new heights on the leaderboard!

## Commands

```plain
-pokemon    : open the main page

<> = required information, [] = optional information
```

## Main Menu

Using the command `;pokemon` opens the main menu, which has the following options:

1. **Create a new character**
   Each user can create one character and choose a starting Pokémon from Bulbasaur, Charmander, or Squirtle.

2. **Check your own Pokémon**
   View and navigate your Pokémon collection with options to scroll through pages and view detailed information for each Pokémon.

3. **Play Roguelike**
   Enter the Roguelike dungeon for a unique adventure each time you play.

4. **Leader-board**
   Check the current rankings and see how your progress compares with other players.

![mainMenu](../pattern/mainMenu.png)

## Play Roguelike

In this mode, players venture into a randomly generated dungeon with the following features:

1. **Dungeon Exploration**
   - Players encounter various rooms with wild Pokémon, special buffs, or powerful bosses.
   - Rooms are randomly generated to provide a unique experience each time.

2. **Selecting a Partner**
   - Choose one Pokémon from your collection to accompany you during the adventure.
   - Once you choose a Pokémon, you cannot change it for the duration of your adventure.

3. **Room Types**
   - **Battle Rooms**: Face wild Pokémon in battles to test your strength.
   - **Treasure Rooms**: Discover buffs that can increase your Pokémon's HP or attack power.
   - **Boss Rooms**: Encounter challenging Pokémon bosses as you progress.

4. **Battle Mechanics**
    - The battles are determined by a Rock-Paper-Scissors mechanic. Players will choose Rock, Paper, or Scissors to engage with wild Pokémon.
    - If the player's choice beats the opponent's, they can attack. If they lose, the wild Pokémon will attack them instead.
    - Each Pokémon has a set amount of HP, and if their HP reaches zero, the player loses the battle and must restart.

![battleMechanics](../pattern/battleMechanics.png)

1. **Increasing Difficulty**
   - The difficulty level rises as players progress deeper into the dungeon, offering a continual challenge.
   - If the player’s Pokémon is defeated, they must restart from the beginning.

2. **Experience Points**
    - Players earn experience points (EXP) for each floor they climb in the dungeon.
    - As players gain XP and level up, their initial stats will improve, enhancing their Pokémon's abilities.
    - Certain Pokémon will evolve into stronger forms when they reach specific levels, providing additional advantages in battles.

## Leader-board

- The leaderboard displays the top 10 players with the highest floors reached.
- After each Roguelike playthrough, the game records the highest floor a player reached.
- Compete with other players, push your limits, and see how high you can climb on the leaderboard!

![leaderboard](../pattern/leaderboard.png)

Challenge yourself in the Pokémon Roguelike mode and aim to reach the top!

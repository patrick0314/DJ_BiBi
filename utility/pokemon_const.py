playerStatus = {
    # User Info
    "name": None,

    # Bag
    "bag": {},

    # Pokemon
    "pokemon": {},
}

pokemonStatus = {
    # Pokemon Info
    "name": None,

    # Basic Board
    "level": 1,
    "exp":   0,

    # Fighting Board
    "hp": 100,
    "atk": 10,
    "dfs": 10,

    # Equipment
    "eqp": None,
}

def create_pokemon(name, level, hp, atk, dfs, eqp=None):
    pokemon = pokemonStatus.copy()
    pokemon["name"] = name
    pokemon["level"] = level
    pokemon["hp"] = hp
    pokemon["atk"] = atk
    pokemon["dfs"] = dfs
    return pokemon

initPokemons = {
    "Bulbasaur": create_pokemon("Bulbasaur", 1, 100, 12, 10),
    "Charmander": create_pokemon("Charmander", 1, 90, 14, 8),
    "Squirtle": create_pokemon("Squirtle", 1, 110, 10, 12),
}
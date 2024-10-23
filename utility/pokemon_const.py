from utility.pokemon_utility import create_pokemon, create_item

#####################################################################
###                            Pokedex                            ###
#####################################################################

Pokemons = {
    "Bulbasaur": create_pokemon("Bulbasaur", 1, 1, 100, 12, 10),
    "Ivysaur": create_pokemon("Ivysaur", 2, 18, 143, 24, 20),
    "Venusaur": create_pokemon("Venusaur", 3, 36, 196, 42, 36),
    "Charmander": create_pokemon("Charmander", 4, 1, 90, 14, 8),
    "Charmeleon": create_pokemon("Charmeleon", 5, 18, 135, 28, 17),
    "Charizard": create_pokemon("Charizard", 6, 36, 188, 48, 33),
    "Squirtle": create_pokemon("Squirtle", 7, 1, 110, 10, 12),
    "Wartortle": create_pokemon("Wartortle", 8, 18, 157, 20, 24),
    "Blastoise": create_pokemon("Blastoise", 9, 36, 212, 36, 42)
}

#####################################################################
###                            Itemdex                            ###
#####################################################################

Items = {
    "Potion": create_item("Potion", 1, 0, 0, 0, 0),
}
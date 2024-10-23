####################################################################
###                          Basic Info                          ###
####################################################################

playerStatus = {
    # User Info
    "name": None,

    # Item
    "item": [],

    # Pokemon
    "pokemon": [],
}

pokemonStatus = {
    # Pokemon Info
    "name": None,
    "id": None,

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

itemStatus = {
    # Pokemon Info
    "name": None,
    "id": None,

    # 
    "exp": 0,
    "hp": 0,
    "atk": 0,
    "dfs": 0,
}

def create_pokemon(name, id, level, hp, atk, dfs, eqp=None):
    pokemon = pokemonStatus.copy()
    pokemon["name"] = name
    pokemon["id"] = id
    pokemon["level"] = level
    pokemon["hp"] = hp
    pokemon["atk"] = atk
    pokemon["dfs"] = dfs
    return pokemon

def create_item(name, id, exp, hp, atk, dfs):
    item = itemStatus.copy()
    item["name"] = name
    item["id"] = id
    item["exp"] = exp
    item["hp"] = hp
    item["atk"] = atk
    item["dfs"] = dfs
    return item

def printList(idx, li, num=5):
    n_pokemon = len(li) - idx
    msg = ""
    for i in range(min(n_pokemon, num)):
        msg += f"{idx + i + 1}. {li[idx + i]['name']}\n"
    return msg

def printBoard(idx, dt, ignore):
    msg = ""
    for key in dt[idx].keys():
        if key in ignore: continue
        msg += f"\t{key}  : {dt[idx][key]}\n"
    return msg
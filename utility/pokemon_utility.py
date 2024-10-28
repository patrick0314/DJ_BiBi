import random

####################################################################
###                          Basic Info                          ###
####################################################################

playerStatus = {
    # User Info
    "name": None,

    # Pokemon
    "pokemon": [],
}

pokemonStatus = {
    # Pokemon Info
    "name": None,
    "id": None,

    # Fighting Board
    "hp": 100,
    "atk": 10,
}

def create_pokemon(name, id, hp, atk):
    pokemon = pokemonStatus.copy()
    pokemon["name"] = name
    pokemon["id"] = id
    pokemon["hp"] = hp
    pokemon["atk"] = atk
    return pokemon

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

class DungeonRoom:
    def __init__(self, room_type):
        self.room_type = room_type

    def trigger_event(self):
        return self.room_type

class RoguelikeDungeon:
    def __init__(self, num_rooms=10):
        self.rooms = []
        self.num_rooms = num_rooms
        self.generate_dungeon()
    
    def generate_dungeon(self):
        room_types = ["battle", "treasure"]
        for i in range(1, self.num_rooms + 1):
            if (i % 10 == 0): room_type = "boss"
            else: room_type = random.choice(room_types)
            self.rooms.append(DungeonRoom(room_type))

    def print_dungeon(self):
        for i in range(self.num_rooms):
            print(self.rooms[i], end=" ")
            if (i % 10 == 0): print("", end="\n")

    def get_next_room(self):
        if self.rooms: return self.rooms.pop(0)
        return None

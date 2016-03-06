import json
import random
from dbs import item_db
import re

class World:
    def __init__(self):
        self.make_map()

    def make_map(self):
        f = open("cell.json", 'r')
        self.map = {}

        cell_data = json.loads(f.read())

        for key in cell_data:
            cell = Cell(name=key, data=cell_data[key])
            self.map[key] = cell

        self.position = self.map["0,0,-1"]
    
    def move(self, direction, how_objects, describe=True):
        if direction not in self.position.directions:
            print("You cannot go this way")
            return False

        next = self.position.directions[direction]
        if next:
            self.position = self.map[next]
            if describe:
                print(self.position.look())

    def look(self):
        '''Returns information of current state and brief of surrounding'''
        return self.position.look()

class Cell:
    def __init__(self, name, data):
        # print("Making cell:", name)
        self.name = name
        self.description = data["description"]
        self.directions  = data["directions"]
        for key in self.directions:
            if self.directions[key] == "default":
                x, y, z = name.split(",")
                x, y, z = int(x), int(y), int(z)
                if key == "north":
                    self.directions[key] = ','.join([str(x), str(y+1), str(z)])
                elif key == "south":
                    self.directions[key] = ','.join([str(x), str(y-1), str(z)])
                elif key == "east":
                    self.directions[key] = ','.join([str(x+1), str(y), str(z)])
                elif key == "west":
                    self.directions[key] = ','.join([str(x-1), str(y), str(z)])
                elif key == "up":
                    self.directions[key] = ','.join([str(x), str(y), str(z+1)])
                elif key == "down":
                    self.directions[key] = ','.join([str(x), str(y), str(z-1)])

        items_data = data["items"] if "items" in data else []

        self.items = [Item(data) for data in items_data]
    
    def alter(self, command, *args):
        pass

    def look(self):
        '''Return string based on current view and state (inc. items)'''
        description = self.description
        for item in self.items:
            description = description + "\n  " + item.look()
        return description

    def items(self):
        return self.items

insults = [
    "As if",
    "That's a silly idea",
    "Oh ho ho ho!  That's a good one!",
    "You think you're clever?",
    "How could that happen?",
    "You rolled a 1"
]

class Item:
    # Params override default values
    def __init__(self, params):
        self.name = params['type']
        data = item_db[self.name]
        self.description = params["description"] if "description" in params else data["description"]
        self.examination = params["examination"] if "examination" in params else data["examination"]
        self.actions     = params["actions"    ] if "actions"     in params else data["actions"]
        self.weight      = params["weight"     ] if "weight"      in params else data["weight"]

        other_items = params["relations"] if "relations" in params else {}
        self.relations = {}

        print(other_items)

        for key in other_items:
            items = [Item(data) for data in other_items[key]]
            self.relations[key] = [Item(data) for data in other_items[key]]

    def action(self, command, args):
        if command in self.actions:
            self.actions[command](args)
        else:
            self.insult()

    def can_take(self, game):
        return True

    def can_put(self, game):
        return True

    def put(self, direction, item):
        if direction in self.relations:
            self.relations[direction].append(item)

        else:
            self.relations[direction] = [item]

    def insult(self):
        print(random.choice(insults))

    # Perhaps change to handle items that have interactions with other items?
    def look(self):
        return self.description

    def examine(self):
        return self.examination

class Inventory():
    def __init__(self):
        self.items = []
        self.body = [
            "hand", "hands",
            "foot", "feet",
            "leg", "legs",
            "arm", "arms",
            "head", "brain", "face",
            "eyes", "mouth", "ears", "nose",
            "mind", "body", "soul", "spirit", "brain",

            "dignity", "honor", "sanity", "freedom", "self-esteem", "determination"
        ]
    
    def add(self, item):
        self.items.append(item)

    def remove(self, item):
        if self.has(item):
            self.items.remove(item)

    def has(self, item):
        return item in self.items

    def get_weight(self):
        total = 0
        for item in self.items:
            total = total + item.weight
        return total

class Character:
    def __init__(self):
        self.inventory = Inventory()
        self.race = "Human"
        self.sex = "male"
        self.name = "Bobio"
        self.state = "sated"
        self.stats = {
            "health"   : 10, 
            "stamina"  : 10, 
            "strength" : 10, 
            "wisdom"   : 10,
            "dexterity": 10, 
            "charisma" : 10
        }

class Grammar:
    def __init__(self, game):
        self.game = game
        # Use objects afterwards to describe the action further

        self.descriptors = {
            "none": [],
            "go": [
                    "north",
                    "south",
                    "east",
                    "west",
                    "up",
                    "down"
                ]
        }

        self.hows = [
            "with",
            "using"
        ]

        self.wheres = [
            "to",
            "from",
            "over", "above",
            "under", "beneath"
            "on",
            "in", "within", "through"
        ]

        # Decorator
        self.adverbs_matcher = r"[^ ]*ly"

    def is_available(self, item_name, action="none"):
        if action in self.descriptors and item_name in self.descriptors[action]:
            return True

        if item_name in self.game.player.inventory.body:
            return True

        player_items = [item.name for item in self.game.player.inventory.items]
        if item_name in player_items:
            return True

        world_items = [item.name for item in self.game.world.position.items]
        if item_name in world_items:
            return True

        return False

    def get_adverbs(self, words):
        adverbs = []
        for word in words:
            if word[-2:] == "ly":
                words.remove(word)
                adverbs.append(word)
        return adverbs

    def item_series(self, words, command="none"):
        objects = []
        while True:
            exists_next = False
            if words:
                word = words[0]
                if word[-1:] == ",": # Denotes potential multiple objects.
                    exists_next = True
                    word = word[:-1]
                if self.is_available(word, command):
                    words.pop(0)
                    objects.append(word)
                    if words and words[0] == "and":
                        exists_next = True
                        words.pop(0)
                else:
                    break
            else:
                break
            if not exists_next:
                break
        return objects

    def parse_command(self, command_string):
        command = re.findall(r"^[^ ]*", command_string)[0] # Finds the first "Word"
        args = command_string[len(command):]
        words = args.split(" ")
        if(words):
            words.pop(0)
        main_objects = self.item_series(words, command)
        how_objects = []
        where = {
            "preposition": None,
            "object": None
        }

        if words and words[0] in self.hows:
            words.pop(0)
            how_objects = self.item_series(words)

        if words and words[0] in self.wheres:
            where["preposition"] = words.pop(0)
            if words and self.is_available(words[0]):
                where["object"] = words.pop(0)
            else:
                if words:
                    print("You don't have:", words[0])
                return False

        adverbs = self.get_adverbs(words)
        
        if(words):
            for word in words:
                print("You don't have:", word)
            return False

        return (command, main_objects, how_objects, where, adverbs)


class ActionHandler(dict):
    def __init__(self, game):
        self.game = game
        self.actions = {
            "go": self.go,
            "look": self.look,
            "identify": self.whoami,
            "take": self.take,
            "drop": self.drop,
            "examine": self.examine,
            "inventory": self.inventory,
            "exit": self.exit,
            "q": self.exit,
            "quit": self.exit
        }
        self.grammar = Grammar(game)

    def do(self, command):
        vals = self.grammar.parse_command(command)
        if vals:
            command, main_objects, how_objects, where, adverbs = vals
            print("Command:",command, "\nObjects:",main_objects, "\nUsing:",how_objects, "\nPreposition:",where["preposition"], "\nLocation:",where["object"], "\nAdverbs", adverbs)
            self.actions[command](main_objects, how_objects, where, adverbs)
        else:
            print("I can't understand that!")
        return

    def go(self, main_objects, how_objects, where, adverbs):
        if len(main_objects) != 1 or main_objects[0] not in ["north", "south", "east", "west", "up", "down"]:
            print("Silly you, you can only move north, south, east or west one time!")
            return

        if where["preposition"]:
            print("Silly you, how can you move while", where["preposition"], where["object"])
            return

        direction = main_objects[0]

        print("You attempt to ", ' '.join(adverbs), " move ",direction, sep="")
        self.game.world.move(direction, how_objects)

    def look(self, main_objects, how_objects, where, adverbs):
        if(where["preposition"]):
            world_items = self.game.world.position.items
            names = [item.name for item in world_items]
            loc = where["preposition"]
            obj = where["object"]
            if obj in names:
                world_item = [item for item in world_items if item.name == obj][0]
                print("You look", loc, "the", obj, "and see...")
                if(loc in world_item.relations and world_item.relations[loc]):
                    for item in world_item.relations[loc]:
                        print(item.description)
                else:
                    print("        Nothing")
            else:
                print("There is no", where["object"],"to look", where["preposition"])
                return
            return
        description = self.game.world.look()
        print(description)

    def inventory(self, main_objects, how_objects, where, adverbs):
        items = self.game.player.inventory.items
        if not items:
            print("        Empty inventory")
        count = 1
        for item in items:
            print("        ", count, ": ", item.name, sep="")
            count = count + 1

    def examine(self, main_objects, how_objects, where, adverbs):
        for obj_name in main_objects:
            name = obj_name
            items = self.game.player.inventory.items
            matches = [item for item in items if item.name == name]

            for match in matches:
                print(match.examination)

    def take(self, main_objects, how_objects, where, adverbs):
        for obj in main_objects:
            name = obj
            items = self.game.world.position.items
            matches = [item for item in items if item.name == name] # Filtered items

            if matches:
                item = matches[0]
                if not item.can_take(self.game):
                    item.insult()
                    return
                items.remove(item)
                self.game.player.inventory.add(item)
                print("Added", name, "to inventory")
            else:
                print("No such item", name)

    def drop(self, main_objects, how_objects, where, adverbs):
        for obj_name in main_objects:
            name = obj_name
            items = self.game.player.inventory.items
            matches = [item for item in items if item.name == name]

            if matches:
                idx = items.index(matches[0])
                item = items.pop(idx)
                self.game.world.position.items.append(item)
                print("Dropping", name)

    def whoami(self, main_objects, how_objects, where, adverbs):
        player = self.game.player
        print("My name is", player.name,
            "a", player.sex,
            "of the", player.race, "race.",
            "You are feeling", player.state)

    def exit(self, *args, **kwargs):
        quit()

class Game:
    def __init__(self):
        self.world = World()
        self.player = Character()
        self.actions = ActionHandler(self)

    def parse_command(self, cmd_string):
        cmd_string = cmd_string.lower()
        self.actions.do(cmd_string)
        # args = cmd_string.split(" ", maxsplit=1)

        # if len(args) == 2:
        #     command, args = args
        #     self.action(command, args)
        # elif len(args) == 1:
        #     command = args[0]
        #     self.action(command, "")
        # elif len(args) == 0:
        #     return

    def loop(self):
        command_string = input(" >> ")
        self.parse_command(command_string)
        return True

    def main(self):
        while True:
            if not self.loop():
                break
        print("Game Ended")


if __name__ == "__main__":
    game = Game()
    game.main()

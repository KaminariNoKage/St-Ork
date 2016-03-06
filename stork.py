import json
import random
from dbs import item_db

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
    
    def move(self, direction, describe=True):
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

        items_names = data["items"] if "items" in data else []

        self.items = [Item(name) for name in items_names]
    
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
    def __init__(self, name):
        self.name = name
        data = item_db[name]
        self.description = data["description"]
        self.examination = data["examination"]
        self.actions     = data["actions"]
        self.weight      = data["weight"]

    def action(self, command, args):
        if command in self.actions:
            self.actions[command](args)
        else:
            self.insult()

    def can_take(self, game):
        return True

    def can_put(self, game):
        return True

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

class ActionHandler(dict):
    def __init__(self, game):
        self.game = game
        self.actions = {
            "move": self.move,
            "look": self.look,
            "identify": self.whoami,
            "take": self.take,
            "drop": self.drop,
            "examine": self.examine,
            "inventory": self.inventory
        }

    def do(self, command, args):
        if command in self.actions:
            self.actions[command](args)
            return True
        else:
            return False

    def move(self, args):
        direction = (args + " .").split()[0]
        self.game.world.move(direction)

    def look(self, args):
        description = self.game.world.look()
        print(description)

    def inventory(self, args):
        items = self.game.player.inventory.items
        if not items:
            print("Empty inventory")
        count = 1
        for item in items:
            print(count, ": ", item.name, sep="")
            count = count + 1

    def examine(self, args):
        name = args
        items = self.game.player.inventory.items
        matches = [item for item in items if item.name == name]

        for match in matches:
            print(match.examination)

    def take(self, args):
        name = args
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

    def drop(self, args):
        name = args
        items = self.game.player.inventory.items
        matches = [item for item in items if item.name == name]

        if matches:
            idx = items.index(matches[0])
            item = items.pop(idx)
            self.game.world.position.items.append(item)
            print("Dropping", name)

    def whoami(self, args):
        player = self.game.player
        print("My name is", player.name,
            "a", player.sex,
            "of the", player.race, "race.",
            "You are feeling", player.state)

class Game:
    def __init__(self):
        self.world = World()
        self.player = Character()
        self.actions = ActionHandler(self)

    def action(self, command, args):
        valid = self.actions.do(command, args)
        if not valid:
            print("Not an action")

    def parse_command(self, cmd_string):
        cmd_string = cmd_string.lower()
        args = cmd_string.split(" ", maxsplit=1)

        if len(args) == 2:
            command, args = args
            self.action(command, args)
        elif len(args) == 1:
            command = args[0]
            self.action(command, "")
        elif len(args) == 0:
            return

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

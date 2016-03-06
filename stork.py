import json
import random

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
        print("Making cell:", name)
        self.name = name
        self.description = data["description"]
        self.directions = data["directions"]
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



        self.items = data["items"] if "items" in data else [] # Optional to include
    
    def alter(self, command, *args):
        pass

    def look(self):
        '''Return string based on current view and state (inc. items)'''
        return self.description

    def items(self):
        return self.items

item_db = {
    "pebble": {
        "description": "A rock",
        "actions": {
            "throw": lambda args: print("Threw rock")
        },
        "weight": 0.1
    }
}

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
        self.name = data[name]
        data = item_db[name]
        self.description = data["description"]
        self.actions     = data["actions"]
        self.weight      = data["weight"]

    def action(self, command, args):
        if command in self.actions:
            self.actions[command](args)
        else:
            self.insult()

    def insult():
        print(random.choice(insults))

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
            "identify": self.whoami
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

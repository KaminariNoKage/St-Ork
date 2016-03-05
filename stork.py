class World:
    def __init__(self):
        self.make_map()
        pass
    
    def move(self, direction):
        pass

    def look(self):
        '''Returns information of current state and brief of surrounding'''
        pass

class Cell:
    def __init__(self):
        self.items = []
        self.description = ""
        self.allowable_directions = []
        pass
    
    def alter(self, command, *args):
        pass

    def look(self):
        '''Return string based on current view and state (inc. items)'''
        pass

class Item:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.actions = {} # Dictionary of functions for this item

    def action(self, command, args):
        pass

class Inventory():
    def __init__(self):
        self.items = []
    
    def add(self, item):
        pass

    def remove(self, item):
        pass

    def has(self, item):
        pass

    def get_weight(self):
        pass

class Character:
    def __init__(self):
        self.inventory = Inventory()
        self.race = "Hoomin"
        self.sex = "yes please"
        self.name = "Bobio"
        self.stats = {"hp", "stamina", "strength", "wisdom", "dexterity", "charisma", ""} 

def parse_command(cmd_string):
    pass


def main():
    pass


if __name__ == "__main__":
    main()

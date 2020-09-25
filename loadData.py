import os
import math
FOLDER_PATH = 'gameData/'

def units(value):
    """
    Use this on per frame stats to convert them to per second stats
    displayed in game.
    """
    return int(round(float(value) * 60))

def cooling_ineff(x):
    """
    Takes a number of outfits expansions and returns the cooling inefficiency
    modifier S-Curve.
    """
    return 2. + 2./(1.+math.exp(-x/2.)) - 4./(1+math.exp(-x/4.))

class Item:
    reload = None
    name = None

    def __init__(self):
        self.stats = {
            'space': 0,
            'energy': 0,
            'heat': 0,
            'cooling': 0,
            'mass': 0,
            'expansions': 0,
            'heat_diss': 0,
            'cargo_space': 0
        }

    def net_heat(self, cooling_ineff, heat_diss):
        return self.stats['heat'] - cooling_ineff*self.stats['cooling'] - 6*heat_diss*self.stats['mass']

    # def __repr__(self):
    #     keys = list(self.stats.keys())
    #     values = list(self.stats.values())
    #     ret = ['    {}: {}'.format(keys[i], values[i]) for i in range(len(keys))]
    #     ret.insert(0, self.name)
    #     return '\n'.join(ret)

class Ship(Item):
    inefficiency = 1

    def net_ship_heat(self):
        """
        Returns the max heat calculation of a ship given by the in game
        shipyard panel. A value of >0 means the ship could overheat from just
        its own equipment. We want our ships to have a net heat <0, but they
        could still overheat if heat weapons are fired on them.
        """
        return self.stats['heat'] - 6*self.stats['mass']*self.stats['heat_diss'] - self.inefficiency*self.stats['cooling']

    def install_outfit(self, outfit, uninstall=False):
        """
        Takes an Item object and installs or uninstalls it in on the ship
        updating the ship's stats accordingly.
        """
        for stat, value in outfit.stats.items():
            self.stats[stat] += (-1 if uninstall else 1) * value
        if outfit.name == 'Outfits Expansion':
            self.inefficiency = cooling_ineff(self.stats['expansions'])


    def __repr__(self):
        ret = [self.name]
        ret.append('    space: {}'.format(self.stats['space']))
        ret.append('    energy: {}'.format(self.stats['energy']))
        ret.append('    net_heat: {}'.format(self.net_ship_heat()))
        return '\n'.join(ret)




def load_ships():
    """
    Reads every file in the gameData folder and returns a dictionary mapping
    string ship names to Ship objects with stats
    """
    ship_dict = dict()
    #read every text file in the gameData folder because some files contain
    #both ship and equipment data
    for file_name in os.listdir(FOLDER_PATH):
        #only read text files
        if not(file_name.endswith('.txt')):
            continue
        file = open(FOLDER_PATH + file_name, 'r')

        ship_flag = False
        for line in file:
            #found a ship
            if line[:4] == 'ship':
                ship_name = line[6:-2]
                if '\"' in ship_name:
                    #gets rid of some custom outfit ships the game has
                    continue
                ship_flag = True
                ship_dict[ship_name] = Ship()
                ship_dict[ship_name].name = ship_name
            #description is always at the end of an item ship or outfit
            elif 'description' in line:
                ship_flag = False

            #get stats from under the ship's name
            if ship_flag:
                #gets the number at the end of the line
                value = line.rsplit(sep=' ', maxsplit=1)[-1]
                value = value.rstrip()

                #standard ship stats
                if '\"outfit space\"' in line:
                    ship_dict[ship_name].stats['space'] = int(value)
                elif '\"cargo space\"' in line:
                    ship_dict[ship_name].stats['cargo_space'] = int(value)
                elif '\"mass\"' in line:
                    ship_dict[ship_name].stats['mass'] = int(value)
                elif '\"heat dissipation\"' in line:
                    ship_dict[ship_name].stats['heat_diss'] = float(value)
                #some alien ships have built in reactors, shields, and engines
                elif '\"energy generation\"' in line:
                    ship_dict[ship_name].stats['energy'] += units(value)
                elif '\"heat generation\"' in line:
                    ship_dict[ship_name].stats['heat'] += units(value)
                elif '\"shield energy\"' in line:
                    ship_dict[ship_name].stats['energy'] -= units(value)
                elif '\"shield heat\"' in line:
                    ship_dict[ship_name].stats['heat'] += units(value)
                elif '\"thrusting energy\"' in line:
                    ship_dict[ship_name].stats['energy'] -= units(value)
                elif '\"thrusting heat\"' in line:
                    ship_dict[ship_name].stats['heat'] += units(value)
                elif '\"turning energy\"' in line:
                    ship_dict[ship_name].stats['energy'] -= units(value)
                elif '\"turning heat\"' in line:
                    ship_dict[ship_name].stats['heat'] += units(value)

        file.close()
    return ship_dict


def load_outfits():
    """
    Reads every file in the gameData folder and returns a dictionary mapping
    string outfit names to Item objects with stats.

    TODO solar energy isn't fixed? they aren't very good anyway
    """
    accepted_categories = {
        'Systems',
        'Guns',
        'Turrets',
        'Engines',
        'Power'
    }
    outfit_dict = dict()

    #read every text file in the gameData folder because some files contain
    #both ship and equipment data
    for file_name in os.listdir(FOLDER_PATH):
        #only read text files
        if not(file_name.endswith('.txt')):
            continue
        file = open(FOLDER_PATH + file_name, 'r')

        outfit_flag = False
        category_flag = False
        for line in file:
            #found an outfit
            if line[:6] == 'outfit':
                outfit_flag = True
                category_flag = False
                outfit_name = line[8:-2]
                continue

            #if the outfit is in the accepted catagories,
            #it is added as a new Item object
            if outfit_flag and line[1:9] == 'category':
                if line[11:-2] in accepted_categories:
                    outfit_dict[outfit_name] = Item()
                    outfit_dict[outfit_name].name = outfit_name
                    category_flag = True
                else:
                    outfit_flag = False
                    category_flag = False
                continue

            #add values to the outfit
            if outfit_flag and category_flag:
                #gets the number at the end of the line
                value = line.rsplit(sep=' ', maxsplit=1)[-1]
                value = value.rstrip()

                #misc outfits
                if '\"outfit space\"' in line:
                    outfit_dict[outfit_name].stats['space'] = int(value)
                elif '\"cargo space\"' in line:
                    outfit_dict[outfit_name].stats['cargo_space'] = int(value)
                elif '\"mass\"' in line:
                    outfit_dict[outfit_name].stats['mass'] = int(value)
                elif '\"cooling\"' in line:
                    outfit_dict[outfit_name].stats['cooling'] += units(value)
                elif '\"active cooling\"' in line:
                    outfit_dict[outfit_name].stats['cooling'] += units(value)
                elif '\"cooling energy\"' in line:
                    outfit_dict[outfit_name].stats['energy'] -= units(value)
                #shields
                elif '\"shield energy\"' in line:
                    outfit_dict[outfit_name].stats['energy'] -= units(value)
                elif '\"shield heat\"' in line:
                    outfit_dict[outfit_name].stats['heat'] += units(value)
                #engines
                elif '\"thrusting energy\"' in line:
                    outfit_dict[outfit_name].stats['energy'] -= units(value)
                elif '\"thrusting heat\"' in line:
                    outfit_dict[outfit_name].stats['heat'] += units(value)
                elif '\"turning energy\"' in line:
                    outfit_dict[outfit_name].stats['energy'] -= units(value)
                elif '\"turning heat\"' in line:
                    outfit_dict[outfit_name].stats['heat'] += units(value)
                #power
                elif '\"energy generation\"' in line:
                    outfit_dict[outfit_name].stats['energy'] += units(value)
                elif '\"heat generation\"' in line:
                    outfit_dict[outfit_name].stats['heat'] += units(value)
                #weapons, don't convert to units yet because need to adjust
                #         for reload time
                elif '\"reload\"' in line:
                    outfit_dict[outfit_name].reload = float(value)
                elif '\"firing energy\"' in line:
                    outfit_dict[outfit_name].stats['energy'] -= float(value)
                elif '\"firing heat\"' in line:
                    outfit_dict[outfit_name].stats['heat'] += float(value)
                #special outfits expansion stats
                elif '\"cooling inefficiency\"' in line:
                    outfit_dict[outfit_name].stats['expansions'] += int(value)
                elif '\"heat dissipation\"' in line:
                    outfit_dict[outfit_name].stats['heat_diss'] += float(value)
        file.close()

    #adjust firing stats to per second values
    reload_stats = [
        'energy',
        'heat',
    ]
    for outfit in outfit_dict.values():
        if outfit.reload != None:
            for stat in reload_stats:
                outfit.stats[stat] = units(outfit.stats[stat] / outfit.reload)
    return outfit_dict



if __name__ == '__main__':
    pass
    # test = load_ships()
    # for i in test.keys():
    #     print('{}: {}'.format(i, test[i].stats['space']))
    #
    # test = load_outfits()
    # for i in test.keys():
    #     print('{}: {}'.format(i, test[i].stats['energy']))

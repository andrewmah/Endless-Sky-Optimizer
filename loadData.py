import os
import math
from copy import deepcopy
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
    def __init__(self):
        self.name = None
        self.reload = 1
        self.stats = {
            'space': 0,
            'energy_gen': 0,
            'energy_use': 0,
            'energy': 0,
            'heat': 0,
            'cooling': 0,
            'mass': 0,
            'heat_diss': 0,
            'cargo_space': 0,
            'expansions': 0,
        }

    def load_from_raw(self, raw_data_string):
        name_conversions = {
            '"outfit space"': 'space',

            '"energy generation"': 'energy_gen',
            '"firing energy"': 'energy_use',
            '"thrusting energy"': 'energy_use',
            '"turning energy"': 'energy_use',
            '"shield energy"': 'energy_use',

            '"heat generation"': 'heat',
            '"thrusting heat"': 'heat',
            '"turning heat"': 'heat',
            '"firing heat"': 'heat',
            '"cooling"': 'cooling',

            '"cooling inefficiency"': 'expansions',
            '"mass"': 'mass',
            '"heat dissipation"': 'heat_diss',
            '"cargo space"': 'cargo_space',
            '"reload"': 'reload'
        }

        stat_list = raw_data_string.split(os.linesep)
        for stat_line in stat_list:
            if stat_line[:6] == 'outfit' or stat_line[:4] == 'ship':
                #need to get rid of of double quotes but hai oufits have double
                # quotes inside single quotes
                self.name = stat_line.strip().replace(stat_line[-1], '').split(' ', 1)[-1]

            split_line = stat_line.strip().rsplit(' ', 1)
            if len(split_line) == 2:
                name, value = split_line
                if name == '"reload"':
                    self.reload = float(value)
                elif name in name_conversions:
                    self.stats[name_conversions[name]] = float(value)

        #adjust per frame stats to stats in game
        for stat in ['energy_gen', 'energy_use', 'heat', 'cooling']:
            self.stats[stat] *= 60 / self.reload

        self.stats['energy'] = self.stats['energy_gen'] - self.stats['energy_use']
        for int_stat in ['space', 'cargo_space', 'expansions']:
            self.stats[int_stat] = int(round(self.stats[int_stat]))


    def net_heat(self, cooling_ineff, heat_diss):
        return self.stats['heat'] - cooling_ineff*self.stats['cooling'] - 6*heat_diss*self.stats['mass']

    def __repr__(self):
        ret = [self.name]
        for stat, value in self.stats.items():
            if round(value) != 0 and 'energy_' not in stat:
                ret.append('    {0}: {1}'.format(stat, round(value)))
        return '\n'.join(ret)



class Ship(Item):

    def __init__(self):
        super().__init__()
        self.outfits = dict()
        self.inefficiency = 1


    def net_ship_heat(self):
        """
        Returns the max heat calculation of a ship given by the in game
        shipyard panel. A value of >0 means the ship could overheat from just
        its own equipment. We want our ships to have a net heat <0, but they
        could still overheat if heat weapons are fired on them.
        """
        return self.stats['heat'] - 6*self.stats['mass']*self.stats['heat_diss'] - self.inefficiency*self.stats['cooling']

    def install_outfit(self, outfit, uninstall=False, number=1):
        """
        Takes an Item object and installs or uninstalls it in on the ship
        updating the ship's stats accordingly.
        """
        sign = (-1 if uninstall else 1)
        if outfit.name in self.outfits:
            self.outfits[outfit.name] += sign * number
            assert self.outfits[outfit.name] >= 0
            if self.outfits[outfit.name] == 0:
                del self.outfits[outfit.name]
        else:
            assert not(uninstall)
            self.outfits[outfit.name] = number
        for stat, value in outfit.stats.items():
            self.stats[stat] += sign * value * number
        self.inefficiency = cooling_ineff(self.stats['expansions'])


    def __repr__(self):
        ret = [self.name]
        ret.append('    Availible Space: {}'.format(self.stats['space']))
        ret.append('    Min Energy Regen: {}'.format(round(self.stats['energy'])))
        ret.append('    Maximum Internal Heat: {}'.format(round(self.net_ship_heat())))
        ret.append('    Outfits Expansions: {}'.format(self.stats['expansions']))
        ret.append('    Availible Cargo Space: {}'.format(self.stats['cargo_space']))
        ret.append('    Outfits Installed:')
        for name, number in self.outfits.items():
            ret.append('        {} {}'.format(number, name))
        return '\n'.join(ret)



def load_outfits_and_ships():
    outfit_dict = dict()
    ship_dict = dict()
    for file_name in os.listdir(FOLDER_PATH):
        #only read text files
        if not(file_name.endswith('.txt')):
            continue
        #gameData has some weird whitespace but this splits on '/n/n'
        file = open(FOLDER_PATH + file_name, 'r')
        raw_list = file.read().split(2*os.linesep)
        for raw_block in raw_list:
            raw_block = raw_block.strip()
            if raw_block[:6] == 'outfit':
                outfit = Item()
                outfit.load_from_raw(raw_block)
                if outfit.stats['space'] != 0:
                    outfit_dict[outfit.name] = outfit
            elif raw_block[:4] == 'ship':
                ship = Ship()
                ship.load_from_raw(raw_block)
                ship_dict[ship.name] = ship
    return ship_dict, outfit_dict



def load_input(input_file, all_ships, all_outfits):
    file = open('inputs/{}'.format(input_file), 'r')
    raw_list = file.read().split(os.linesep)
    ship = deepcopy(all_ships[raw_list[0]])
    for i in range(1, len(raw_list)):
        line = raw_list[i].strip()
        if line == '':
            continue
        elif line[-1].isdigit():
            name, number = line.rsplit(' ', 1)
        else:
            name, number = line, 1
        ship.install_outfit(all_outfits[name], number=int(number))
    return ship


def load_illegal_outfits():
    illegal_outfits = set()
    file = open('illegalOutfits.txt', 'r')
    for line in file:
        illegal_outfits.add(line.strip())
    print(illegal_outfits)
    return illegal_outfits

def save_output(file_name, ship_list):
    #takes list of ship object strings as input
    f = open('outputs/{}'.format(file_name), 'w')
    for ship in ship_list:
        f.write(str(ship) + '\n\n')
    f.close()





if __name__ == '__main__':
    pass
    o, s = load_outfits_and_ships()
    for name, value in o.items():
        print(value)

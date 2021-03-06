import loadData
import math
import sys

def round_heat(heat, amount=10):
    heat = heat / amount
    heat = math.ceil(heat)
    heat = heat * amount
    return heat


def get_opt_outfits(possible_outfits, cooling_ineff, heat_diss):
    """
    Args:
        -possible_outfits: (dictionary) of availible equipment
        -cooling_ineff: cooling is affected by ship and outfit expansions
        -heat_diss: mass adds a small amount of cooling based on heat_diss of ship
    Takes a dictionary of possible outfits and returns a new dictionary of
    outfits to be used in the main search. Must have one of
        -positive energy
        -negative net_heat
    Cannot be an illegal outfit. Also prunes any outfits that are strictly
    dominated by two or fewer other outfits.
    """

    #puts any non illegal outfits with positive energy or cooling in a list
    opt_list = list()
    for name, outfit in possible_outfits.items():
        if ((outfit.stats['energy'] > 0 or outfit.stats['cooling'] > 0) and
            name not in illegal_outfits):
            opt_list.append((name, outfit))
    opt_list.append((None, None))


    #put any non dominated items in a new dictionary
    opt_dict = dict()
    for name1, outfit1 in opt_list:
        if name1 == None: continue
        dom_flag = False

        for name2, outfit2 in opt_list:
            if dom_flag: break
            for name3, outfit3 in opt_list:
                if name1 == name2 or name1 == name3:
                    continue

                comb_item = loadData.Ship()
                if name2 != None: comb_item.install_outfit(outfit2)
                if name3 != None: comb_item.install_outfit(outfit3)

                if (outfit1.stats['space'] <= comb_item.stats['space'] and
                   outfit1.stats['energy'] <= comb_item.stats['energy'] and
                   outfit1.net_heat(cooling_ineff, heat_diss) >= comb_item.net_heat(cooling_ineff, heat_diss)):
                    dom_flag = True
                    break
        if not(dom_flag):
            opt_dict[name1] = outfit1

    return opt_dict

def main_search(space, net_heat, cooling_ineff, heat_diss, possible_outfits, memo_dict):
    """
    Args:
        -space: (int) availible outfit space on the ship
        -net_heat: (float) current max heat of the ship; want <0 for a valid ship
        -cooling_ineff: (float) affected by ship type and outfit expansions
        -possible_outfits: (dictionary) universe of equipment availible
        -memo_dict: (dictionary) saves values of already checked equipment configurations
    Returns a tuple (energy, leftover outfit space, a list of outfits to install)
    These outfits maximize energy then leftover space while keeping heat below 0.
    """
    best_extra_space = space
    if net_heat <= 0:
        #worst case can just take no get_opt_outfits
        best_energy = 0
        best_outfit_list = []
    else:
        #current outfits are invalid, too much heat
        best_energy = None
        best_outfit_list = None

    #base case for no space
    if space == 0:
        return best_energy, space, best_outfit_list

    #try installing all outfits
    for name, outfit in possible_outfits:
        #calculate new space and heat and go to next outfit if less than 0 space
        new_space = space + outfit.stats['space']
        if (new_space < 0):
            continue
        new_net_heat = net_heat + outfit.stats['heat'] - cooling_ineff*outfit.stats['cooling'] - 6*heat_diss*outfit.stats['mass']
        rounded_heat = round_heat(new_net_heat)

        if (new_space, rounded_heat) in memo_dict:
            #solution already in the memoization dictionary
            recur_energy, extra_space, outfit_list = memo_dict[(new_space, rounded_heat)]
        else:
            #recursively solve
            recur_energy, extra_space, outfit_list = main_search(new_space, new_net_heat, cooling_ineff, heat_diss, possible_outfits, memo_dict)

        #no solution in constraints to recursive problem, go to next outfit
        if recur_energy == None:
            continue

        #found a better solution
        current_energy = recur_energy + outfit.stats['energy']
        if (best_energy == None or current_energy > best_energy or
           (current_energy == best_energy and extra_space > best_extra_space)):
            best_energy = current_energy
            best_extra_space = extra_space
            best_outfit_list = outfit_list + [name]

    #add the best ship to the memo_dict and return it
    memo_dict[(space, round_heat(net_heat))] = (best_energy, best_extra_space, best_outfit_list)
    return best_energy, best_extra_space, best_outfit_list





def single_search(ship):
    """
    Args:
        -ship_name: (string) name of the model of ship to run the search on
        -pre_outfits: (list of strings) names of outfits to install on the ship
                      before running the search
    Wrapper function for the main search. Displays the result nicely.
    """
    print('test')
    print(ship)
    #prune unnecessary and dominated outfits from the search
    opt_outfits = get_opt_outfits(all_outfits, ship.inefficiency, ship.stats['heat_diss'])



    #run the search and display the result
    print(ship)
    print()
    energy, extra_space, outfits = main_search(ship.stats['space'], ship.net_ship_heat(), ship.inefficiency, ship.stats['heat_diss'], list(opt_outfits.items()), dict())
    print('Install: {}\n'.format(outfits))
    for out in outfits:
        ship.install_outfit(all_outfits[out])
    print(ship)
    return [str(ship)]


def full_expansion_sweep(ship):
    """
    Args:
        -ship_name: (string) name of the model of ship to run the search on
        -pre_outfits: (list of strings) names of outfits to install on the ship
                      before running the search
    Wrapper function for the main search. Does a search for every number of
    outfits expansions and displays the results for comparison.
    """
    ship_list = list()
    print('ORIGINAL SHIP')
    print(ship)
    print()

    while ship.stats['cargo_space'] > 0:
        opt_outfits = get_opt_outfits(all_outfits, ship.inefficiency, ship.stats['heat_diss'])
        energy, extra_space, outfits = main_search(ship.stats['space'], ship.net_ship_heat(), ship.inefficiency, ship.stats['heat_diss'], list(opt_outfits.items()), dict())
        for out in outfits:
            ship.install_outfit(all_outfits[out])
        print('EXPANSIONS: {}'.format(ship.inefficiency))
        print(ship)
        ship_list.append(str(ship))
        print('Install: {}\n'.format(outfits))
        for out in outfits:
            ship.install_outfit(all_outfits[out], uninstall=True)
        ship.install_outfit(all_outfits['Outfits Expansion'])
    return ship_list




if __name__ == '__main__':
    #load ship and outfit data
    all_ships, all_outfits = loadData.load_outfits_and_ships()
    illegal_outfits = loadData.load_illegal_outfits()
    ship = loadData.load_input(sys.argv[1], all_ships, all_outfits)

    print(ship)

    search_type = input('Type 1 or 2\n1) Try all possible numbers of outfits expansions\n2) Only use the outfits given in input.txt\n')

    if search_type == '1':
        loadData.save_output(sys.argv[1], full_expansion_sweep(ship))
    elif search_type == '2':
        loadData.save_output(sys.argv[1], single_search(ship))

#!/usr/bin/env python
#

"""
// The DoTurn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist. Inside this function, you issue orders using the
// pw.IssueOrder() function. For example, to send 10 ships from planet 3 to
// planet 8, you would say pw.IssueOrder(3, 8, 10).
"""

from PlanetWars import PlanetWars
from PlanetWars import Planet
from math import ceil
from Log import debug, game_log
from PlanetSim import PlanetSim
import math
import random
import operator
from Utils import *

distances = {}
nearestNeighbors = {}


def ComputePlanetDistances(pw):
    planets = sorted(pw.Planets(), key=lambda x: x.PlanetID())
    for p in planets:
        dists = []
        distances[p.PlanetID()] = {}
        for q in planets:
            if q.PlanetID() != p.PlanetID():
                dx = p.X() - q.X()
                dy = p.Y() - q.Y()
                actual_distance = math.sqrt(dx * dx + dy * dy)
                x = (q.PlanetID(), actual_distance)
                dists.append(x)
                distances[p.PlanetID()][q.PlanetID()] = actual_distance
            # endif
        # endfor
        nearestNeighbors[p.PlanetID()] = sorted(dists, key=lambda x: x[1])
    # endfor


def DoTurn(pw, turn):
    try:
        debug("DO TURN {0}".format(turn))
        if distances == {}:
            ComputePlanetDistances(pw)
        # endif
        foreign_planets = get_foreign_planets(pw)
        enemy_planets = get_enemy_planets(pw)
        my_planets = get_my_planets(pw)
        hardness = 0
        foreign_center_x, foreign_center_y = calculate_center_of_gravity(foreign_planets)
        own_center_x, own_center_y = calculate_center_of_gravity(my_planets)

        for my_planet in my_planets:
            total_invasion_ships_for_planet = get_available_invasion_ships(my_planet, pw)
            if total_invasion_ships_for_planet >= 1:
                debug(
                    "Planning invasions from planet {0} that contains currently {1} ships. Available for invasion: {2} ships"
                    .format(my_planet.PlanetID(), my_planet.NumShips(), total_invasion_ships_for_planet))
                invade_planets(my_planet, pw, total_invasion_ships_for_planet, own_center_x, own_center_y, turn)
            else:
                debug("Planet {0} with {1} ships cannot attack, it will be overrun soon...".format(my_planet.PlanetID(),
                                                                                                   my_planet.NumShips()))
            # endif
        # endfor
    except Exception, e:
        debug(str(e) + str(e.message))


def invade_planets(my_planet, pw, total_invasion_ships_for_planet, own_center_x, own_center_y, turn):
    targets_of_opportunity = {}

    for nearestNeighborIDs in nearestNeighbors[my_planet.PlanetID()]:
        nearestNeighbor = pw.GetPlanet(nearestNeighborIDs[0])

        distance_to_planet = distances[my_planet.PlanetID()][nearestNeighbor.PlanetID()]
        necessary_ships_to_invade = get_necessary_invasion_ships(nearestNeighbor, distance_to_planet, pw)
        opportunity = calculate_opportunity_fuzzy_logic(total_invasion_ships_for_planet,
                                                        necessary_ships_to_invade, nearestNeighbor, distance_to_planet,
                                                        own_center_x, own_center_y, turn)
        targets_of_opportunity[nearestNeighbor] = opportunity
    # endfor

    for opportunity_target in reversed(sorted(targets_of_opportunity, key=targets_of_opportunity.get)):
        distance_to_planet = distances[my_planet.PlanetID()][opportunity_target.PlanetID()]
        debug(
            "Target of opportunity {0} planet {1} currently contains {2} ships with opportunity {3} at distance {4}"
            .format(get_planet_type(opportunity_target), opportunity_target.PlanetID(), opportunity_target.NumShips(),
                    targets_of_opportunity[opportunity_target], distance_to_planet))
        sent_ships = 0

        necessary_ships_to_invade = get_necessary_invasion_ships(opportunity_target, distance_to_planet, pw)
        if necessary_ships_to_invade > 0:
            sent_ships = min(total_invasion_ships_for_planet, necessary_ships_to_invade + random.randint(0, 2))
            send(pw, my_planet, opportunity_target, sent_ships, distances)
        # endif

        total_invasion_ships_for_planet -= sent_ships
        if total_invasion_ships_for_planet <= random.randint(turn/21, turn/8):
            break
    # endfor


def main():
    debug("starting")
    map_data = ''
    turn_number = 0
    while (True):
        current_line = raw_input()
        if len(current_line) >= 2 and current_line.startswith("go"):
            pw = PlanetWars(map_data)
            debug("NEW TURN {0}".format(turn_number))
            turn_number += 1
            DoTurn(pw, turn_number)
            pw.FinishTurn()
            debug("TURN FINISHED")
            map_data = ''
        else:
            map_data += current_line + '\n'


if __name__ == '__main__':
    try:
        import psyco

        psyco.full()
    except ImportError:
        pass
    try:
        main()
    except KeyboardInterrupt:
        print 'ctrl-c, leaving ...'

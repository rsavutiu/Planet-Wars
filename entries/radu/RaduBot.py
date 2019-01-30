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
                actual_distance = pw.Distance(p, q)
                x = (q.PlanetID(), actual_distance)
                dists.append(x)
                distances[p.PlanetID()][q.PlanetID()] = actual_distance
            # endif
        # endfor
        nearestNeighbors[p.PlanetID()] = sorted(dists, key=lambda x: x[1])
    # endfor


def DoTurn(pw):
    try:
        debug("DO TURN")
        if distances == {}:
            ComputePlanetDistances(pw)
        # endif
        foreign_planets = get_foreign_planets(pw)
        enemy_planets = get_enemy_planets(pw)
        my_planets = get_my_planets(pw)
        hardness = 0
        foreign_center_x, foreign_center_y, foreign_distances_to_center_map = calculate_center_of_gravity(
            foreign_planets)
        own_center_x, own_center_y, own_distances_to_center_map = calculate_center_of_gravity(my_planets)

        for my_planet in my_planets:
            total_invasion_ships_for_planet = get_available_invasion_ships(my_planet, pw)
            debug("Processing planet {0} that contains currently {1} ships. Available for invasion: {2} ships"
                  .format(my_planet.PlanetID(), my_planet.NumShips(), total_invasion_ships_for_planet))
            if total_invasion_ships_for_planet >= 1:
                invade_planets(my_planet, pw, total_invasion_ships_for_planet)
            # endif
        # endfor
    except Exception, e:
        debug(str(e) + str(e.message))


def invade_planets(my_planet, pw, total_invasion_ships_for_planet):
    targets_of_opportunity = {}

    for nearestNeighborIDs in nearestNeighbors[my_planet.PlanetID()]:
        nearestNeighbor = pw.GetPlanet(nearestNeighborIDs[0])
        distance_to_planet = distances[my_planet.PlanetID()][nearestNeighbor.PlanetID()]
        necessary_ships_to_invade = get_necessary_invasion_ships(nearestNeighbor, distance_to_planet, pw)
        opportunity = calculate_opportunity(total_invasion_ships_for_planet, necessary_ships_to_invade, nearestNeighbor,
                              distance_to_planet)
        debug(
            "Looking to invade planet {0} with {1} ships landed on it at distance {2} from planet "
            "and at growth rate {3}. Opportunity: {4}"
            .format(nearestNeighbor.PlanetID(), nearestNeighbor.NumShips(), distance_to_planet,
                    nearestNeighbor.GrowthRate(), opportunity))

        targets_of_opportunity[nearestNeighbor] = opportunity
    # endfor

    for opportunity_target in reversed(sorted(targets_of_opportunity, key=targets_of_opportunity.get)):
        distance_to_planet = distances[my_planet.PlanetID()][opportunity_target.PlanetID()]
        debug(
            "Target of opportunity planet {0} with opportunity {1} at distance {2}"
                .format(opportunity_target.PlanetID(), targets_of_opportunity[opportunity_target], distance_to_planet))
        sent_ships = 0
        if opportunity_target.Owner() != 1:
            necessary_ships_to_invade = get_necessary_invasion_ships(opportunity_target,distance_to_planet, pw)
            if necessary_ships_to_invade > 0:
                sent_ships = min(total_invasion_ships_for_planet, necessary_ships_to_invade + 1)
                send(pw, my_planet, opportunity_target, sent_ships, distances)
            # endif
        # endif
        total_invasion_ships_for_planet -= sent_ships
        if total_invasion_ships_for_planet <= 1:
            break
    # endfor


def main():
    debug("starting")
    map_data = ''
    while (True):
        current_line = raw_input()
        if len(current_line) >= 2 and current_line.startswith("go"):
            pw = PlanetWars(map_data)
            debug("NEW TURN")
            DoTurn(pw)
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

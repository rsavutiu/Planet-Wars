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
        #endfor
        nearestNeighbors[p.PlanetID()] = sorted(dists, key=lambda x: x[1])

def DoTurn(pw):
    try:
        if distances == None or distances == {}:
            ComputePlanetDistances(pw)
        # endif

        dictTargets = {}
        foreign_planets = pw.NotMyPlanets()
        enemy_planets = pw.EnemyPlanets()
        hardness = 0
        for foreign_planet in foreign_planets:
            hardness = foreign_planet.NumShips()

            incoming_fleets = get_incoming_fleets(foreign_planet.PlanetID(), pw)
            for incoming_fleet in incoming_fleets:
                if incoming_fleet.Owner() == 1:
                    hardness -= incoming_fleet.NumShips()
                else:
                    hardness += incoming_fleet.NumShips()
                    # endif
            # endfor

            if (hardness > 0):
                closest_own_planet = find_closest_own_planets(foreign_planet.PlanetID(), pw)[0]
                debug("dict {0} {1}".format(closest_own_planet, foreign_planet.PlanetID()))
                distance_to_my_closest_planet = distances[closest_own_planet][foreign_planet.PlanetID()]

                hardness = hardness * distance_to_my_closest_planet * distance_to_my_closest_planet

                if enemy_planets.count(foreign_planet) > 0:
                    # account to capture it it's going to take at least
                    # distance_to_my_closest_planet turns of enemy holding this.
                    # Which would be even worse.
                    # So it's easier taking it now than in the future.
                    hardness -= foreign_planet.GrowthRate() * distance_to_my_closest_planet
                # endif

            dictTargets[foreign_planet.PlanetID()] = hardness
        # endfor
        debug("Dict targets size: {0}".format(len(dictTargets)))
        sorted_targets = sorted(dictTargets.items(), key=operator.itemgetter(1))

        i = 0

        while (i<1):
            i += 1
            main_target_planet_id = sorted_targets[i][0]
            enemy_ships_to_defeat_on_planet = pw.GetPlanet(main_target_planet_id).NumShips()

            incoming_fleets = get_incoming_fleets(main_target_planet_id, pw)
            for incoming_fleet in incoming_fleets:
                if incoming_fleet.Owner() == 2:
                    enemy_ships_to_defeat_on_planet += incoming_fleet.NumShips()
                else:
                    enemy_ships_to_defeat_on_planet -= incoming_fleet.NumShips()
                #endif
            #endfor


            debug("Main target id: {0}".format(main_target_planet_id))
            own_optimum_attacking_planets = find_closest_own_planets(main_target_planet_id, pw)

            for own_optimum_attacking_planet in own_optimum_attacking_planets[:4]:
                attacking_planet_total_ships_at_disposal = pw.GetPlanet(own_optimum_attacking_planet).NumShips() - 1

                incoming_fleets = get_incoming_opponent_fleets(own_optimum_attacking_planet, pw)
                incoming_ships = 0
                for incoming_fleet in incoming_fleets:
                    incoming_ships += incoming_fleet.NumShips()
                #endfor

                if (incoming_ships >= attacking_planet_total_ships_at_disposal):
                    #TODO defend here
                    debug("Danger, cancel attack : {0} -> [{1}] -> {2}".format(own_optimum_attacking_planet, main_target_planet_id, fleet_number))
                else:
                    fleet_number = random.randint(int((attacking_planet_total_ships_at_disposal - incoming_ships)/4),
                                                  int((attacking_planet_total_ships_at_disposal - incoming_ships)/2))
                    fleet_number = min(fleet_number, enemy_ships_to_defeat_on_planet)
                    if (fleet_number>0):
                        debug("Issue order: {0} -> [{1}] -> {2}".format(own_optimum_attacking_planet, main_target_planet_id, fleet_number))
                        pw.IssueOrderByIds(own_optimum_attacking_planet, main_target_planet_id, fleet_number)
                    #endif
                #endif
            #endfor
        #endwhile
    except Exception, e:
        debug(e.message)
        pass

def get_incoming_fleets(planet_id, pw):
    return filter(lambda x: x.DestinationPlanet == planet_id, pw.Fleets())

def get_incoming_opponent_fleets(planet_id, pw):
    return filter(lambda x: x.DestinationPlanet == planet_id and x.Owner()==2, pw.Fleets())

def find_closest_own_planets(target_planet_id, pw):
    sources = []
    my_planets_ids = map(lambda x: x.PlanetID(), pw.MyPlanets())
    for nearest_neighbor in nearestNeighbors[target_planet_id]:
        if my_planets_ids.count(nearest_neighbor[0]):
            sources.append(nearest_neighbor[0])
            # endif
    # endfor
    return sources


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

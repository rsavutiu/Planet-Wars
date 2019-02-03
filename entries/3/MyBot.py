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
from Log import debug
import os
import sys
from Utils import *

distances = {}
nearestNeighbors = {}
universe_max_space = None
turn = 0
dists = []
actual_distances = []

def ComputePlanetDistances(pw):
    planets = sorted(pw.Planets(), key=lambda x: x.PlanetID())
    for p in planets:

        distances[p.PlanetID()] = {}
        for q in planets:
            if q.PlanetID() != p.PlanetID():
                dx = p.X() - q.X()
                dy = p.Y() - q.Y()
                actual_distance = math.sqrt(dx * dx + dy * dy)
                x = (q.PlanetID(), actual_distance)
                dists.append(x)
                actual_distances.append(actual_distance)
                distances[p.PlanetID()][q.PlanetID()] = actual_distance
            # endif
        # endfor
        nearestNeighbors[p.PlanetID()] = sorted(dists, key=lambda x: x[1])
    # endfor


def invade_planets(my_planet, pw, total_invasion_ships_for_planet, turn):
    try:
        targets_of_opportunity = {}
        debug("invade planets from planet {0}. Invasion fleet available: {1}"
              .format(my_planet.PlanetID(), total_invasion_ships_for_planet))
        for nearestNeighborIDs in nearestNeighbors[my_planet.PlanetID()]:
            nearestNeighbor = pw.GetPlanet(nearestNeighborIDs[0])
            if (my_planet.PlanetID() != nearestNeighbor.PlanetID()):
                distance_to_planet = distances[my_planet.PlanetID()][nearestNeighbor.PlanetID()]
                necessary_ships_to_invade = get_necessary_invasion_ships(nearestNeighbor, distance_to_planet, pw)

                if necessary_ships_to_invade > 0:
                    opportunity = calculate_opportunity_fuzzy_logic(total_invasion_ships_for_planet,
                        necessary_ships_to_invade, nearestNeighbor, distance_to_planet, turn, max(actual_distances))
                    targets_of_opportunity[nearestNeighbor] = opportunity

                    # debug("processing neighbor {0} planet {1} currently contains {2} ships with "
                    #       " at distance {3}. Necessary ships to take: {4}. Opp: {5}"
                    #       .format(get_planet_type(nearestNeighbor), nearestNeighbor.PlanetID(),
                    #               nearestNeighbor.NumShips(),
                    #               distance_to_planet, necessary_ships_to_invade, opportunity))
                # endif
        # endfor

        opportunity_targets = reversed(sorted(targets_of_opportunity, key=targets_of_opportunity.get))

        for opportunity_target in opportunity_targets:
            if targets_of_opportunity[opportunity_target] < 0.15:
                debug("better wait opportunity is: {0}".format(targets_of_opportunity[opportunity_target]))
                return

            distance_to_planet = distances[my_planet.PlanetID()][opportunity_target.PlanetID()]
            sent_ships = 0
            necessary_ships_to_invade = \
                get_necessary_invasion_ships(opportunity_target, distance_to_planet, pw)

            debug(
                "Target of opportunity {0} planet {1} currently contains {2} ships with "
                "opportunity {3} at distance {4}. Necessary ships to take: {5}"
                    .format(get_planet_type(opportunity_target), opportunity_target.PlanetID(),
                            opportunity_target.NumShips(),
                            targets_of_opportunity[opportunity_target], distance_to_planet, necessary_ships_to_invade))
            if necessary_ships_to_invade > 0:
                necessary_ships_to_invade += 1
                sent_ships = min(total_invasion_ships_for_planet, necessary_ships_to_invade)
                send(pw, my_planet, opportunity_target, sent_ships, distances)
            # endif

            total_invasion_ships_for_planet -= sent_ships
            if total_invasion_ships_for_planet <= 4:
                debug("finished invasion ships {0}".format(total_invasion_ships_for_planet))
                return
            # endif
        #endfor
        debug("end do turn")

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        debug(str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
        debug(str(e) + str(e.message))
        raise e


def DoTurn(pw):
    myPlanets = pw.MyPlanets()
    enemyPlanets = pw.EnemyPlanets()
    # neutralPlanets = pw.NeutralPlanets()
    # myFleets = pw.MyFleets()
    # enemyFleets = pw.EnemyFleets()
    enemySize = 0
    mySize = 0
    global turn

    for planet in myPlanets:
        mySize += planet.NumShips()
    # endfor

    for planet in enemyPlanets:
        enemySize += planet.NumShips()
    # endfor

    if (enemySize <= 0) or (mySize <= 0):
        winRatio = 0
    else:
        winRatio = float(mySize) / enemySize
    # endif
    debug("WIN Ratio: " + str(winRatio))

    try:
        debug("DO TURN {0}".format(turn))
        if len(distances) == 0:
            ComputePlanetDistances(pw)
        # endif
        foreign_planets = get_foreign_planets(pw)
        enemy_planets = get_enemy_planets(pw)
        my_planets = get_my_planets(pw)
        hardness = 0
        # foreign_center_x, foreign_center_y = calculate_center_of_gravity(foreign_planets)
        # own_center_x, own_center_y = calculate_center_of_gravity(my_planets)

        # debug("I have {0} planets".format(len(my_planets)))
        index = 0
        for my_planet in my_planets:
            total_invasion_ships_for_planet = get_available_invasion_ships(my_planet, pw)
            # debug("Planet nr. {0} with {1} ships. {2} available for attack"
            #       .format(index, my_planet.NumShips(), total_invasion_ships_for_planet))
            index += 1
            if total_invasion_ships_for_planet >= 1:
                # debug("Planning invasions from planet {0} that contains currently {1} ships. "
                #       "Available for invasion: {2} ships"
                #       .format(my_planet.PlanetID(), my_planet.NumShips(), total_invasion_ships_for_planet))
                invade_planets(my_planet, pw, total_invasion_ships_for_planet, turn)
            else:
                debug("Planet {0} with {1} ships cannot attack, it will be overrun soon...".format(my_planet.PlanetID(),
                                                                                                   my_planet.NumShips()))
            # endif
            if index > 4: break
        # endfor
        turn += 1
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        debug(str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
        debug(str(e) + str(e.message))
        #raise e


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
        # endif
    # endwhile


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

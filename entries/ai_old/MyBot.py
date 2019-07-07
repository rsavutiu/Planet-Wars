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
from Log import debug
import os
import sys
import math
import time
import numpy

import utils.PlanetHelper
import utils.FleetsHelper
import utils.CenterOfGravity
import utils.Utils

distances = {}
nearestNeighbors = {}
max_planet_size = 1
universe_max_space = None
actual_distances = []
ATTACK_LIMIT = 8
max_distance = 0
game_turn = 0
theta = []


def compute_planet_distances_and_max_planet_size(pw):
    global max_planet_size, max_distance, nearestNeighbors
    planets = sorted(pw.Planets(), key=lambda x: x.PlanetID())
    for p in planets:
        if p.GrowthRate() > max_planet_size:
            max_planet_size = p.GrowthRate()
        # endif
        dists = []
        distances[p.PlanetID()] = {}
        for q in planets:
            if q.PlanetID() != p.PlanetID():
                dx = p.X() - q.X()
                dy = p.Y() - q.Y()
                actual_distance = math.sqrt(dx * dx + dy * dy)
                x = (q.PlanetID(), actual_distance)
                dists.append(x)
                actual_distances.append(actual_distance)
                if actual_distance > max_distance:
                    max_distance = actual_distance
                # endif
                distances[p.PlanetID()][q.PlanetID()] = actual_distance
            # endif
        # endfor
        nearestNeighbors[p.PlanetID()] = sorted(dists, key=lambda x: x[1])
    # endfor
    return actual_distances


def identifyOpportunities(my_center_of_gravity, enemy_center_of_gravity, foreign_planets):

    calculated_opportunities = {}
    for foreign_planet in foreign_planets:
        distance_to_my_center = (max_distance - (math.pow(my_center_of_gravity[0] - foreign_planet.X(), 2) +
                                 math.pow(my_center_of_gravity[1] - foreign_planet.Y(), 2))) / float(max_distance)
        distance_to_enemy_center = (max_distance - (math.pow(enemy_center_of_gravity[0] - foreign_planet.X(), 2) +
                                    math.pow(enemy_center_of_gravity[1] - foreign_planet.Y(), 2))) / float(max_distance)
        values = [foreign_planet.GrowthRate() / float(max_planet_size),
                  float(distance_to_my_center),
                  float(distance_to_enemy_center),
                  foreign_planet.NumShips() / float(max_planet_ships),
                  float(foreign_planet.Owner() - 1)]
        opportunity = numpy.matmul(values, theta)
        calculated_opportunities[foreign_planet] = opportunity
        debug("Opportunity for planet {0} with {1} ships is {2}"
              .format(foreign_planet, foreign_planet.NumShips(), opportunity))
    # endfor
    return sorted(calculated_opportunities.items(), key=lambda x: x[1], reverse=True)


def DoTurn(pw):
    my_planets = utils.PlanetHelper.get_my_planets(pw)
    enemy_planets = utils.PlanetHelper.get_enemy_planets(pw)
    foreign_planets = utils.PlanetHelper.get_foreign_planets(pw)

    my_center_of_gravity = utils.CenterOfGravity.calculate_center_of_gravity(my_planets)
    enemy_center_of_gravity = utils.CenterOfGravity.calculate_center_of_gravity(enemy_planets)
    all_center_of_gravity = utils.CenterOfGravity.calculate_center_of_gravity(pw.Planets())

    global game_turn
    global max_planet_ships

    my_size = sum(p.NumShips() for p in my_planets)
    enemy_size = sum(p.NumShips() for p in enemy_planets)

    max_planet_ships = max(p.NumShips() for p in pw.Planets())

    if my_size <= 0:
        win_ratio = 0
    elif enemy_size <= 0:
        win_ratio = 1
    else:
        win_ratio = float(my_size) / enemy_size
    # endif

    try:
        start_time = time.time()
        debug("DO TURN {0}. I have {1} planets".format(game_turn, len(my_planets)))
        debug("WIN Ratio: " + str(win_ratio) + "\n")
        if len(distances) == 0:
            debug("Computing distances")
            compute_planet_distances_and_max_planet_size(pw)
        # endif

        # debug("I have {0} planets".format(len(my_planets)))
        index = 0
        planet_opportunities = identifyOpportunities(my_center_of_gravity, enemy_center_of_gravity, foreign_planets)

        for target_planet, opportunity_number in planet_opportunities[:5]:
            my_sorted_planets_for_target = sorted(my_planets,
                                                  key=lambda x: distances[target_planet.PlanetID()][x.PlanetID()])
            for my_planet in my_sorted_planets_for_target:
                if my_planet.NumShips() <= 1:
                    continue
                # endif

                distance_to_planet = distances[target_planet.PlanetID()][my_planet.PlanetID()]
                total_invasion_ships_for_planet = utils.PlanetHelper.get_available_invasion_ships(my_planet, pw)
                debug("Planet nr. {0} with {1} ships. {2} available for attack"
                      .format(index, my_planet.NumShips(), total_invasion_ships_for_planet))

                necessary_ships_to_invade = utils.PlanetHelper.get_necessary_invasion_ships(
                    target_planet, distance_to_planet, pw, max_distance)

                if necessary_ships_to_invade > 0 and total_invasion_ships_for_planet > 0:
                    necessary_ships_to_invade += 1
                    sent_ships = min(total_invasion_ships_for_planet, necessary_ships_to_invade)
                    assert (my_planet.Owner() == 1)
                    utils.Utils.send(pw, my_planet, target_planet, sent_ships,
                                     math.ceil(distances[my_planet.PlanetID()][target_planet.PlanetID()]))
                    necessary_ships_to_invade = \
                        utils.PlanetHelper.get_necessary_invasion_ships(target_planet, distance_to_planet, pw,
                                                                        max_distance)
                    debug(
                        "AFTER SENDING SHIPS! Target of opportunity {0} planet {1} currently contains {2} ships "
                        "at distance {3}. Necessary ships to take: {4}".format(
                            utils.PlanetHelper.get_planet_type(target_planet), target_planet.PlanetID(),
                            target_planet.NumShips(), distance_to_planet, necessary_ships_to_invade))
                # endif
            # endfor
        # endfor

        debug("END TURN {0} in time: {1} ms\n".format(game_turn, (time.time() - start_time) * 1000))
        game_turn += 1
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        debug(str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
        debug(str(e) + str(e.message))
        raise e


def main():
    global theta
    abs_path = os.path.dirname(os.path.abspath(__file__))
    print "cwd:", os.path.dirname(os.path.abspath(__file__))
    print "\r\n\r\n"
    with open(os.path.join(abs_path, "theta.txt")) as f:
        line = f.readline().split(" ")
        theta = map(lambda x: float(x), line)
    #endwith
    debug("starting")
    map_data = ''
    while True:
        current_line = raw_input()
        if len(current_line) >= 2 and current_line.startswith("go"):
            pw = PlanetWars(map_data)
            DoTurn(pw)
            pw.FinishTurn()
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

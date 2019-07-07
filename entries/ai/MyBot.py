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
from utils.Utils import *

distances = {}
nearest_neighbors = {}
max_planet_size = 1
universe_max_space = None
actual_distances = []
ATTACK_LIMIT = 8
max_distance = 0
game_turn = 0
theta = []

NUMBER_OF_FEATURES = 7


def identify_opportunities(my_center_of_gravity, enemy_center_of_gravity, foreign_planets, my_planets, enemy_planets):
    calculated_opportunities = {}
    if len(my_planets) > 0 and len(enemy_planets) > 0:
        for foreign_planet in foreign_planets:
            distance_to_my_center = (max_distance - (math.pow(my_center_of_gravity[0] - foreign_planet.X(), 2) +
                                                     math.pow(my_center_of_gravity[1] - foreign_planet.Y(),
                                                              2))) / float(
                max_distance)
            distance_to_enemy_center = (max_distance - (math.pow(enemy_center_of_gravity[0] - foreign_planet.X(), 2) +
                                                        math.pow(enemy_center_of_gravity[1] - foreign_planet.Y(),
                                                                 2))) / float(max_distance)

            growth_rate = foreign_planet.GrowthRate() / float(max_planet_size)

            values = [growth_rate,
                      growth_rate * distance_to_my_center / distance_to_enemy_center,
                      (foreign_planet.NumShips() * distance_to_my_center) /
                      (float(max_planet_ships) * distance_to_enemy_center),
                      float(3 - foreign_planet.Owner() * 2.0),
                      float(3 - foreign_planet.Owner() * 2.0) * growth_rate,
                      growth_rate * len(my_planets) / (len(enemy_planets) + 1),
                      ]

            assert (len(values) == NUMBER_OF_FEATURES - 1)  # last feature decides to carry out unsuccessful attacks
            opportunity = numpy.matmul(values, theta[:-1])
            calculated_opportunities[foreign_planet] = opportunity
            debug("Opportunity for planet {0} with {1} ships is {2}"
                  .format(foreign_planet, foreign_planet.NumShips(), opportunity))
        # endfor
        return sorted(calculated_opportunities.items(), key=lambda x: x[1], reverse=True)
    else:
        return None


def DoTurn(pw):
    global actual_distances, nearest_neighbors, distances, game_turn, max_planet_ships, max_distance

    my_planets = utils.PlanetHelper.get_my_planets(pw)
    enemy_planets = utils.PlanetHelper.get_enemy_planets(pw)
    foreign_planets = utils.PlanetHelper.get_foreign_planets(pw)

    my_center_of_gravity = utils.CenterOfGravity.calculate_center_of_gravity(my_planets)
    enemy_center_of_gravity = utils.CenterOfGravity.calculate_center_of_gravity(enemy_planets)
    all_center_of_gravity = utils.CenterOfGravity.calculate_center_of_gravity(pw.Planets())

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

            actual_distances, nearest_neighbors, distances, max_distance = \
                compute_planet_distances_and_max_planet_size(pw, max_planet_size, max_distance, nearest_neighbors)
        # endif

        # Defense first!

        for my_planet in my_planets:
            result = utils.PlanetHelper.get_needed_defense_ships(my_planet, pw)
            if result is not None:
                turn, ships_needed = result
                debug(
                    "I have {0} planet that needs help of {1} ships in {2} turns".format(my_planet, ships_needed, turn))
                mp_without_target = my_planets
                mp_without_target.remove(my_planet)
                if mp_without_target is not None:
                    my_sorted_planets_for_target = sorted(mp_without_target,
                                                          key=lambda x: distances[my_planet.PlanetID()][x.PlanetID()])
                    for my_closest_planet in my_sorted_planets_for_target:
                        available_ships = utils.PlanetHelper.get_available_invasion_ships(my_closest_planet, pw)
                        debug("Available ships on planet {0} = {1} ships".format(my_closest_planet.PlanetID(),
                                                                                 available_ships))
                        if available_ships > 0:
                            send(pw, my_closest_planet, my_planet, available_ships,
                                 math.ceil(distances[my_closest_planet.PlanetID()][my_planet.PlanetID()]))
                            ships_needed = ships_needed - available_ships
                        # endif
                        if ships_needed <= 0:
                            break
                        # endif
                    # endfor
                # endif
            # endif
        # endfor
        index = 0
        planet_opportunities = identify_opportunities(my_center_of_gravity, enemy_center_of_gravity, foreign_planets,
                                                      my_planets, enemy_planets)
        if planet_opportunities is not None:
            # Attack
            for target_planet, opportunity_number in planet_opportunities[:10]:
                if target_planet.GrowthRate() > 0:
                    my_sorted_planets_for_target = sorted(my_planets,
                                                          key=lambda x: distances[target_planet.PlanetID()][x.PlanetID()])
                    for my_planet in my_sorted_planets_for_target:
                        available_ships = utils.PlanetHelper.get_available_invasion_ships(my_planet, pw)

                        if my_planet.NumShips() <= 4 or available_ships <= 1:
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
                            invade_factor = available_ships / necessary_ships_to_invade
                            if (invade_factor * theta[-1]) > .5:
                                sent_ships = min(total_invasion_ships_for_planet, necessary_ships_to_invade)
                                assert (my_planet.Owner() == 1)
                                send(pw, my_planet, target_planet, sent_ships,
                                     math.ceil(distances[my_planet.PlanetID()][target_planet.PlanetID()]))
                                necessary_ships_to_invade = \
                                    utils.PlanetHelper.get_necessary_invasion_ships(target_planet, distance_to_planet, pw,
                                                                                    max_distance)
                                debug(
                                    "AFTER SENDING SHIPS! Target of opportunity {0} planet {1} currently contains {2} ships "
                                    "at distance {3}. Necessary ships to take: {4}".format(
                                        utils.PlanetHelper.get_planet_type(target_planet), target_planet.PlanetID(),
                                        target_planet.NumShips(), distance_to_planet, necessary_ships_to_invade))
                            else:
                                debug(
                                    "DIDN'T SEND SHIPS! Target of opportunity {0} planet {1} currently contains {2} ships "
                                    "at distance {3}. Necessary ships to take: {4}".format(
                                        utils.PlanetHelper.get_planet_type(target_planet), target_planet.PlanetID(),
                                        target_planet.NumShips(), distance_to_planet, necessary_ships_to_invade))
                        # endif
                    # endfor
                # endif
            # endfor
        # endif

        debug("END TURN {0} in time: {1} ms\n".format(game_turn, (time.time() - start_time) * 1000))
        game_turn += 1
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        debug(str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
        debug(str(e) + str(e.message))
        raise e


def main():
    import sys
    global theta

    if len(sys.argv) >= NUMBER_OF_FEATURES:
        debug("theta from commandline args")
        theta = sys.argv[1:]
        new_list = []
        for element in theta:
            new_list.append([float(element)])
        theta = new_list
    else:
        debug("random theta")
        # theta = [1.07668319, -4.67252562, -4.83999886, -3.78736198, -2.50656436, 3.8234228, 0.2380]
        theta = [0.25499724, - 0.03653183, - 0.04419227, - 0.34623976,  0.67157856,  0.39569266, 0.37693781]
    #endif

    debug("starting for theta: {0}".format(str(theta)))

    # with open("results.txt", "a+") as f:
    #     for i in range(NUMBER_OF_FEATURES):
    #         elem = theta[i][0]
    #         f.write("{0} ".format(elem))

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



# /Users/rsavutiu/workspace/Python/Planet-Wars/venv/bin/python /Users/rsavutiu/workspace/Python/Planet-Wars/Runner.py "python entries/ai/MyBot.py" "python entries/3/MyBot.py"
# /Users/rsavutiu/workspace/Python/Planet-Wars
# won on maps/map1.txt
# won on maps/map2.txt
# won on maps/map3.txt
# won on maps/map4.txt
# won on maps/map5.txt
# won on maps/map6.txt
# won on maps/map7.txt
# lost on maps/map8.txt
# won on maps/map9.txt
# won on maps/map10.txt
# lost on maps/map11.txt
# lost on maps/map12.txt
# lost on maps/map13.txt
# won on maps/map14.txt
# won on maps/map15.txt
# won on maps/map16.txt
# won on maps/map17.txt
# lost on maps/map18.txt
# won on maps/map19.txt
# won on maps/map20.txt
# lost on maps/map21.txt
# won on maps/map22.txt
# lost on maps/map23.txt
# won on maps/map24.txt
# won on maps/map25.txt
# lost on maps/map26.txt
# won on maps/map27.txt
# lost on maps/map28.txt
# won on maps/map29.txt
# won on maps/map30.txt
# won on maps/map31.txt
# lost on maps/map32.txt
# won on maps/map33.txt
# won on maps/map34.txt
# lost on maps/map35.txt
# won on maps/map36.txt
# lost on maps/map37.txt
# lost on maps/map38.txt
# won on maps/map39.txt
# won on maps/map40.txt
# won on maps/map41.txt
# won on maps/map42.txt
# lost on maps/map43.txt
# won on maps/map44.txt
# lost on maps/map45.txt
# won on maps/map46.txt
# lost on maps/map47.txt
# won on maps/map48.txt
# lost on maps/map49.txt
# won on maps/map50.txt
# won on maps/map51.txt
# won on maps/map52.txt
# lost on maps/map53.txt
# won on maps/map54.txt
# won on maps/map55.txt
# lost on maps/map56.txt
# won on maps/map57.txt
# lost on maps/map58.txt
# lost on maps/map59.txt
# won on maps/map60.txt
# won on maps/map61.txt
# won on maps/map62.txt
# lost on maps/map63.txt
# won on maps/map64.txt
# won on maps/map65.txt
# won on maps/map66.txt
# lost on maps/map67.txt
# lost on maps/map68.txt
# won on maps/map69.txt
# won on maps/map70.txt
# lost on maps/map71.txt
# won on maps/map72.txt
# won on maps/map73.txt
# won on maps/map74.txt
# won on maps/map75.txt
# won on maps/map76.txt
# won on maps/map77.txt
# won on maps/map78.txt
# lost on maps/map79.txt
# won on maps/map80.txt
# won on maps/map81.txt
# won on maps/map82.txt
# won on maps/map83.txt
# won on maps/map84.txt
# lost on maps/map85.txt
# won on maps/map86.txt
# won on maps/map87.txt
# won on maps/map88.txt
# won on maps/map89.txt
# won on maps/map90.txt
# won on maps/map91.txt
# won on maps/map92.txt
# won on maps/map93.txt
# won on maps/map94.txt
# won on maps/map95.txt
# won on maps/map96.txt
# lost on maps/map97.txt
# lost on maps/map98.txt
# lost on maps/map99.txt
# P1 wins 69.0%
#
# Process finished with exit code 0

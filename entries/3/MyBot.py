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

import utils.PlanetHelper
import utils.FleetsHelper
import utils.CenterOfGravity
import utils.Utils

import fuzzy_logic.FuzzyFCL

distances = {}
nearestNeighbors = {}
max_planet_size = 1
universe_max_space = None
turn = 0
actual_distances = []
ATTACK_LIMIT = 8
max_distance = 0
game_turn = 0

def compute_planet_distances(pw):
    global max_planet_size, max_distance, nearestNeighbors
    planets = sorted(pw.Planets(), key=lambda x: x.PlanetID())
    for p in planets:
        if p.GrowthRate() > max_planet_size:
            max_planet_size = p.GrowthRate()
        #endif
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
                #endif
                distances[p.PlanetID()][q.PlanetID()] = actual_distance
            # endif
        # endfor
        nearestNeighbors[p.PlanetID()] = sorted(dists, key=lambda x: x[1])
    # endfor
    return actual_distances


def invade_planets(my_planet, pw, total_invasion_ships_for_planet, turn, ignored_planets, win_ratio):
    global max_planet_size, max_distance
    try:

        debug("invade planets from planet {0}. Invasion fleet available: {1} out of {2} ships. Neighbors: {3}"
              .format(my_planet.PlanetID(), total_invasion_ships_for_planet, my_planet.NumShips(),
                      len(nearestNeighbors[my_planet.PlanetID()])))


        targets_of_opportunity = calculate_all_opportunities(
            my_planet, pw, ignored_planets, total_invasion_ships_for_planet)

        opportunity_targets = reversed(sorted(targets_of_opportunity, key=targets_of_opportunity.get))

        own_planets_index = 0
        opportunity_targets_own_planets_first = []
        for opportunity_target in opportunity_targets:
            if opportunity_target.Owner() == 1:
                opportunity_targets_own_planets_first.insert(own_planets_index, opportunity_target)
                own_planets_index += 1
            #endif
            else:
                opportunity_targets_own_planets_first.append(opportunity_target)
            #endif
        #endfor

        limit_index = 0
        for opportunity_target in opportunity_targets_own_planets_first:

            distance_to_planet = distances[my_planet.PlanetID()][opportunity_target.PlanetID()]

            debug("{0} Target: {1} planet {2} at distance {3} with currently {4} ships on it. Opportunity: {5}"
                  .format(limit_index, utils.PlanetHelper.get_planet_type(opportunity_target),
                      opportunity_target.PlanetID(), distance_to_planet, opportunity_target.NumShips(),
                          targets_of_opportunity[opportunity_target]))
            if limit_index > ATTACK_LIMIT:
                break
            #endif
            limit_index += 1

            if targets_of_opportunity[opportunity_target] < 0.10 and opportunity_target.Owner() != 1 and win_ratio < 5:
                if opportunity_target.Owner != 1:
                    debug("finished own defense. better wait opportunity is: {0}. target was: {1} with {2} ships. "
                          "distance percentage to max distance ever: {3}".format(
                        targets_of_opportunity[opportunity_target], opportunity_target.PlanetID(),
                            opportunity_target.NumShips(), distance_to_planet * 100.0 / max_distance))
                    return ignored_planets
                #endif
            #endif

            sent_ships = 0
            necessary_ships_to_invade = \
                utils.PlanetHelper.get_necessary_invasion_ships(opportunity_target, distance_to_planet, pw, max_distance)

            debug(
                "Target of opportunity {0} planet {1} currently contains {2} ships with "
                "opportunity {3} at distance {4}. Necessary ships to take: {5}".format(
                    utils.PlanetHelper.get_planet_type(opportunity_target), opportunity_target.PlanetID(),
                    opportunity_target.NumShips(),
                    targets_of_opportunity[opportunity_target], distance_to_planet, necessary_ships_to_invade))

            if necessary_ships_to_invade > 0:
                necessary_ships_to_invade += 1
                sent_ships = min(total_invasion_ships_for_planet, necessary_ships_to_invade)
                utils.Utils.send(pw, my_planet, opportunity_target, sent_ships, math.ceil(distances[my_planet.PlanetID()][opportunity_target.PlanetID()]))
                necessary_ships_to_invade = \
                    utils.PlanetHelper.get_necessary_invasion_ships(opportunity_target, distance_to_planet, pw,
                                                                    max_distance)
                debug(
                    "AFTER SENDING SHIPS! Target of opportunity {0} planet {1} currently contains {2} ships with "
                    "opportunity {3} at distance {4}. Necessary ships to take: {5}".format(
                        utils.PlanetHelper.get_planet_type(opportunity_target), opportunity_target.PlanetID(),
                        opportunity_target.NumShips(),
                        targets_of_opportunity[opportunity_target], distance_to_planet, necessary_ships_to_invade))

                if sent_ships > necessary_ships_to_invade:
                    ignored_planets.append(opportunity_target.PlanetID())
                #endif
            # endif

            total_invasion_ships_for_planet -= sent_ships
            if total_invasion_ships_for_planet <= 0:
                debug("finished invasion ships {0}".format(total_invasion_ships_for_planet))
                return ignored_planets
            # endif
        # endfor
        return ignored_planets

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        debug(str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
        debug(str(e) + str(e.message))
        raise e


def DoTurn(pw):
    my_planets = pw.MyPlanets()
    enemy_planets = pw.EnemyPlanets()
    enemy_size = 0
    my_size = 0
    global game_turn

    for planet in my_planets:
        my_size += planet.NumShips()
    # endfor

    for planet in enemy_planets:
        enemy_size += planet.NumShips()
    # endfor

    if (enemy_size <= 0) or (my_size <= 0):
        winRatio = 0
    else:
        winRatio = float(my_size) / enemy_size
    # endif


    try:
        start_time = time.time()
        debug("DO TURN {0}. I have {1} planets".format(game_turn, len(my_planets)))
        debug("WIN Ratio: " + str(winRatio) + "\n")
        if len(distances) == 0:
            compute_planet_distances(pw)
        # endif
        my_planets = utils.PlanetHelper.get_my_planets(pw)

        # debug("I have {0} planets".format(len(my_planets)))
        index = 0
        ignored_planets = []
        for my_planet in sorted(my_planets, key=lambda x: x.NumShips(), reverse=True):
            total_invasion_ships_for_planet = utils.PlanetHelper.get_available_invasion_ships(my_planet, pw)
            # debug("Planet nr. {0} with {1} ships. {2} available for attack"
            #       .format(index, my_planet.NumShips(), total_invasion_ships_for_planet))
            index += 1
            if total_invasion_ships_for_planet > 0:
                # debug("Planning invasions from planet {0} that contains currently {1} ships. "
                #       "Available for invasion: {2} ships"
                #       .format(my_planet.PlanetID(), my_planet.NumShips(), total_invasion_ships_for_planet))
                ignored_planets = invade_planets(
                    my_planet, pw, total_invasion_ships_for_planet, game_turn, ignored_planets, winRatio)
                debug("ignored planets  {0}".format(len(ignored_planets)))
            else:
                debug("Planet {0} with {1} ships cannot attack, it will be overrun soon...".format(
                    my_planet.PlanetID(), my_planet.NumShips()))
            # endif
            if index > 4:
                return
        # endfor
        debug("END TURN {0} in time: {1} ms\n".format(game_turn, (time.time() - start_time) * 1000))
        game_turn += 1
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        debug(str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
        debug(str(e) + str(e.message))
        raise e


def calculate_all_opportunities(my_planet, pw, ignored_planets, total_invasion_ships_for_planet):
    targets_of_opportunity = {}
    for nearest_neighbour_ids in nearestNeighbors[my_planet.PlanetID()]:
        nearest_neighbour = pw.GetPlanet(nearest_neighbour_ids[0])

        if my_planet.PlanetID() != nearest_neighbour.PlanetID() and not ignored_planets.count(nearest_neighbour.PlanetID()) > 0:
            distance_to_planet = distances[my_planet.PlanetID()][nearest_neighbour.PlanetID()]
            necessary_ships_to_invade = utils.PlanetHelper.get_necessary_invasion_ships(nearest_neighbour,
                                                                                        distance_to_planet, pw,
                                                                                        max_distance)

            distance_percentage = distance_to_planet * 100.0 / max_distance

            if necessary_ships_to_invade > 0:
                opportunity = fuzzy_logic.FuzzyFCL.crisp_output(turn, distance_percentage,
                                                     total_invasion_ships_for_planet - necessary_ships_to_invade,
                                                     (nearest_neighbour.GrowthRate() * 100.0 / max_planet_size))

                opportunity *= (4 - distance_percentage/100.0) / 4.0

                if nearest_neighbour.Owner() == 2:
                    opportunity *= 1.07
                elif nearest_neighbour.Owner() == 1:
                    opportunity *= 1.25

                # if game_turn < 30:
                #     if necessary_ships_to_invade > 120:
                #         opportunity *= 0.9
                #     if necessary_ships_to_invade > 100:
                #         opportunity *= 0.91
                #     if necessary_ships_to_invade > 80:
                #         opportunity *= 0.92
                #     elif necessary_ships_to_invade > 70:
                #         opportunity *= 0.93
                #     elif necessary_ships_to_invade > 50:
                #         opportunity *= 0.94
                #     elif necessary_ships_to_invade > 30:
                #         opportunity *= 0.95
                #     elif necessary_ships_to_invade > 20:
                #         opportunity *= 0.96
                #     elif necessary_ships_to_invade > 15:
                #         opportunity *= 0.97
                #     elif necessary_ships_to_invade > 10:
                #         opportunity *= 0.98
                #     elif necessary_ships_to_invade > 5:
                #         opportunity *= 0.99
                #     #endif

                # if turn < 5:
                #     if nearest_neighbour.Owner() == 2:
                #         opportunity *= 0.5
                #     elif nearest_neighbour.Owner() == 0:
                #         opportunity *= 1
                #     # endif
                # elif turn < 10:
                #     if nearest_neighbour.Owner() == 2:
                #         opportunity *= 0.55
                #     elif nearest_neighbour.Owner() == 0:
                #         opportunity *= 0.95
                #     # endif
                # elif turn < 15:
                #     if nearest_neighbour.Owner() == 2:
                #         opportunity *= 0.6
                #     elif nearest_neighbour.Owner() == 0:
                #         opportunity *= 0.9
                #     # endif
                # elif turn < 20:
                #     if nearest_neighbour.Owner() == 2:
                #         opportunity *= 0.7
                #     elif nearest_neighbour.Owner() == 0:
                #         opportunity *= 0.85
                #     # endif
                # elif turn < 25:
                #     if nearest_neighbour.Owner() == 2:
                #         opportunity *= 0.8
                #     elif nearest_neighbour.Owner() == 0:
                #         opportunity *= 0.8
                #     # endif
                # elif turn < 30:
                #     if nearest_neighbour.Owner() == 2:
                #         opportunity *= 0.9
                #     elif nearest_neighbour.Owner() == 0:
                #         opportunity *= 0.75
                #     # endif
                # elif turn < 35:
                #     if nearest_neighbour.Owner() == 2:
                #         opportunity *= 0.95
                #     elif nearest_neighbour.Owner() == 0:
                #         opportunity *= 0.7
                #     # endif
                # else:
                #     if nearest_neighbour.Owner() == 2:
                #         opportunity *= 1
                #     elif nearest_neighbour.Owner() == 0:
                #         opportunity *= 0.675
                #     # endif

                targets_of_opportunity[nearest_neighbour] = opportunity

            else:
                debug("Ignoring planet {0} with {1} ships on it. It's fine.".format(
                    nearest_neighbour.PlanetID(), nearest_neighbour.NumShips()))
                ignored_planets.append(nearest_neighbour.PlanetID())
                # debug("processing neighbor {0} planet {1} currently contains {2} ships with "
                #       " at distance {3}. Necessary ships to take: {4}. Opp: {5}"
                #       .format(get_planet_type(nearest_neighbour), nearest_neighbour.PlanetID(),
                #               nearest_neighbour.NumShips(),
                #               distance_to_planet, necessary_ships_to_invade, opportunity))
            # endif
        # endif
    # endfor
    return targets_of_opportunity

def main():
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

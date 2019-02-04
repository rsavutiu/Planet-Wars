import time
import os
import sys
import numpy
from Log import debug
import pickledict
from fcl_parser import FCLParser

SHIPS_MAX_LIMIT = 10
SHIPS_MIN_LIMIT = -10
DISTANCE_MAX_LIMIT = 100
GAME_TIME_LIMIT = 201
PLANET_SIZE_MAX_LIMIT = 17

PICKLED_DICT = "fuzzy_granular_1_results_dict.py"
FCL_RULES_FILE = "invasion_opportunity.fcl"
loaded_dict = None


def fuzzify_hashtable(game_time, distance, ships_surplus, planet_size):
    if game_time < 0:
        game_time = 0
    elif game_time >= GAME_TIME_LIMIT:
        game_time = GAME_TIME_LIMIT - 1
    # endif

    if distance >= DISTANCE_MAX_LIMIT:
        distance = DISTANCE_MAX_LIMIT - 1
    # endif

    if ships_surplus <= SHIPS_MIN_LIMIT:
        ships_surplus = SHIPS_MIN_LIMIT + 1
    elif ships_surplus >= SHIPS_MAX_LIMIT:
        ships_surplus = SHIPS_MAX_LIMIT - 1
    #endif

    if planet_size >= PLANET_SIZE_MAX_LIMIT:
        planet_size = PLANET_SIZE_MAX_LIMIT
    #endif

    pickledict.a((game_time, distance, ships_surplus, planet_size))


def fuzzify(game_time, distance, ships_surplus, planet_size):
    global opportunity, opportunity_ctrl

    if ships_surplus > SHIPS_MAX_LIMIT:
        ships_surplus = SHIPS_MAX_LIMIT
    elif ships_surplus <= SHIPS_MIN_LIMIT:
        ships_surplus = SHIPS_MIN_LIMIT
    #endif

    if distance > DISTANCE_MAX_LIMIT:
        distance = DISTANCE_MAX_LIMIT
    elif distance <= 0:
        distance = 0
    #endif

    if game_time >= GAME_TIME_LIMIT:
        game_time = GAME_TIME_LIMIT-1
    elif game_time <= 0:
        game_time = 0
    #endif

    opportunity.input['game_turn'] = game_time
    opportunity.input['distance'] = distance
    opportunity.input['ships_surplus'] = ships_surplus
    opportunity.input['planet_size'] = planet_size

    opportunity.compute()
    ret = opportunity.output['opportunity']
    # debug("Calculated for [time {:4}] [distance {:5}] [ships {:5}] --> {:10}"
    # .format(game_time, distance, ships_surplus, ret))
    return ret


if __name__ == "__main__":
    import skfuzzy.control as ctrl
    import numpy as np
    start_timestamp = time.time()
    lines = []
    lines.append("a = {}\n")
    # if not os.path.isfile(PICKLED_DICT):
    with open(PICKLED_DICT, 'w') as handle:

            p = FCLParser()  # Create the parser
            p.read_fcl_file(FCL_RULES_FILE)  # Parse a file
            opportunity_ctrl = ctrl.ControlSystem(p.rules)
            opportunity = ctrl.ControlSystemSimulation(opportunity_ctrl)

            for game_time_index in range(1, GAME_TIME_LIMIT):
                for distance_index in range(0, DISTANCE_MAX_LIMIT):
                    for ships_surplus_index in range(SHIPS_MIN_LIMIT, SHIPS_MAX_LIMIT+1):
                        for planet_size in range(1, PLANET_SIZE_MAX_LIMIT):
                            try:
                                result = fuzzify(game_time_index, distance_index, ships_surplus_index, planet_size)
                                line = "a[{0}] = {1}\n".format(
                                    (game_time_index, distance_index, ships_surplus_index, planet_size), result)
                                # print line
                                lines.append(line)
                            except Exception, e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                debug(str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
                    #endfor
                #endfor
            #endfor
            handle.writelines(lines)
            handle.close()
        #endwith
    #endwith
#endif

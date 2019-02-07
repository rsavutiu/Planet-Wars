import time
import os
import sys
import numpy
import fuzzy_granular_1_results_dict
from Log import debug
from fcl_parser import FCLParser

SHIPS_MAX_LIMIT = 20
SHIPS_MIN_LIMIT = -10
DISTANCE_MAX_LIMIT = 10
GAME_TIME_LIMIT = 201
PLANET_SIZE_MAX_LIMIT = 10

PICKLED_DICT = "fuzzy_granular_ships_surplus_results_dict.py"
FCL_RULES_FILE = "invasion_opportunity.fcl"
loaded_dict = None

def fuzzy_crisp_hashtable(game_time, distance_percentage, ships_surplus, planet_size_percentage):
    if game_time < 0:
        game_time = 0
    elif game_time >= GAME_TIME_LIMIT:
        game_time = GAME_TIME_LIMIT - 1
    # endif

    if distance_percentage >= DISTANCE_MAX_LIMIT:
        distance_percentage = DISTANCE_MAX_LIMIT - 1
    # endif

    if ships_surplus < SHIPS_MIN_LIMIT:
        ships_surplus = SHIPS_MIN_LIMIT
    elif ships_surplus > SHIPS_MAX_LIMIT:
        ships_surplus = SHIPS_MAX_LIMIT
    #endif

    if planet_size_percentage >= PLANET_SIZE_MAX_LIMIT:
        planet_size_percentage = PLANET_SIZE_MAX_LIMIT
    #endif

    return fuzzy_granular_1_results_dict.a[(game_time, distance_percentage, ships_surplus, planet_size_percentage)]


def crisp_output(game_time, distance_percentage, ships_surplus, planet_size_percentage):
    global opportunity, opportunity_ctrl

    if ships_surplus > SHIPS_MAX_LIMIT:
        ships_surplus = SHIPS_MAX_LIMIT
    elif ships_surplus < SHIPS_MIN_LIMIT:
        ships_surplus = SHIPS_MIN_LIMIT
    #endif

    if distance_percentage > DISTANCE_MAX_LIMIT:
        distance_percentage = DISTANCE_MAX_LIMIT
    elif distance_percentage <= 0:
        distance_percentage = 0
    #endif

    if game_time >= GAME_TIME_LIMIT:
        game_time = GAME_TIME_LIMIT-1
    elif game_time <= 0:
        game_time = 0
    #endif

    opportunity.input['game_turn'] = game_time
    opportunity.input['distance'] = distance_percentage
    opportunity.input['ships_surplus'] = ships_surplus
    opportunity.input['planet_size'] = planet_size_percentage

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
    lines.append("a = {\n")
    # if not os.path.isfile(PICKLED_DICT):
    with open(PICKLED_DICT, 'w') as handle:

            p = FCLParser()  # Create the parser
            p.read_fcl_file(FCL_RULES_FILE)  # Parse a file
            opportunity_ctrl = ctrl.ControlSystem(p.rules)
            opportunity = ctrl.ControlSystemSimulation(opportunity_ctrl)

            for game_time_index in range(0, GAME_TIME_LIMIT+1):
                print "game time index:", game_time_index
                for distance_index in range(0, DISTANCE_MAX_LIMIT + 1):

                    print "distance index:", distance_index
                    for ships_surplus_index in range(SHIPS_MIN_LIMIT, SHIPS_MAX_LIMIT+1):

                        for size in range(0, PLANET_SIZE_MAX_LIMIT + 1):

                            try:
                                result = crisp_output(game_time_index, distance_index, ships_surplus_index, size)
                                line = "{0} : {1},\n".format(
                                    (game_time_index, distance_index, ships_surplus_index, size), result)
                                # print line
                                lines.append(line)
                            except Exception, e:
                                print "ships", ships_surplus_index
                                print "planet size", size
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                debug(str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
                                raise e
                    #endfor
                #endfor
            #endfor
            line = line[:-1]
            lines = lines[:-1]
            lines.append(line)
            lines.append("}\n")
            handle.writelines(lines)
            handle.close()
        #endwith
    #endwith
#endif

import numpy as np
import skfuzzy.control as ctrl
from Log import debug
"""
def automf(self, number=5, variable_type='quality', names=None,
           invert=False):
    Automatically populate the universe with membership functions.

    Parameters
    ----------
    number : [3, 5, 7] or list of names
        Number of membership functions to create. Must be an odd integer.
        At present, only 3, 5, or 7 are supported.
        If a list of names is given, then those are used
    variable_type : string
        Type of variable this is. Accepted arguments are
        * 'quality' : Continuous variable, higher values are better.
        * 'quant' : Quantitative variable, no value judgements.
    names : list
        List of names to use when creating mebership functions if you wish
        to override the default. Naming proceeds from lowest to highest.
    invert : bool
        Reverses the naming order if True. Membership function peaks still
        march from lowest to highest.

    Notes
    -----
    This convenience function allows quick construction of fuzzy variables
    with overlapping, triangular membership functions.

    It uses a standard naming convention defined for ``'quality'`` as::

    * dismal
    * poor
    * mediocre
    * average (always middle)
    * decent
    * good
    * excellent

    and for ``'quant'`` as::

    * lowest
    * lower
    * low
    * average (always middle)
    * high
    * higher
    * highest
    
    where the names on either side of ``'average'`` are used as needed to
        create 3, 5, or 7 membership functions.
        """

HASH_TABLE_FUZZY_LOGIC = 'fuzzy_logic_results.npy'
loaded_dict = np.load(HASH_TABLE_FUZZY_LOGIC).item()

SHIPS_MIN_LIMIT = -10
SHIPS_MAX_LIMIT = 10

DISTANCE_MAX_LIMIT = 30

GAME_TIME_LIMIT = 201


def fuzzify_hashtable(game_time, distance, ships_surplus):
    if game_time < 0:
        game_time = 0
    elif game_time >= GAME_TIME_LIMIT:
        game_time = GAME_TIME_LIMIT - 1

    if distance >= DISTANCE_MAX_LIMIT:
        distance = DISTANCE_MAX_LIMIT - 1

    if ships_surplus <= SHIPS_MIN_LIMIT:
        ships_surplus = SHIPS_MIN_LIMIT + 1
    elif ships_surplus >= SHIPS_MAX_LIMIT:
        ships_surplus = SHIPS_MAX_LIMIT - 1

    return loaded_dict((game_time, distance, ships_surplus))


# def fuzzify(game_time, distance, ships_surplus):
#     global opportunity, opportunity_ctrl
#
#     short_names = ['n', 'z', 'p']
#     # create antecedents
#     tttime = ctrl.Antecedent(np.arange(0, GAME_TIME_LIMIT, 1), 'tttime')
#     tttime.automf(3, names=['early', 'mid', 'late'])
#
#     ships = ctrl.Antecedent(np.arange(SHIPS_MIN_LIMIT - 1, SHIPS_MAX_LIMIT, 1), 'ships')
#     ships.automf(3, names=short_names)
#
#     dist = ctrl.Antecedent(np.arange(0, DISTANCE_MAX_LIMIT, 1), 'dist')
#     dist.automf(3, names=short_names)
#
#     atck = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'atck')
#     atck.automf(3, names=short_names)
#
#     rules = []
#
#     # 18 rules out of 147
#     rules.append(ctrl.Rule(antecedent=(
#             (tttime['early'] & dist['p'] & ships['n']) |
#             (tttime['early'] & dist['p'] & ships['z']) |
#             (tttime['early'] & dist['z'] & ships['n']) |
#             (tttime['early'] & dist['n'] & ships['z']) |
#             (tttime['mid'] & dist['p'] & ships['n']) |
#             (tttime['mid'] & dist['p'] & ships['z']) |
#             (tttime['mid'] & dist['z'] & ships['p']) |
#             (tttime['mid'] & dist['n'] & ships['n']) |
#             (tttime['late'] & dist['z'] & ships['n'])),
#         consequent=atck['n'], label='attack forbidden'))
#
#     rules.append(ctrl.Rule(antecedent=(
#             (tttime['early'] & dist['z'] & ships['z']) |
#             (tttime['early'] & dist['z'] & ships['p']) |
#             (tttime['early'] & dist['p'] & ships['p']) |
#
#             (tttime['mid'] & dist['p'] & ships['p']) |
#             (tttime['mid'] & dist['z'] & ships['p']) |
#             (tttime['mid'] & dist['z'] & ships['z']) |
#             (tttime['mid'] & dist['n'] & ships['n']) |
#
#             (tttime['late'] & dist['n'] & ships['n']) |
#             (tttime['late'] & dist['p'] & ships['n']) |
#             (tttime['late'] & dist['p'] & ships['z']) |
#
#             (tttime['late'] & dist['z'] & ships['z'])),
#         consequent=atck['z'], label='attack questionable'))
#
#     rules.append(ctrl.Rule(antecedent=(
#             (tttime['early'] & dist['n'] & ships['z']) |
#             (tttime['early'] & dist['n'] & ships['p']) |
#
#             (tttime['mid'] & dist['n'] & ships['z']) |
#             (tttime['mid'] & dist['n'] & ships['p']) |
#
#             (tttime['late'] & dist['p'] & ships['p']) |
#             (tttime['late'] & dist['z'] & ships['p']) |
#             (tttime['late'] & dist['n'] & ships['z'])),
#         consequent=atck['p'], label='attack recommended'))
#
#     if opportunity_ctrl is None:
#         opportunity_ctrl = ctrl.ControlSystem(rules)
#     #endif
#
#     if opportunity is None:
#         opportunity = ctrl.ControlSystemSimulation(opportunity_ctrl)
#     #endif
#
#     if ships_surplus > SHIPS_MAX_LIMIT:
#         ships_surplus = SHIPS_MAX_LIMIT
#     elif ships_surplus < SHIPS_MIN_LIMIT:
#         ships_surplus = SHIPS_MIN_LIMIT
#     #endif
#
#     if distance > DISTANCE_MAX_LIMIT:
#         distance = DISTANCE_MAX_LIMIT
#     elif distance <= 0:
#         distance = 0
#     #endif
#
#     if game_time >= GAME_TIME_LIMIT:
#         game_time = GAME_TIME_LIMIT-1
#     elif game_time <= 0:
#         game_time = 0
#     #endif
#
#     opportunity.input['tttime'] = game_time
#     opportunity.input['dist'] = distance
#     opportunity.input['ships'] = ships_surplus
#
#     opportunity.compute()
#     ret = opportunity.output['atck']
#     debug("Calculated for [time {:4}] [distance {:5}] [ships {:5}] --> {:10}".format(game_time, distance, ships_surplus, ret))
#     return ret


# if __name__ == "__main__":
#     start_timestamp = time.time()
#
#     class AutoVivification(dict):
#         """Implementation of perl's autovivification feature."""
#
#         def __getitem__(self, item):
#             try:
#                 return dict.__getitem__(self, item)
#             except KeyError:
#                 value = self[item] = type(self)()
#                 return value
#
#     if not os.path.isfile(HASH_TABLE_FUZZY_LOGIC):
#
#         fuzzy_dictionary_results = {}
#
#         for game_time_index in range(1, GAME_TIME_LIMIT-1):
#             for distance_index in range(0, DISTANCE_MAX_LIMIT):
#                 for ships_surplus_index in range(SHIPS_MIN_LIMIT-1, SHIPS_MAX_LIMIT):
#                     try:
#                         result = fuzzify(game_time_index, distance_index, ships_surplus_index)
#                         fuzzy_dictionary_results[(game_time_index, distance_index, ships_surplus_index)] = result
#                     except Exception, e:
#                         print 'game time', game_time_index
#                         print 'distance', distance_index
#                         print 'ships', ships_surplus_index
#                         exc_type, exc_obj, exc_tb = sys.exc_info()
#                         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#                         print(str(exc_type) + str(fname) + str(exc_tb.tb_lineno))
#                 #endfor
#             #endfor
#         #endfor
#
#         np.save(HASH_TABLE_FUZZY_LOGIC, fuzzy_dictionary_results)
#
#         print "initial calculations took: ", time.time() - start_timestamp
#     #endif
#
#     loaded_dict = np.load(HASH_TABLE_FUZZY_LOGIC).item()
#     # for key in loaded_dict.keys():
#     #     print key, type(key)
#     #endfor
#     print loaded_dict[(30, 5, 3)]
#     print "load took: ", time.time() - start_timestamp
# #endif
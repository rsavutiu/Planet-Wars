import numpy as np
import skfuzzy.control as ctrl
import random
import math
import time
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

SHIPS_MIN_LIMIT = -20
SHIPS_MAX_LIMIT = 30

DISTANCE_MAX_LIMIT = 120

GAME_TIME_LIMIT = 201

short_names=['n', 'z', 'p']

#create antecedents
turn = ctrl.Antecedent(np.arange(0, 201, 1), 'turn')
turn.automf(3, names=['early', 'mid', 'late'])

ships = ctrl.Antecedent(np.arange(SHIPS_MIN_LIMIT-1, SHIPS_MAX_LIMIT, 1), 'ships')
ships.automf(3, names=short_names)

dist = ctrl.Antecedent(np.arange(0, 400, 1), 'dist')
dist.automf(3, names=short_names)

atck = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'atck')
atck.automf(3, names=short_names)

rules = []
#
#18 rules out of 147
rules.append(ctrl.Rule(antecedent=(
                                   (turn['early']   & dist['p']   & ships['n'])  |
                                   (turn['early']   & dist['p']   & ships['z'])  |
                                   (turn['early']   & dist['p']   & ships['p'])  |
                                   (turn['early']   & dist['z']   & ships['n'])  |

                                   (turn['mid']     & dist['p']   & ships['n'])  |
                                   (turn['mid']     & dist['p']   & ships['z'])  |
                                   (turn['mid']     & dist['z']   & ships['p'])  |

                                   (turn['late']    & dist['z']   & ships['n'])),
                       consequent=atck['n'], label='attack forbidden'))

rules.append(ctrl.Rule(antecedent=(
                                   (turn['early']   & dist['z']   & ships['z'])  |
                                   (turn['early']   & dist['z']   & ships['p'])  |
                                   (turn['early']   & dist['n']   & ships['z'])  |

                                   (turn['mid']     & dist['p']   & ships['p'])  |
                                   (turn['mid']     & dist['z']   & ships['p'])  |
                                   (turn['mid']     & dist['z']   & ships['z'])  |
                                   (turn['mid']     & dist['n']   & ships['n'])  |

                                   (turn['late']    & dist['n']   & ships['n'])  |
                                   (turn['late']    & dist['p']   & ships['n'])  |
                                   (turn['late']    & dist['p']   & ships['z'])  |
                                   (turn['late']    & dist['p']   & ships['p'])  |
                                   (turn['late']    & dist['z']   & ships['z'])),
                       consequent=atck['z'], label='attack questionable'))

rules.append(ctrl.Rule(antecedent=(
                                   (turn['early']   & dist['n']   & ships['z'])  |
                                   (turn['early']   & dist['n']   & ships['p'])  |


                                   (turn['mid']     & dist['n']   & ships['z'])  |
                                   (turn['mid']     & dist['n']   & ships['n'])  |

                                   (turn['late']    & dist['z']   & ships['p'])  |
                                   (turn['late']    & dist['n']   & ships['z'])),
                       consequent=atck['p'], label='attack recommended'))

opportunity_ctrl = ctrl.ControlSystem(rules)
opportunity = ctrl.ControlSystemSimulation(opportunity_ctrl)

def fuzzify(game_time, distance, ships_surplus):
    if ships_surplus > SHIPS_MAX_LIMIT:
        ships_surplus = SHIPS_MAX_LIMIT
    elif ships_surplus < -SHIPS_MIN_LIMIT:
        ships_surplus = -SHIPS_MIN_LIMIT
    #endif

    if distance > DISTANCE_MAX_LIMIT:
        distance = DISTANCE_MAX_LIMIT
    elif distance <= 0:
        distance = 0
    #endif

    if game_time > GAME_TIME_LIMIT:
        game_time = GAME_TIME_LIMIT
    elif game_time <= 0:
        game_time = 0
    #endif

    opportunity.input['turn'] = game_time
    opportunity.input['dist'] = distance
    opportunity.input['ships'] = ships_surplus

    opportunity.compute()
    ret = opportunity.output['atck']
    #debug("Calculated for [turn {:4}] [distance {:5}] [ships {:5}] --> {:10}".format(game_time, distance, ships_surplus, ret))
    return ret

if __name__ == "__main__":
    SIM = 0
    for turn in range[1, MA]
        turn = random.randint(0, 201)
        dist = random.random() * 120
        ships_surplus = random.randint(-20, 30)
        fuzzify(turn, dist, ships_surplus)
        SIM += 1
    #endwhile
    # surplus_ships.view()
    # # total_ships_quantity.view()
    # # necessary_ships_quantity.view()
    # surplus_ships.view()
    # target_owner.view()
    # attack_opportunity.view()
    raw_input()
#endif
import numpy as np
import skfuzzy.control as ctrl
import random
import math

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

short_names=['nvb', 'nb', 'n', 'z', 'p', 'pb', 'pvb']

#create antecedents
turn = ctrl.Antecedent(np.arange(0, 201, 1), 'turn')
turn.automf(3, names=['early', 'mid', 'late'])

ships = ctrl.Antecedent(np.arange(-21, 30, 1), 'ships')
ships.automf(7)

dist = ctrl.Antecedent(np.arange(0, 400, 1), 'dist')
dist.automf(7, names=short_names)

atck = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'attack_opportunity')
atck.automf(7, names=short_names)

rules = []
#
#18 rules out of 147
rules.append(ctrl.Rule(antecedent=((turn['early']   & dist['pvb']   & ships['nvb']) |
                                   (turn['early']   & dist['pvb']   & ships['nb'])  |
                                   (turn['early']   & dist['pb']    & ships['nb'])) |
                                   (turn['early']   & dist['pb']    & ships['nvb']) |

                                   (turn['early']   & dist['p']     & ships['nvb']) |
                                   (turn['early']   & dist['p']     & ships['nb'])  |
                                   (turn['early']   & dist['pb']    & ships['z'])   |
                                   (turn['early']   & dist['pb']    & ships['z'])   |

                                   (turn['early']   & dist['z']     & ships['nvb']) |
                                   (turn['early']   & dist['n']     & ships['nb'])  |

                                   (turn['mid']     & dist['pvb']   & ships['nvb']) |
                                   (turn['mid']     & dist['pvb']   & ships['nb'])  |
                                   (turn['mid']     & dist['pb']    & ships['nb'])  |
                                   (turn['mid']     & dist['pb']    & ships['nvb']) |

                                   (turn['late']    & dist['pvb']   & ships['nvb']) |
                                   (turn['late']    & dist['pvb']   & ships['nb'])  |
                                   (turn['late']    & dist['pvb']   & ships['nb'])  |
                                   (turn['late']    & dist['pb']    & ships['nvb'])),
                       consequent=atck['nvb'], label='attack forbidden')


# + 8 = 26 rules out of 149
rules.append(ctrl.Rule(antecedent=((turn['early'] & dist['z']  & ships['nvb']) |
                                   (turn['early'] & dist['z']  & ships['nb'])  |
                                   (turn['early'] & dist['pb'] & ships['z'])   |
                                   (turn['early'] & dist['pb'] & ships['z'])   |

                                   (turn['late']  & dist['p']  & ships['nvb']) |
                                   (turn['late']  & dist['p']  & ships['nb'])  |
                                   (turn['late']  & dist['pb'] & ships['z'])   |
                                   (turn['late']  & dist['pb'] & ships['z']))),
                       consequent=atck['nb'], label='attack discouraged_no_ships_big_distance')

# + 12 = 38 rules
rules.append(ctrl.Rule(antecedent=((turn['early'] & dist['nvb'] & ships['nvb']) |
                                   (turn['early'] & dist['nvb'] & ships['nb'])  |
                                   (turn['early'] & dist['nvb'] & ships['z'])   |
                                   (turn['early'] & dist['nb'] & ships['z'])   |

                                   (turn['mid'] & dist['nb'] & ships['nvb']) |
                                   (turn['mid'] & dist['nb'] & ships['nb'])  |
                                   (turn['mid'] & dist['nb'] & ships['z'])   |
                                   (turn['mid'] & dist['nb'] & ships['z'])   |

                                   (turn['late'] & dist['p'] & ships['nvb']) |
                                   (turn['late'] & dist['p'] & ships['nb'])  |
                                   (turn['late'] & dist['pb'] & ships['z'])  |
                                   (turn['late'] & dist['pb'] & ships['z']))),
                       consequent=atck['n'], label='attack unlikely_no_ships_close_distance')

# + 12 = 50 rules
rules.append(ctrl.Rule(antecedent=((turn['early'] & dist['nvb'] & ships['nvb']) |
                                   (turn['early'] & dist['nvb'] & ships['nb'])  |
                                   (turn['early'] & dist['nvb'] & ships['z'])   |
                                   (turn['early'] & dist['nvb'] & ships['z'])   |

                                   (turn['mid'] & dist['nb'] & ships['nvb']) |
                                   (turn['mid'] & dist['nb'] & ships['nb'])  |
                                   (turn['mid'] & dist['nb'] & ships['z'])   |
                                   (turn['mid'] & dist['nb'] & ships['z'])   |

                                   (turn['late'] & dist['p'] & ships['nvb']) |
                                   (turn['late'] & dist['p'] & ships['nb'])  |
                                   (turn['late'] & dist['pb'] & ships['z'])  |
                                   (turn['late'] & dist['pb'] & ships['z']))),
                       consequent=atck['n'], label='attack unlikely_no_ships_close_distance')




# + 28 = 78 rules
rules.append(ctrl.Rule(antecedent=((turn['early'] & dist['nvb'] & ships['pvb']) |
                                   (turn['early'] & dist['nvb'] & ships['pb'])  |
                                   (turn['early'] & dist['nvb'] & ships['p'])   |

                                   (turn['mid']   & dist['nvb'] & ships['pvb']) |
                                   (turn['mid']   & dist['nvb'] & ships['pb'])  |
                                   (turn['mid']   & dist['nvb'] & ships['p'])   |

                                   (turn['late']  & dist['nvb'] & ships['pvb']) |
                                   (turn['late']  & dist['nvb'] & ships['pb'])  |
                                   (turn['late']  & dist['nvb'] & ships['p'])   |
                                   (turn['late']  & dist['nvb'] & ships['z'])

                                   (turn['early'] & dist['nb'] & ships['pvb'])  |
                                   (turn['early'] & dist['nb'] & ships['pb'])   |
                                   (turn['early'] & dist['nb'] & ships['p'])    |

                                   (turn['mid']   & dist['nb'] & ships['pvb'])  |
                                   (turn['mid']   & dist['nb'] & ships['pb'])   |
                                   (turn['mid']   & dist['nb'] & ships['p'])    |

                                   (turn['late']  & dist['nb'] & ships['pvb']   |
                                   (turn['late']  & dist['nb'] & ships['pb']    |
                                   (turn['late']  & dist['nb'] & ships['p']     |

                                   (turn['mid']  & dist['n'] & ships['pvb'])    |
                                   (turn['mid']  & dist['n'] & ships['pb'])     |
                                   (turn['mid']  & dist['n'] & ships['p'])      |

                                   (turn['late']  & dist['n'] & ships['pvb'])   |
                                   (turn['late']  & dist['n'] & ships['pb'])    |
                                   (turn['late']  & dist['n'] & ships['p'])     |

                                   (turn['late'] & dist['z'] & ships['pvb'])    |
                                   (turn['late'] & dist['z'] & ships['b'])      |
                                   (turn['late'] & dist['z'] & ships['z'])),
                       consequent=atck['pvb'], label='attack likely_have_ships_close_distance')

def calculate_opportunity(opportunity, game_time, distance, ships_surplus):
    print game_time, distance, ships_surplus

    if ships_surplus > 30:
        ships_surplus = 30
    elif ships_surplus < -20:
        ships_surplus = -20
    #endif

    opportunity.input['game_time'] = game_time
    opportunity.input['distance_to_target'] = distance
    opportunity.input['surplus_ships'] = ships_surplus

    opportunity.compute()

    print "Calculated for [turn {:4}] [distance {:5}] [ships {:5}] -->"\
        .format(game_time, distance, ships_surplus)

    print atck.view(sim=opportunity)

if __name__ == "__main__":
    opportunity_ctrl = ctrl.ControlSystem(rules)
    opportunity = ctrl.ControlSystemSimulation(opportunity_ctrl)

    SIM = 0
    while SIM < 1000:
        turn = random.randint(0, 10)
        dist = random.random() * 200 * math.sqrt(2)
        ships_surplus = random.randint(-100, 300)
        calculate_opportunity(opportunity, turn, dist, ships_surplus)
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
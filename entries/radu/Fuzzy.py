import numpy as np
import skfuzzy
import skfuzzy.control as ctrl
import os


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

#create antecedents
game_time = ctrl.Antecedent(np.arange(0, 201, 1), 'game_time')
game_time.automf(3, names=['early', 'mid', 'late'])

surplus_ships = ctrl.Antecedent(np.arange(-20, 30, 1), 'surplus_ships')
surplus_ships.automf(7)

distance_to_target = ctrl.Antecedent(np.arange(0, 50, 1), 'distance_to_target')
distance_to_target.automf(3, names=['negligible', 'tiny', 'small', 'medium', 'large', 'huge', 'unreachable'])

attack_opportunity = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'attack_opportunity')
attack_opportunity.automf(7)

rules = []
#
#
# rules.append(ctrl.Rule(distance_to_target['tiny'], attack_opportunity['good']))
# rules.append(ctrl.Rule(distance_to_target['negligible'], attack_opportunity['excellent']))

rules.append(ctrl.Rule(surplus_ships['dismal'], attack_opportunity['dismal']))
rules.append(ctrl.Rule(surplus_ships['poor'], attack_opportunity['poor']))

rules.append(ctrl.Rule((surplus_ships['poor'] & distance_to_target['huge']) |
                       (game_time['early'] & (distance_to_target['large'] & surplus_ships['mediocre'])),
                       attack_opportunity['poor']))

rules.append(ctrl.Rule((surplus_ships['mediocre'] & distance_to_target['large']) |
                       (game_time['early'] & (distance_to_target['medium'] & surplus_ships['average'])),
                       attack_opportunity['mediocre']))

rules.append(ctrl.Rule((surplus_ships['mediocre'] & distance_to_target['large']) |
                       (game_time['early'] & (distance_to_target['medium'] & surplus_ships['average'])),
                       attack_opportunity['mediocre']))

rules.append(ctrl.Rule(surplus_ships['mediocre'] & (distance_to_target['small'] | distance_to_target['medium']), attack_opportunity['average']))

rules.append(ctrl.Rule(((surplus_ships['decent'] | surplus_ships['average']) & (distance_to_target['medium'] | distance_to_target['large'])),
                       attack_opportunity['average']))

rules.append(ctrl.Rule(((surplus_ships['mediocre'] | surplus_ships['average']) & (distance_to_target['small'] | distance_to_target['medium'])),
                       attack_opportunity['average']))

rules.append(ctrl.Rule(((surplus_ships['decent'] | surplus_ships['average']) & (distance_to_target['small'] | distance_to_target['medium'])),
                       attack_opportunity['good']))

rules.append(ctrl.Rule(((surplus_ships['excellent'] | surplus_ships['good'] | surplus_ships['decent']) & distance_to_target['tiny']),
                       attack_opportunity['excellent']))

rules.append(ctrl.Rule(((surplus_ships['excellent'] | surplus_ships['good'] | surplus_ships['decent']) & distance_to_target['negligible']),
                       attack_opportunity['excellent']))

if __name__ == "__main__":
    opportunity_ctrl = ctrl.ControlSystem(rules)
    opportunity = ctrl.ControlSystemSimulation(opportunity_ctrl)
    opportunity.input['game_time'] = 1
    opportunity.input['distance_to_target'] = 49
    opportunity.input['surplus_ships'] = 10

    opportunity.compute()

    print opportunity.output['attack_opportunity']
    attack_opportunity.view(sim=opportunity)
    # surplus_ships.view()
    # # total_ships_quantity.view()
    # # necessary_ships_quantity.view()
    # surplus_ships.view()
    # target_owner.view()
    # attack_opportunity.view()
    raw_input()

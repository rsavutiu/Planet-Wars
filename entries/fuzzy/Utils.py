from Log import debug
import math
from Fuzzy import fuzzify_hashtable

def get_available_invasion_ships(my_planet, pw):
    invasion_ships = my_planet.NumShips() - 1
    planet_ships = my_planet.NumShips()

    turns = 0
    while turns < 30:
        fleets_coming_in = get_incoming_fleets_in_exacly_x_turns(my_planet.PlanetID(), turns, pw)
        invading_enemy_ships = sum([invasion_fleet.NumShips() for invasion_fleet in fleets_coming_in if invasion_fleet.Owner() == 2])
        invading_own_ships = sum([invasion_fleet.NumShips() for invasion_fleet in fleets_coming_in if invasion_fleet.Owner() == 1])
        planet_ships = planet_ships + my_planet.GrowthRate() + invading_own_ships - invading_enemy_ships
        invasion_ships = min(invasion_ships, planet_ships - 1)
        turns += 1
    #endwhile
    if invasion_ships < 0:
        invasion_ships = 0
    #emdof
    return invasion_ships


def get_necessary_invasion_ships(foreign_planet, distance_to_planet, pw):
    turn_until_my_fleet_arrives = int(distance_to_planet) + 1
    planet_owner = foreign_planet.Owner()

    # while turn_until_my_fleet_arrives > 0:
    #     fleets_coming_in = get_incoming_fleets_in_exacly_x_turns(foreign_planet.PlanetID(), turn_until_my_fleet_arrives, pw)
    #     if len(fleets_coming_in) > 0:
    #         invading_enemy_ships = sum([invasion_fleet.NumShips() for invasion_fleet in fleets_coming_in if invasion_fleet.Owner() == 2])
    #         invading_own_ships = sum([invasion_fleet.NumShips() for invasion_fleet in fleets_coming_in if invasion_fleet.Owner() == 1])
    #         # debug("turn {0} [invading enemy ships: {1}] [invading own ships: {2}]".format(
    #         #     turn_until_my_fleet_arrives, invading_enemy_ships, invading_own_ships))
    #
    #         if planet_owner == 0:
    #             if invading_enemy_ships > planet_ships and invading_enemy_ships > invading_own_ships:
    #                 planet_owner = 2
    #                 planet_ships = invading_enemy_ships - max(planet_ships, invading_own_ships)
    #             elif planet_ships >= invading_enemy_ships and planet_ships >= invading_own_ships:
    #                 planet_owner = 0
    #                 planet_ships = planet_ships - max(invading_enemy_ships, invading_own_ships)
    #             else:
    #                 planet_owner = 1
    #                 planet_ships = invading_own_ships - max(invading_enemy_ships, planet_ships)
    #             #endif
    #         elif planet_owner == 1:
    #             return 0
    #             # planet_ships = invading_enemy_ships - planet_ships - invading_own_ships
    #             # if planet_ships > 0:
    #             #     # change owner
    #             #     planet_owner = 2
    #             # else:
    #             #     planet_ships = 0 - planet_ships
    #             # #endif
    #         elif planet_owner == 2:
    #             planet_ships = invading_own_ships - planet_ships - invading_enemy_ships
    #             if planet_ships > 0:
    #                 #change owner
    #                 planet_owner = 1
    #                 return 0
    #             else:
    #                 planet_ships = 0 - planet_ships
    #             #endif
    #         #endif
    #     # else:
    #     #     debug("no fleets coming in at turn: {0}".format(turn_until_my_fleet_arrives))
    #     # #endif
    #     turn_until_my_fleet_arrives -= 1
    # #endwhile

    turn = 0
    if foreign_planet.Owner() != 1:
        balance =  foreign_planet.NumShips()
    else:
        balance =  0 - foreign_planet.NumShips()

    while turn < turn_until_my_fleet_arrives:

        enemy_fleets_coming_in = get_incoming_fleets_in_exacly_x_turns(foreign_planet.PlanetID(), turn_until_my_fleet_arrives, pw)
        enemy_ships_coming_in = reduce(lambda a,b: )
        own_ships_coming_in = 0

        #endfor
        turn += 1
    #endwhile
    if planet_owner == 1:
        return 0
    #endif
    # debug("Get necessary invasion ships for planet at distance {0} with currently {1} ships. We need: {2}"
    #       .format(distance_to_planet, foreign_planet.NumShips(), planet_ships))
    return planet_ships


def calculate_growth_opportunity(potential_target):
    if potential_target.GrowthRate() > 20:
        opportunity = 1.0
    elif potential_target.GrowthRate() > 15:
        opportunity = 0.99
    elif potential_target.GrowthRate() > 10:
        opportunity = 0.98
    elif potential_target.GrowthRate() > 9:
        opportunity = 0.95
    elif potential_target.GrowthRate() > 8:
        opportunity = 0.85
    elif potential_target.GrowthRate() > 7:
        opportunity = 0.75
    elif potential_target.GrowthRate() > 6:
        opportunity = 0.7
    elif potential_target.GrowthRate() > 5:
        opportunity = 0.6
    elif potential_target.GrowthRate() > 4:
        opportunity = 0.5
    elif potential_target.GrowthRate() > 3:
        opportunity = 0.3
    elif potential_target.GrowthRate() > 2:
        opportunity = 0.2
    elif potential_target.GrowthRate() > 1:
        opportunity = 0.1
    elif potential_target.GrowthRate() > 0:
        opportunity = 0.05
    else:
        opportunity = 0
    # endif
    return opportunity


def calculate_opportunity_fuzzy_logic(available_ships_for_invasion, necessary_ships_for_invasion,
                                      potential_target, distance_to_planet,
                                      turn):
    opportunity = 0
    if necessary_ships_for_invasion > 0:
        fuzzy_result = fuzzify_hashtable(
            turn, distance_to_planet, available_ships_for_invasion - necessary_ships_for_invasion)
        #fuzzy_result = 0.5
        delta_ships = available_ships_for_invasion - necessary_ships_for_invasion
        if turn < 20:
            if (distance_to_planet > 30 and delta_ships < 1):
                fuzzy_result = 0
            else:
                fuzzy_result = 0
            #endif
        #endif
        fuzzy_weight = 2

        growth_rate_opportunity = calculate_growth_opportunity(potential_target)
        growth_rate_weight = 1 + (1.0 - turn / 200.0) / 2

        owner_of_planet_opportunity = 1
        if potential_target.Owner() == 2:
            # theirs - they defend so it's less profitable to attack
            owner_of_planet_opportunity = min(1.0, 0.5 + (float(turn) / 200.0)/2)
        elif potential_target.Owner() == 1:
            # mine
            owner_of_planet_opportunity = 0.6
        elif potential_target.Owner() == 0:
            # neutral
            owner_of_planet_opportunity = 1
        # endif
        owner_of_planet_weight = 1

        # teritorry_center_of_gravity_opportunity = \
        #     calculate_center_of_gravity_opportunity(turn, potential_target, own_center_x, own_center_y)
        # teritorry_center_of_gravity_weight = 1 - (turn / 200.0) * 0.5

        opportunity = ((fuzzy_result * fuzzy_weight) + (growth_rate_opportunity * growth_rate_weight) + (owner_of_planet_opportunity * owner_of_planet_weight)) /\
                       (fuzzy_weight + growth_rate_weight + owner_of_planet_weight)
    #endif
    return opportunity




def get_my_planets(pw):
    return filter(lambda x: x.Owner() == 1, pw.Planets())


def get_enemy_planets(pw):
    return filter(lambda x: x.Owner() == 2, pw.Planets())


def get_foreign_planets(pw):
    return filter(lambda x: x.Owner() != 1, pw.Planets())


def get_incoming_fleets(planet_id, pw):
    return filter(lambda x: x.DestinationPlanet() == planet_id, pw.Fleets())


def get_incoming_fleets_in_exacly_x_turns(planet_id, turns, pw):
    ret = filter(lambda x: x.DestinationPlanet() == planet_id and x.TurnsRemaining() == turns, pw.Fleets())
    return ret

def get_incoming_enemy_fleets_in_exacly_x_turns(planet_id, turns, pw):
    ret = filter(lambda x: x.DestinationPlanet() == planet_id and x.TurnsRemaining() == turns and x.Owner() == 2, pw.Fleets())
    return ret

def get_incoming_own_fleets_in_exacly_x_turns(planet_id, turns, pw):
    ret = filter(lambda x: x.DestinationPlanet() == planet_id and x.TurnsRemaining() == turns and x.Owner() == 1, pw.Fleets())
    return ret

def get_incoming_opponent_fleets(planet_id, pw):
    return filter(lambda x: x.DestinationPlanet() == planet_id and x.Owner() == 2, pw.Fleets())


# def find_closest_own_planets(target_planet_id, pw):
#     sources = []
#     my_planets_ids = map(lambda x: x.PlanetID(), pw.MyPlanets())
#     for nearest_neighbor in nearestNeighbors[target_planet_id]:
#         if my_planets_ids.count(nearest_neighbor[0]):
#             sources.append(nearest_neighbor[0])
#             # endif
#     # endfor
#     return sources

def get_planet_type(target):
    if target.Owner() == 0:
        target_type = " Neutral "
    elif target.Owner() == 1:
        target_type = " OWN!!!! "
    elif target.Owner() == 2:
        target_type = " enemy "
    #endif
    return target_type


def send(pw, my_planet, target, available_invasion_ships, distances):
    target_type = get_planet_type(target)
    if (target.Owner()==1):
        debug(
        "Send relief force {0} ships from planet id {1} to {2} planet id {3} which currently has {4} ships landed on it"
            .format(available_invasion_ships, my_planet.PlanetID(), target_type, target.PlanetID(),
                    target.NumShips()))
    else:
        debug(
            "Send invasion force {0} ships from planet id {1} to {2} planet id {3} which currently has {4} ships landed on it"
                .format(available_invasion_ships, my_planet.PlanetID(), target_type, target.PlanetID(),
                        target.NumShips()))
    #endif
    pw.IssueOrderByIds(my_planet.PlanetID(), target.PlanetID(), available_invasion_ships)
    # pw._fleets.append(Fleet(1,  # Owner is ME
    #                                    available_invasion_ships/10,  # Num ships
    #                                    my_planet.PlanetID(),  # Source
    #                                    target.PlanetID(),  # Destination
    #                                    distances[my_planet.PlanetID(), target.PlanetID()],  # Total trip length
    #                                    distances[my_planet.PlanetID(), target.PlanetID()]))  # Turns remaining)
    my_planet.NumShips(new_num_ships=my_planet.NumShips() - available_invasion_ships)


if __name__ == "__main__":
    get_necessary_invasion_ships()
    pass



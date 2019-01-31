from PlanetWars import PlanetWars
from PlanetWars import Planet
from PlanetWars import Fleet
from math import ceil
from Log import debug
from PlanetSim import PlanetSim
import math
import numpy as np
import skfuzzy
from skfuzzy import control



def calculate_center_of_gravity(planets):
    x = 0
    y = 0
    for planet in planets:
        x += planet.X()
        y += planet.Y()
    # endfor
    x = x / len(planets)
    y = y / len(planets)
    return x, y


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


def get_necessary_invasion_ships (foreign_planet, distance_to_planet, pw):
    turn_until_my_fleet_arrives = int(distance_to_planet)
    planet_ships = foreign_planet.NumShips() + 1
    planet_owner = foreign_planet.Owner()

    while turn_until_my_fleet_arrives > 0:
        fleets_coming_in = get_incoming_fleets_in_exacly_x_turns(foreign_planet.PlanetID(), turn_until_my_fleet_arrives, pw)
        if len(fleets_coming_in) > 0:
            invading_enemy_ships = sum([invasion_fleet.NumShips() for invasion_fleet in fleets_coming_in if invasion_fleet.Owner() == 2])
            invading_own_ships = sum([invasion_fleet.NumShips() for invasion_fleet in fleets_coming_in if invasion_fleet.Owner() == 1])
            # debug("turn {0} [invading enemy ships: {1}] [invading own ships: {2}]".format(
            #     turn_until_my_fleet_arrives, invading_enemy_ships, invading_own_ships))

            if planet_owner == 0:
                if invading_enemy_ships > planet_ships and invading_enemy_ships > invading_own_ships:
                    planet_owner = 2
                    planet_ships = invading_enemy_ships - max(planet_ships, invading_own_ships)
                elif planet_ships >= invading_enemy_ships and planet_ships >= invading_own_ships:
                    planet_owner = 0
                    planet_ships = planet_ships - max(invading_enemy_ships, invading_own_ships)
                else:
                    planet_owner = 1
                    planet_ships = invading_own_ships - max(invading_enemy_ships, planet_ships)
                #endif
            elif planet_owner == 1:
                return 0
                # planet_ships = invading_enemy_ships - planet_ships - invading_own_ships
                # if planet_ships > 0:
                #     # change owner
                #     planet_owner = 2
                # else:
                #     planet_ships = 0 - planet_ships
                # #endif
            elif planet_owner == 2:
                planet_ships = invading_own_ships - planet_ships - invading_enemy_ships
                if planet_ships > 0:
                    #change owner
                    planet_owner = 1
                    return 0
                else:
                    planet_ships = 0 - planet_ships
                #endif
            #endif
        # else:
        #     debug("no fleets coming in at turn: {0}".format(turn_until_my_fleet_arrives))
        # #endif
        turn_until_my_fleet_arrives -= 1
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


def calculate_distance_to_planet(distance_to_planet, target, surplus_ships):
    if distance_to_planet > 400:
        opportunity = 0.0001
    elif distance_to_planet > 250:
        opportunity = 0.0005
    elif distance_to_planet > 100:
        opportunity = 0.0010
    elif distance_to_planet > 50:
        opportunity = 0.0020
    elif distance_to_planet > 40:
        opportunity = 0.0050
    elif distance_to_planet > 30:
        opportunity = 0.0100
    elif distance_to_planet > 20:
        opportunity = 0.1
    elif distance_to_planet > 15:
        opportunity = 0.2
    elif distance_to_planet > 12:
        opportunity = 0.3000
    elif distance_to_planet > 10:
        opportunity = 0.4
    elif distance_to_planet > 7:
        opportunity = 0.5
    elif distance_to_planet > 5:
        opportunity = 0.6
    elif distance_to_planet > 4:
        opportunity = 0.7
    elif distance_to_planet > 3:
        opportunity = 0.8
    elif distance_to_planet > 2:
        opportunity = 0.900
    elif distance_to_planet > 1:
        opportunity = 0.999
    else:
        # neutral
        opportunity = 1
    # endif
    if surplus_ships < 0:
        opportunity /= 3
    elif surplus_ships < 10:
        opportunity /= 1.3

    return opportunity


def calculate_opportunity_fuzzy_logic(available_ships_for_invasion, necessary_ships_for_invasion,
                                      potential_target, distance_to_planet,
                                      own_center_x, own_center_y, turn):

    number_of_ships_opportunity = calculate_number_of_ships_oppportunity(potential_target)
    number_of_ships_weight = 1.0 - turn / 200.0

    surplus_ships = available_ships_for_invasion - necessary_ships_for_invasion
    surplus_ships_opportunity = calculate_surplus_ships_opportunity(surplus_ships)
    surplus_ships_weight = 1.0

    growth_rate_opportunity = calculate_growth_opportunity(potential_target)
    growth_rate_weight = 0.5 + (1.0 - turn / 200.0) / 2

    distance_to_planet_opportunity = calculate_distance_to_planet(distance_to_planet, potential_target, surplus_ships)
    distance_to_planet_weight = 0.8 + (1 - turn / 200.0) * 0.2

    owner_of_planet_opportunity = 1
    if potential_target.Owner() == 2:
        # theirs - they defend so it's less profitable to attack
        owner_of_planet_opportunity = min(1.0, 0.3 + float(turn) / 200.0)
    elif potential_target.Owner() == 1:
        # mine
        owner_of_planet_opportunity = 0.6
    elif potential_target.Owner() == 0:
        # neutral
        owner_of_planet_opportunity = 1
    # endif
    owner_of_planet_weight = 1

    teritorry_center_of_gravity_opportunity = \
        calculate_center_of_gravity_opportunity(turn, potential_target, own_center_x, own_center_y)
    teritorry_center_of_gravity_weight = 1 - (turn / 200.0) * 0.5

    opportunity = (number_of_ships_opportunity * number_of_ships_weight +
                   surplus_ships_opportunity * surplus_ships_weight +
                   growth_rate_opportunity * growth_rate_weight +
                   distance_to_planet_opportunity * distance_to_planet_weight +
                   owner_of_planet_opportunity * owner_of_planet_weight +
                   teritorry_center_of_gravity_opportunity * teritorry_center_of_gravity_weight) /\
                (number_of_ships_weight +
                 surplus_ships_weight +
                 growth_rate_weight +
                 distance_to_planet_weight +
                 owner_of_planet_weight +
                 teritorry_center_of_gravity_weight)

    return opportunity


def calculate_center_of_gravity_opportunity(turn, potential_target, own_center_x, own_center_y):
    opportunity = 1
    if turn > 50:
        distance_to_own_center = math.sqrt(abs(potential_target.X() * potential_target.X() - own_center_x * own_center_x) +
                                           abs(potential_target.Y() * potential_target.Y() - own_center_y * own_center_y))

        if distance_to_own_center > 400:
            # neutral
            opportunity = 0.2
        elif distance_to_own_center > 300:
            # neutral
            opportunity = 0.5
        elif distance_to_own_center > 200:
            # neutral
            opportunity = 0.7
        elif distance_to_own_center > 100:
            # neutral
            opportunity = 0.80
        elif distance_to_own_center > 50:
            # neutral
            opportunity = 0.90
        elif distance_to_own_center > 40:
            # neutral
            opportunity = 0.92
        elif distance_to_own_center > 30:
            # neutral
            opportunity = 0.95
        elif distance_to_own_center > 20:
            # neutral
            opportunity = 0.96
        elif distance_to_own_center > 15:
            # neutral
            opportunity = 0.97
        elif distance_to_own_center > 10:
            # neutral
            opportunity = 0.98
        elif distance_to_own_center > 5:
            # neutral
            opportunity = 0.99
        else:
            # neutral
            opportunity = 1
        # endif
    #endif
    return opportunity

def calculate_number_of_ships_oppportunity(potential_target):
    if potential_target.NumShips() < 5:
        opportunity = 1.0
    elif potential_target.NumShips() < 10:
        opportunity = 0.9500
    elif potential_target.NumShips() < 15:
        opportunity = 0.9000
    elif potential_target.NumShips() < 20:
        opportunity = 0.8000
    elif potential_target.NumShips() < 25:
        opportunity = 0.700
    elif potential_target.NumShips() < 30:
        opportunity = 0.6000
    elif potential_target.NumShips() < 35:
        opportunity = 0.5000
    elif potential_target.NumShips() < 40:
        opportunity = 0.400
    elif potential_target.NumShips() < 45:
        opportunity = 0.300
    elif potential_target.NumShips() < 50:
        opportunity = 0.2000
    elif potential_target.NumShips() < 60:
        opportunity = 0.1000
    elif potential_target.NumShips() < 70:
        opportunity = 0.0800
    elif potential_target.NumShips() < 90:
        opportunity = 0.0400
    elif potential_target.NumShips() < 100:
        opportunity = 0.0300
    elif potential_target.NumShips() < 120:
        opportunity = 0.0200
    else:
        opportunity = 0.01
    return opportunity


def calculate_surplus_ships_opportunity(surplus_ships):
    opportunity = 1.0
    if surplus_ships > 100:
        opportunity = 1.0
    elif surplus_ships > 80:
        opportunity = 0.98
    elif surplus_ships > 60:
        opportunity = 0.95
    elif surplus_ships > 40:
        opportunity = 0.9
    elif surplus_ships > 20:
        opportunity = 0.8
    elif surplus_ships > 10:
        opportunity = 0.6
    elif surplus_ships > 1:
        opportunity = 0.4
    else:
        return 0
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
    # if len(ret) > 0:
    #     debug("get incoming fleets for planet id {0} in {1} turns = {2} fleets".format(planet_id, turns, len(ret)))
    # #endif
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

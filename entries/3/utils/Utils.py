from Log import debug
import pickledict
import FleetsHelper
import PlanetHelper
import CenterOfGravity

SHIPS_MIN_LIMIT = -2
SHIPS_MAX_LIMIT = 2
DISTANCE_MAX_LIMIT = 20
GAME_SPARSE_TIME_LIMIT = 40
TOTAL_GAME_TIME = 200


def fuzzify_hashtable(game_time, distance, ships_surplus):
    game_time += 1
    distance = int(distance)
    if game_time < 0:
        game_time = 0
    elif game_time >= GAME_SPARSE_TIME_LIMIT:
        game_time = GAME_SPARSE_TIME_LIMIT - 1
    #endif

    if distance >= DISTANCE_MAX_LIMIT:
        distance = int(DISTANCE_MAX_LIMIT - 1)
    # endif

    if ships_surplus < SHIPS_MIN_LIMIT:
        ships_surplus = SHIPS_MIN_LIMIT
    elif ships_surplus > SHIPS_MAX_LIMIT:
        ships_surplus = SHIPS_MAX_LIMIT
    #endif

    if not pickledict.a.has_key((game_time, distance, ships_surplus)):
        return 0
    #endif

    return pickledict.a[(game_time, distance, ships_surplus)]


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
                                      potential_target, distance_to_planet, turn, max_distance):
    opportunity = 0
    if necessary_ships_for_invasion > 0:
        fuzzy_result = fuzzify_hashtable(
            turn * GAME_SPARSE_TIME_LIMIT / TOTAL_GAME_TIME, CenterOfGravity.get_weighted_distance_to_planet(max_distance, distance_to_planet),
                available_ships_for_invasion - necessary_ships_for_invasion)

        fuzzy_result *= (6 + float(min(potential_target.GrowthRate(), 14)) / 20.0)
        #debug("fuzzy result: {0}".format(fuzzy_result))
        fuzzy_result *= (0.9 + max(100 - necessary_ships_for_invasion, 0) / 1000.0)
        fuzzy_result *= (max_distance - distance_to_planet) / max_distance

    #endif
    return fuzzy_result


def send(pw, my_planet, target, available_invasion_ships):
    target_type = PlanetHelper.get_planet_type(target)
    if target.Owner() == 1:
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


if __name__=="__main__":
    from PlanetWars import Planet
    #calculate_opportunity_fuzzy_logic(available_ships_for_invasion, necessary_ships_for_invasion,
    #                                      potential_target, distance_to_planet, turn, max_distance)
    planet = Planet(1, 2, 4, 6, 1, 1)
    print calculate_opportunity_fuzzy_logic(available_ships_for_invasion=50, necessary_ships_for_invasion=4,
                                          potential_target=planet, distance_to_planet=100, turn=50, max_distance=100)
from Log import debug
import FleetsHelper
import PlanetHelper
from PlanetWars import Fleet
import CenterOfGravity


def send(pw, my_planet, target, available_invasion_ships, distance):
    target_type = PlanetHelper.get_planet_type(target)
    if target.Owner() == 1:
        debug(
            "Send relief force {0} ships from planet id {1} to {2} planet id {3} which currently has {4} ships landed "
            "on it "
                .format(available_invasion_ships, my_planet.PlanetID(), target_type, target.PlanetID(),
                        target.NumShips()))
    else:
        debug(
            "Send invasion force {0} ships from planet id {1} to {2} planet id {3} which currently has {4} ships "
            "landed on it "
                .format(available_invasion_ships, my_planet.PlanetID(), target_type, target.PlanetID(),
                        target.NumShips()))
    # endif
    pw.IssueOrderByIds(my_planet.PlanetID(), target.PlanetID(), available_invasion_ships)
    pw._fleets.append(Fleet(1,  # Owner is ME
                            available_invasion_ships,  # Num ships
                            my_planet,  # Source
                            target,  # Destination
                            distance,  # Total trip length
                            distance))  # Turns remaining)
    my_planet.NumShips(new_num_ships=my_planet.NumShips() - available_invasion_ships)


if __name__ == "__main__":
    from PlanetWars import Planet

    # calculate_opportunity_fuzzy_logic(available_ships_for_invasion, necessary_ships_for_invasion,
    #                                      potential_target, distance_to_planet, turn, max_distance)
    planet = Planet(1, 2, 4, 6, 1, 1)
    # print calculate_opportunity_fuzzy_logic(available_ships_for_invasion=50, necessary_ships_for_invasion=4,
    #                                       potential_target=planet, distance_to_planet=100, turn=50, max_distance=100)

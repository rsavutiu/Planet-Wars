from Log import debug
import PlanetHelper
from PlanetWars import Fleet
import math


def compute_planet_distances_and_max_planet_size(pw, max_planet_size, max_distance, nearest_neighbors):
    actual_distances = []
    distances = {}
    planets = sorted(pw.Planets(), key=lambda x: x.PlanetID())
    for p in planets:
        if p.GrowthRate() > max_planet_size:
            max_planet_size = p.GrowthRate()
        # endif
        dists = []
        distances[p.PlanetID()] = {}
        for q in planets:
            if q.PlanetID() != p.PlanetID():
                dx = p.X() - q.X()
                dy = p.Y() - q.Y()
                actual_distance = math.sqrt(dx * dx + dy * dy)
                x = (q.PlanetID(), actual_distance)
                dists.append(x)
                actual_distances.append(actual_distance)
                if actual_distance > max_distance:
                    max_distance = actual_distance
                # endif
                distances[p.PlanetID()][q.PlanetID()] = actual_distance
            # endif
        # endfor
        nearest_neighbors[p.PlanetID()] = sorted(dists, key=lambda x: x[1])
    # endfor
    return actual_distances, nearest_neighbors, distances, max_distance


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

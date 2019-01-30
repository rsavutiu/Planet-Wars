from PlanetWars import PlanetWars
from PlanetWars import Planet
from math import ceil
from Log import debug
from PlanetSim import PlanetSim
import math

def calculate_center_of_gravity(planets):
    x = 0
    y = 0
    for planet in planets:
        x += planet.X()
        y += planet.Y()
    #endfor
    x = x/len(planets)
    y = y / len(planets)

    distances_to_center = {}
    for planet in planets:
        dx = abs(planet.X() - x)
        dy = abs(planet.Y() - y)
        distances_to_center[planet.PlanetID()] = math.sqrt(dx*dx + dy*dy)
    #endfor

    return x, y, distances_to_center


def get_available_invasion_ships(my_planet, pw):
    invasion_ships = my_planet.NumShips() - 1
    incoming_fleets = get_incoming_fleets(my_planet.PlanetID(), pw)
    for incoming_fleet in incoming_fleets:
        if incoming_fleet.Owner() == 2:
            #enemy fleet!
            invasion_ships -= incoming_fleet.NumShips()
        else:
            #friendly fleet!
            invasion_ships += incoming_fleet.NumShips()
        # endif
    # endfor
    invasion_ships = min(invasion_ships, my_planet.NumShips() - 1)
    return invasion_ships


def get_necessary_invasion_ships(foreign_planet, distance_to_planet, pw):
    necessary_ships = foreign_planet.NumShips()
    if (foreign_planet.Owner()==2):
        #in enemy hands. we're going to need a bigger wrench...
        necessary_ships += distance_to_planet * foreign_planet.GrowthRate()
    #endif
    incoming_fleets = get_incoming_fleets(foreign_planet.PlanetID(), pw)
    for incoming_fleet in incoming_fleets:
        if incoming_fleet.Owner() == 1:
            #my invasion fleet!
            necessary_ships -= incoming_fleet.NumShips()
        else:
            #eneymy relief fleet!
            necessary_ships += incoming_fleet.NumShips()
        # endif
    # endfor

    if necessary_ships < 0: necessary_ships = 0
    return necessary_ships


def calculate_opportunity(available_ships_for_invasion, necessary_ships_for_invasion, nearest_neighbor, distance_to_planet):
    opportunity = ((available_ships_for_invasion * 1.0)/necessary_ships_for_invasion)
    opportunity *= nearest_neighbor.GrowthRate() * 100
    opportunity /= math.pow(distance_to_planet, 4)

    if nearest_neighbor.Owner() == 2:
        opportunity /= 4
    #endif

    if (available_ships_for_invasion < necessary_ships_for_invasion):
        opportunity /= 5
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


def send(pw, my_planet, nearestNeighbor, available_invasion_ships, distances):
    debug(
        "Send {0} ships from planet id {1} to planet id {2} which currently has {3} ships landed on it"
            .format(available_invasion_ships, my_planet.PlanetID(), nearestNeighbor.PlanetID(),
                    nearestNeighbor.NumShips()))
    pw.IssueOrderByIds(my_planet.PlanetID(), nearestNeighbor.PlanetID(), available_invasion_ships)
    # pw._fleets.append(PlanetWars.Fleet(1,  # Owner is ME
    #                                    available_invasion_ships,  # Num ships
    #                                    my_planet.PlanetID(),  # Source
    #                                    nearestNeighbor.PlanetID(),  # Destination
    #                                    distances[my_planet.PlanetID(), nearestNeighbor.PlanetID()],  # Total trip length
    #                                    distances[my_planet.PlanetID(), nearestNeighbor.PlanetID()]))  # Turns remaining)
    #my_planet.NumShips(new_num_ships=my_planet.NumShips() - available_invasion_ships)
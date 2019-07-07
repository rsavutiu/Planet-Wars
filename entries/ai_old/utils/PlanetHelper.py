import FleetsHelper
from Log import debug

def get_my_planets(pw):
    return filter(lambda x: x.Owner() == 1, pw.Planets())


def get_enemy_planets(pw):
    return filter(lambda x: x.Owner() == 2, pw.Planets())


def get_foreign_planets(pw):
    return filter(lambda x: x.Owner() != 1, pw.Planets())


def get_planet_type(target):
    if target.Owner() == 0:
        target_type = " Neutral "
    elif target.Owner() == 1:
        target_type = " OWN!!!! "
    elif target.Owner() == 2:
        target_type = " enemy "
    #endif
    return target_type


def get_ships_on_planet_on_turn_x(my_planet, turn, pw):
    ships = my_planet.NumShips() + my_planet.GrowthRate() * turn
    all_fleets = filter(lambda x: x.DestinationPlanet() == my_planet.PlanetID() and
                                  x.TurnsRemaining() <= turn, pw.Fleets())
    for fleet in all_fleets:
        if fleet.Owner() == 1:
            ships += fleet.NumShips()
        else:
            ships -= fleet.NumShips()
        #endif
    #endfor
    return ships


def get_necessary_invasion_ships(foreign_planet, distance_to_planet, pw, max_distance):
    turn_until_my_fleet_arrives = int(distance_to_planet)
    planet_owner = foreign_planet.Owner()
    planet_ships = foreign_planet.NumShips()
    turn = 0
    total_own_ships_coming_in = 0
    # planet_ships_need_to_leave_now = 0
    while turn <= turn_until_my_fleet_arrives + 1:
        enemy_ships_coming_in = 0
        own_ships_coming_in = 0

        enemy_fleets_coming_in = FleetsHelper.get_incoming_enemy_fleets_in_exacly_x_turns(
            foreign_planet.PlanetID(), turn, pw)
        if len(enemy_fleets_coming_in) > 0:
            for enemy_fleet in enemy_fleets_coming_in:
                enemy_ships_coming_in += enemy_fleet.NumShips()
            #endfor
        #endif

        own_fleets_coming_in = FleetsHelper.get_incoming_own_fleets_in_exacly_x_turns(
            foreign_planet.PlanetID(), turn, pw)
        if len(own_fleets_coming_in) > 0:
            for own_fleet in own_fleets_coming_in:
                own_ships_coming_in += own_fleet.NumShips()
            #endfor
        #endif
        total_own_ships_coming_in += own_ships_coming_in
        turn += 1

        if planet_owner == 0:
            #neutral planet
            if planet_ships < max(enemy_ships_coming_in, own_ships_coming_in):
                planet_ships = max(enemy_ships_coming_in, own_ships_coming_in) - planet_ships
                if enemy_ships_coming_in > own_ships_coming_in:
                    planet_owner = 2
                else:
                    planet_owner = 1
                #endif
            else:
                #remains neutral
                planet_ships = planet_ships - max(enemy_ships_coming_in, own_ships_coming_in)
            #endif
        elif planet_owner == 1:
            #own planet
            planet_ships += own_ships_coming_in + foreign_planet.GrowthRate()
            if planet_ships < enemy_ships_coming_in:
                # got conquered by enemy
                planet_owner = 2
                planet_ships = enemy_ships_coming_in - planet_ships
            else:
                # stay in my possesion
                planet_ships = planet_ships - enemy_ships_coming_in
            #endif
        else:
            #enemy planet
            planet_ships += enemy_ships_coming_in + foreign_planet.GrowthRate()
            if planet_ships < own_ships_coming_in:
                # got conquered by me
                planet_owner = 1
                planet_ships = own_ships_coming_in - planet_ships
            else:
                #stay in the hands of the enemy
                planet_ships = planet_ships - own_ships_coming_in
            # endif

        # if planet_owner != 1 and turn == turn_until_my_fleet_arrives:
        #     planet_ships_need_to_leave_now = planet_ships + 1
    # endwhile

    if planet_owner == 1:
        # debug("Get necessary invasion ships for planet {0} at distance {1} with currently {2} ships. We have already {3} ships coming in. We are NOT sending more ships"
        # .format(foreign_planet.PlanetID(), distance_to_planet, foreign_planet.NumShips(), total_own_ships_coming_in))
        return 0
    # endif

    # debug("Get necessary invasion ships for planet {0} at distance {1} with currently {2} ships. We have already {3} ships coming in. We need to send {4} more ships"
    #       .format(foreign_planet.PlanetID(), distance_to_planet, foreign_planet.NumShips(), total_own_ships_coming_in, planet_ships + 1))
    return planet_ships + 1


def get_available_invasion_ships(my_planet, pw):
    incoming_fleet_set_of_turns = set([fleet.TurnsRemaining() for fleet in
                                       FleetsHelper.get_incoming_opponent_fleets(my_planet.PlanetID(), pw)])
    invasion_ships = my_planet.NumShips()

    for turn in incoming_fleet_set_of_turns:
        if turn > 0:
            ships_here_on_turn_x = get_ships_on_planet_on_turn_x(my_planet, turn, pw)

            if ships_here_on_turn_x < 0:
                return 0
            elif invasion_ships > ships_here_on_turn_x:
                invasion_ships = ships_here_on_turn_x
    #endfor

    if invasion_ships < 0:
        invasion_ships = 0
    #endif

    if invasion_ships > my_planet.NumShips():
        invasion_ships = my_planet.NumShips()
    #endif

    # debug("invade with max {0} out of {1}".format(invasion_ships, my_planet.NumShips()))
    return invasion_ships

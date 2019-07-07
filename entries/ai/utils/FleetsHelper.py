def get_incoming_fleets(planet_id, pw):
    return filter(lambda x: x.DestinationPlanet() == planet_id, pw.Fleets())


def get_incoming_fleets_in_exacly_x_turns(planet_id, turns, pw):
    ret = filter(lambda x: x.DestinationPlanet() == planet_id and x.TurnsRemaining() == turns, pw.Fleets())
    # if len(ret) > 0:
    #     debug("get incoming fleets for planet id {0} in {1} turns = {2} fleets".format(planet_id, turns, len(ret)))
    # #endif
    return ret


def get_incoming_enemy_fleets_in_exacly_x_turns(planet_id, turns, pw):
    ret = filter(lambda x: x.DestinationPlanet() == planet_id and x.TurnsRemaining() == turns and x.Owner() == 2, pw.Fleets())
    # if len(ret) > 0:
    #     debug("get incoming enemy fleets for planet id {0} in {1} turns = {2} fleets".format(planet_id, turns, len(ret)))
    # #endif
    return ret


def get_incoming_own_fleets_in_exacly_x_turns(planet_id, turns, pw):
    ret = filter(lambda x: x.DestinationPlanet() == planet_id and x.TurnsRemaining() == turns and x.Owner() == 1, pw.Fleets())
    # if len(ret) > 0:
    #     debug("get incoming own fleets for planet id {0} in {1} turns = {2} fleets".format(planet_id, turns, len(ret)))
    # #endif
    return ret


def get_incoming_opponent_fleets(planet_id, pw):
    return filter(lambda x: x.DestinationPlanet() == planet_id and x.Owner() == 2, pw.Fleets())
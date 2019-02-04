import math


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


def get_weighted_distance_to_planet(max_distance, distance):
    return int((((max_distance-distance) * 5.0) / max_distance) - 2)
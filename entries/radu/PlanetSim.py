from PlanetWars import PlanetWars
from PlanetWars import Planet
from math import ceil
from Log import debug


class PlanetSim:
    """Useful for predicting the future state of a planet based on
    incoming fleets
    Always uses the convention that my ships and planets are positive
    Enemy and neutral are negative.
    """

    def __init__(self, startingShips, rate, isNeutral):
        if isNeutral:
            self.startingShips = 0
            self.neutralShips = startingShips
        else:
            self.startingShips = startingShips
            self.neutralShips = 0
        self.rate = rate
        self.fleets = []

    def add_fleet(self, turn, numShips):
        self.fleets.append((turn, numShips))

    def del_fleet(self, turn, numShips):
        self.fleets.remove((turn, numShips))

    def find_min_fleet_own(self, turn):
        # what if we do nothing
        left = self.simulate()
        if left > 0:  # Already have it
            debug("Already have it")
            return 0
        curr_fleet_size = 0
        while left < 0:
            # May have to adjust increment to prevent timeout
            curr_fleet_size += 4
            self.add_fleet(turn, curr_fleet_size)
            left = self.simulate()
            # debug("currfleet: " + str(curr_fleet_size) + " left: " + str(left))
            self.del_fleet(turn, curr_fleet_size)
        if left == 0:
            curr_fleet_size += 1
        return curr_fleet_size

    def find_max_expenditure_while_keeping(self):
        """ Assumes we own the planet in question """
        # May have to adjust increment to prevent timeout
        increment = 4
        # what if we do nothing?
        left = self.simulate()
        # we're gonna lose it, can't spend a dime
        if left <= 0:
            return 0
        else:
            startingShips = self.startingShips
            maxSpend = 0
            while left > 0:
                # can't spend more than you have
                if maxSpend + increment >= startingShips:
                    break
                maxSpend += increment
                if startingShips <= increment:
                    break
                self.startingShips -= maxSpend
                left = self.simulate()
                debug("left: " + str(left) + " spent: " + str(maxSpend))
                # restore startingShips state
                self.startingShips = startingShips
            # check if we failed on last simulation
            # if so, take 2 back
            if left <= 0:
                return maxSpend - increment
            return maxSpend

    def simulate(self):
        """After all fleets have come in, how many ships does the planet have?"""

        def reducedFleets():
            """Reduce the fleets so that if multiple fleets happen on
            the same turn, there combined effect is reduced to one
            event"""
            reduced = []
            fleets = sorted(self.fleets, key=lambda x: x[0])
            currTurn = 0
            reducedValue = 0
            for e in fleets:
                if e[0] == currTurn:
                    reducedValue += e[1]
                else:
                    reduced.append((currTurn, reducedValue))
                    reducedValue = e[1]
                    currTurn = e[0]
            if reducedValue:
                reduced.append((currTurn, reducedValue))
            return reduced

        currTurn = 0
        ships = self.startingShips
        neuShips = self.neutralShips
        for e in reducedFleets():
            remain = e[1]
            # debug("fleetSize: " + str(remain))
            # Remove Neutrals if any
            if neuShips < 0:
                if abs(remain) >= abs(neuShips):
                    if remain > 0:
                        remain += neuShips
                    else:
                        remain -= neuShips
                    neuShips = 0
                    currTurn = e[0]
                else:
                    neuShips += abs(remain)
                    remain = 0
                #endif
            #endif
            # If there are no neutrals, update planet and apply remaining fleet
            if neuShips == 0 and remain != 0:
                turns = e[0] - currTurn
                # debug("turns:" + str(turns) + " remain: " + str(remain))
                if ships >= 0:
                    ships = ships + self.rate * turns + remain
                else:
                    ships = ships - self.rate * turns + remain
                #endif
            #endif
            # Update turn
            # debug("ships: " + str(ships))
            currTurn = e[0]
        if neuShips:
            return neuShips
        else:
            return ships
        #endif

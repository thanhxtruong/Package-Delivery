import sys


# This Route class is used to hold each route traveled by trucks.
# It is used as keys in the Truck -> routes{} dictionary of the Truck class.
class Route:
    def __init__(self, start_vertex, end_vertex, departure, arrival):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.departure = departure
        self.arrival = arrival


class Truck:
    def __init__(self, id):
        self.id = id
        # A dictionary of Route(key) / [Packages] pairs, which is populated as packages are loaded
        # onto trucks.
        # [Packages] is list of all packages that have the same delivery address.
        self.routes = {}
        # Total packages loaded onto truck, which is during package loading as a flag that truck
        # is full.
        self.total_packages = 0
        # Address of truck's current location, which is used during package loading and delivery
        # simulation.
        self.current_location = None
        # Departure time is recalculated for each route
        self.departure = None
        # Pickup_time is the fixed time of when truck start its day (8 AM for trucks with drivers
        # and whatever time the driver of the back-up truck finished delivery of the first truck.
        self.pickup_time = None
        # Used to keep track of trucks with driver and back-up trucks
        self.driver = None
        # List of all packages that must be delivered by this truck, which is established by the
        # combination of user-specified requirements for required truck and packages that must
        # be delivered together.
        self.reserved_pkg = []
        # Used as a flag when all packages have been delivered in order to start loading packages
        # onto back-up truck
        self.completed_all_routes = False

    def __str__(self):
        return self.id

    # Override equality comparison to compare based on truck name
    def __eq__(self, other):
        if isinstance(other, Truck):
            return self.id == other.id
        else:
            return NotImplemented

    # Override inequality comparison to compare based on truck name
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    # Override less than comparison to compare based on truck id
    def __lt__(self, other):
        if isinstance(other, Truck):
            return self.id < other.id
        else:
            return NotImplemented

    # Override greater than comparison to compare based on truck id
    def __gt__(self, other):
        if isinstance(other, Truck):
            return self.id > other.id
        else:
            return NotImplemented

    # This function is used to populate the truck -> routes{} dictionary
    def add_route(self, route, path):
        if route not in self.routes.keys():
            self.routes[route] = path
        # It is expected that each key(route) is unique
        else:
            print("ERROR! DUPLICATE KEY", file=sys.stderr)




class Route:
    def __init__(self, start_vertex, end_vertex, departure, arrival):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.departure = departure
        self.arrival = arrival


class Truck:
    def __init__(self, id):
        self.id = id
        self.route = {}
        self.total_packages = 0
        self.current_location = None

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



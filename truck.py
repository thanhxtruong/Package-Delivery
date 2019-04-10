class Truck:
    def __init__(self, name):
        self.name = name
        self.route = []
        self.current_location = None

    def __str__(self):
        return self.name

    # Override equality comparison to compare based on truck name
    def __eq__(self, other):
        if isinstance(other, Truck):
            return self.name == other.name
        else:
            return NotImplemented

    # Override inequality comparison to compare based on truck name
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    # Override less than comparison to compare based on truck name
    def __lt__(self, other):
        if isinstance(other, Truck):
            return self.name < other.name
        else:
            return NotImplemented

    # Override greater than comparison to compare based on truck name
    def __gt__(self, other):
        if isinstance(other, Truck):
            return self.name > other.name
        else:
            return NotImplemented



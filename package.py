# Deadline class used to assign Priority based on deadline
class Deadline:
    def __init__(self, time):
        self.deadline = time
        self.priority = None

    # def __str__(self):
    #     return str(self.deadline) + " -> " + str(self.priority)

    def __eq__(self, other):
        if isinstance(other, Deadline):
            return self.deadline == other.deadline
        else:
            return NotImplemented

    # Override inequality comparison to compare based on delivery deadline
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    # Override less than comparison to compare based on delivery deadline
    def __lt__(self, other):
        if isinstance(other, Deadline):
            return self.deadline < other.deadline
        else:
            return NotImplemented

    # Override greater than comparison to compare based on delivery deadline
    def __gt__(self, other):
        if isinstance(other, Deadline):
            return self.deadline > other.deadline
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.deadline)

    def set_priority(self, priority):
        self.priority = priority


class Package:

    # Constructor for a new Package object.
    # TODO:
    #  Add a boolean for combined_pkg.
    #  Fix constructor with implementation of Truck class
    def __init__(self, pkg_id, address_id, weight):
        self.pkg_id = pkg_id
        self.address_id = address_id
        self.weight = weight

        # Initialize deadline, pickup time, required truck, and combined_pkg to None
        self.deadline = None
        self.pickup_time = None
        self.truck = None
        self.combined_pkg = []

    # Override method to print package by ID and deadline
    def __str__(self):
        # return self.pkg_id + " " + str(self.deadline.deadline)
        return self.pkg_id

    # Override equality comparison to compare based on delivery deadline
    def __eq__(self, other):
        if isinstance(other, Package):
            return self.deadline == other.deadline
        else:
            return NotImplemented

    # Override inequality comparison to compare based on delivery deadline
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    # Override less than comparison to compare based on delivery deadline
    def __lt__(self, other):
        if isinstance(other, Package):
            return self.deadline < other.deadline
        else:
            return NotImplemented

    # Override greater than comparison to compare based on delivery deadline
    def __gt__(self, other):
        if isinstance(other, Package):
            return self.deadline > other.deadline
        else:
            return NotImplemented

    def __len__(self):
        return len(self.pkg_id)

    def __iter__(self):
        return self.pkg_id

    # Set delivery deadline
    def add_delivery_deadline(self, deadline):
        self.deadline = deadline

    # Set pickup time
    def set_pickup_time(self, time):
        self.pickup_time = time

    # Set specific truck requirement
    def set_truck(self, truck):
        self.truck = truck
        # TODO: Add logic to set truck requirement for combined packages

    # Set combined packages requirement
    def set_combined_pkg(self, list):
        self.combined_pkg = list

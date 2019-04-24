from datetime import time
# Deadline class used to assign Priority based on deadline
class Deadline:
    def __init__(self, time):
        self.time = time
        self.priority = None

    # def __str__(self):
    #     return str(self.deadline) + " -> " + str(self.priority)

    def __eq__(self, other):
        if isinstance(other, Deadline):
            return self.time == other.time
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
            return self.time < other.time
        else:
            return NotImplemented

    # Override greater than comparison to compare based on delivery deadline
    def __gt__(self, other):
        if isinstance(other, Deadline):
            return self.time > other.time
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.time)

    def set_priority(self, priority):
        self.priority = priority


class Package:

    # Constructor for a new Package object.
    def __init__(self, pkg_id, address, weight):
        self.pkg_id = pkg_id
        self.address = address
        self.weight = weight

        # Initialize deadline, required truck, and combined_pkg to None
        self.deadline = None
        self.later_pickup_time = None
        self.pickup_time = None
        self.delivered_time = None
        self.truck = None
        self.combined_pkg = []
        self.status = self.add_status(0)

    def add_status(self, status_id):
        options = ('Awaiting Pickup at HUB', 'In Route', 'Delivered')
        status = list(enumerate(options))
        self.status = status[status_id][1]
        return self.status

    # Override method to print package by ID and deadline
    def __str__(self):
        return str(self.pkg_id)

    # Override equality comparison to compare based on delivery deadline
    def __eq__(self, other):
        if isinstance(other, Package):
            return self.pkg_id == other.pkg_id and self.address == other.address and self.deadline == other.deadline and self.weight == other.weight
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
            return self.pkg_id < other.pkg_id and self.address < other.address and self.deadline < other.deadline and self.weight < other.weight
        else:
            return NotImplemented

    # Override greater than comparison to compare based on delivery deadline
    def __gt__(self, other):
        if isinstance(other, Package):
            return self.pkg_id > other.pkg_id and self.address > other.address and self.deadline > other.deadline and self.weight > other.weight
        else:
            return NotImplemented

    def __len__(self):
        return len(self.pkg_id)

    def __iter__(self):
        return self.pkg_id

    def __hash__(self):
        return hash((self.pkg_id, self.address, self.deadline, self.weight))

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

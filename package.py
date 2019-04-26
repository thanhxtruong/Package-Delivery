# Deadline class used to assign Priority based on deadline time.
class Deadline:
    def __init__(self, time):
        self.time = time
        self.priority = None

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

    # This function is used to assign priority for a deadline.
    def set_priority(self, priority):
        self.priority = priority


# The Package class holds all data related to the package as downloaded from the csv file.
# The built-in methods are overridden to compare and hash using pkg_id, address, weight,
# and deadline attributes.
class Package:

    # Constructor for a new Package object.
    def __init__(self, pkg_id, address, weight):
        self.pkg_id = pkg_id
        self.address = address
        self.weight = weight

        # Delivery deadline (Time object NOT Deadline object)
        self.deadline = None
        # Pre-set pickup time per user's requirement (Time object NOT Deadline object)
        self.later_pickup_time = None
        # Calculated Time at which the package will be picked up by the carrier truck
        self.pickup_time = None
        # Calculated Time at which the package will be delivered.
        self.delivered_time = None
        # Carrier truck delivering the package.
        self.truck = None
        # List of all packages that must be delivered with this package per user's
        # requirement.
        self.combined_pkg = []
        # The current status of the package.
        self.status = self.add_status(0)

    # This function assign a status for the Package object,
    def add_status(self, status_id):
        options = ('Awaiting Pickup at HUB', 'In Route', 'Delivered')
        # status is a tuple of actual option and enumerated int value.
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

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __lt__(self, other):
        if isinstance(other, Package):
            return self.pkg_id < other.pkg_id and self.address < other.address and self.deadline < other.deadline and self.weight < other.weight
        else:
            return NotImplemented

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

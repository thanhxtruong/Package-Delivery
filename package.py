class Package:

    # Constructor for a new Package object.
    # TODO:
    #  Add a boolean for combined_pkg.
    #  Fix constructor with implementation of Truck class
    def __init__(self, pkg_id, address, weight):
        self.pkg_id = pkg_id
        self.address = address
        self.weight = weight

        # Initialize deadline, pickup time, required truck, and combined_pkg to None
        self.deadline = None
        self.pickup_time = None
        self.truck = None
        self.combined_pkg = []

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

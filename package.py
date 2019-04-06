class Package:

    # Constructor for a new Package object.
    def __init__(self, pkg_id, address, city, zip_code, state, weight):
        self.pkg_id = pkg_id
        self.address = address
        self.city = city
        self.zipCode = zip_code
        self.state = state
        self.weight = weight

        # Initialize deadline, pickup time, and required truck to None
        self.deadline = None
        self.pickup_time = None
        self.truck = None

    # Set delivery deadline
    def add_delivery_deadline(self, deadline):
        self.deadline = deadline

    # Set pickup time
    def set_pickup_time(self, time):
        self.pickup_time = time

    # Set specific truck requirement
    def set_truck(self, truck):
        self.truck = truck

class Truck:
    def __init__(self, name):
        self.name = name
        self.route = []
        self.current_location = None

    def __str__(self):
        return self.name


class Truck:
    def __init__(self, name):
        self.name = name
        self.route = []
        self.current_location = None

    def __str__(self):
        return self.name

    def set_start_location(self, vertex):
        self.current_location = vertex

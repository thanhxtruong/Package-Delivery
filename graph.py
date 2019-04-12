class Vertex:
    def __init__(self, data):
        self.data = data
        self.pred_vertex = None
        distance = float('inf')                 # shortest path distance from start_vertex
        self.trucks = []                        # all trucks currently at this vertex
        # TODO: Add pred

    # def __str__(self):
    #     return self.address.address1

    def add_truck(self, truck_id):
        self.trucks.append(truck_id)

    def search_truck(self, truck_id):
        for truck_iter in self.trucks:
            if truck_iter == truck_id:
                return self
            else:
                return None


class Graph:
    def __init__(self):
        self.adjacency_list = {}
        self.edge_weights = {}

    def add_truck_to_hub(self, truck):
        i = 0
        for vertex in self.adjacency_list.keys():
            if i == 0:
                vertex.add_truck(truck.id)
                truck.current_location = vertex
                return

    def add_vertex(self, new_vertex, adj_list):
        self.adjacency_list[new_vertex] = adj_list

    def add_directed_edge(self, from_vertex, to_vertex, weight=1):
        self.edge_weights[(from_vertex, to_vertex)] = weight

    def add_undirected_edge(self, vertex_a, vertex_b, weight=1):
        self.add_directed_edge(vertex_a, vertex_b, weight)
        self.add_directed_edge(vertex_b, vertex_a, weight)

    def find_truck(self, truck):
        for vertex in self.adjacency_list.keys():
            if truck in vertex.trucks:
                print("Truck is currently at")
                print(vertex.address.address1)

    def get_vertex(self, address_id):
        for vertex in self.adjacency_list.keys():
            if vertex.address == address_id:
                return vertex

    # TODO Verify this function work
    def dijkstra_shortest_path(g, start_vertex):
        # Put all vertices in an unvisited queue.
        unvisited_queue = []
        for current_vertex in g.adjacency_list:
            unvisited_queue.append(current_vertex)

        # Start_vertex has a distance of 0 from itself
        start_vertex.distance = 0

        # One vertex is removed with each iteration; repeat until the list is
        # empty.
        while len(unvisited_queue) > 0:

            # Visit vertex with minimum distance from start_vertex
            smallest_index = 0
            for i in range(1, len(unvisited_queue)):
                if unvisited_queue[i].distance < unvisited_queue[smallest_index].distance:
                    smallest_index = i
            current_vertex = unvisited_queue.pop(smallest_index)

            # Check potential path lengths from the current vertex to all neighbors.
            for adj_vertex in g.adjacency_list[current_vertex]:
                edge_weight = g.edge_weights[(current_vertex, adj_vertex)]
                alternative_path_distance = current_vertex.distance + edge_weight

                # If shorter path from start_vertex to adj_vertex is found,
                # update adj_vertex's distance and predecessor
                if alternative_path_distance < adj_vertex.distance:
                    adj_vertex.distance = alternative_path_distance
                    adj_vertex.pred_vertex = current_vertex

    # TODO: Verify this function work
    def get_shortest_path(start_vertex, end_vertex):
        # Start from end_vertex and build the path backwards.
        path = ""
        current_vertex = end_vertex
        while current_vertex is not start_vertex:
            path = " -> " + str(current_vertex.label) + path
            current_vertex = current_vertex.pred_vertex
        path = start_vertex.label + path
        return path

    def print_graph(self):
        for vertex, adj_list in self.adjacency_list.items():
            print(vertex.data)
        print("===========================================")
        for vertex_tuple, weight in self.edge_weights.items():
            i += 1
            for vertex in vertex_tuple:
                print(vertex.data, end='')
                print(" --> ", end='')
            print(weight)

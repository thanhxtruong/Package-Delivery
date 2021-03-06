# The Vertex class represents each node of the Graph class
class Vertex:
    def __init__(self, address_id):
        self.address_id = address_id
        self.pred_vertex = None
        # Shortest path distance from start_vertex
        self.distance = float('inf')


# The Graph class holds a vertex adjacency list using a dictionary that maps each Vertex
# on the Graph to a list of adjacent Vertex objects. Distances between vertices are also
# stored.
class Graph:
    def __init__(self):
        self.adjacency_list = {}
        self.edge_weights = {}

    def add_vertex(self, new_vertex):
        self.adjacency_list[new_vertex] = []

    def add_directed_edge(self, from_vertex, to_vertex, weight=1):
        self.edge_weights[(from_vertex, to_vertex)] = weight
        self.adjacency_list[from_vertex].append(to_vertex)

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
            if vertex.address_id == address_id:
                return vertex

    def dijkstra_shortest_path(self, start_vertex):
        # Put all vertices in an unvisited queue.
        unvisited_queue = []
        for current_vertex in self.adjacency_list:
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
            for adj_vertex in self.adjacency_list[current_vertex]:
                edge_weight = self.edge_weights[(current_vertex, adj_vertex)]
                alternative_path_distance = current_vertex.distance + edge_weight

                # If shorter path from start_vertex to adj_vertex is found,
                # update adj_vertex's distance and predecessor
                if alternative_path_distance < adj_vertex.distance:
                    adj_vertex.distance = alternative_path_distance
                    adj_vertex.pred_vertex = current_vertex

    def get_shortest_path(self, start_vertex, end_vertex):
        self.dijkstra_shortest_path(start_vertex)
        # Start from end_vertex and build the path backwards.
        # [(Address, [Packages]), (Address, [Packages])]
        path = []
        current_vertex = end_vertex
        while current_vertex is not start_vertex:
            path.insert(0, (current_vertex.address_id, current_vertex.distance, []))
            current_vertex = current_vertex.pred_vertex
        path.insert(0, (start_vertex.address_id, start_vertex.distance, []))
        return path

    def print_shortest_path(self, start_vertex, end_vertex):
        # Start from end_vertex and build the path backwards.
        path = ""
        current_vertex = end_vertex
        while current_vertex is not start_vertex:
            path = " -> " + str(current_vertex.address_id) + path
            current_vertex = current_vertex.pred_vertex
        path = str(start_vertex.address_id) + path
        return path

    def print_graph(self):
        for vertex, adj_list in self.adjacency_list.items():
            print(vertex.address_id)
        print("===========================================")
        for vertex_tuple, weight in self.edge_weights.items():
            for vertex in vertex_tuple:
                print(vertex.address_id, end='')
                print(" --> ", end='')
            print(weight)

    # This function reset all distances in adjacency_list back to inf.
    # This function should be called after each call of
    def reset_adjacency_list(self):
        for vertex in self.adjacency_list.keys():
            vertex.distance = float('inf')

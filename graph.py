class Vertex:
    def __init__(self, address):
        self.address = address
        self.visited = False


class Graph:
    def __init__(self):
        self.adjacency_list = {}
        self.edge_weights = {}

    def add_vertex(self, new_vertex, adj_list):
        self.adjacency_list[new_vertex] = adj_list

    def add_directed_edge(self, from_vertex, to_vertex, weight=1):
        self.edge_weights[(from_vertex, to_vertex)] = weight

    def add_undirected_edge(self, vertex_a, vertex_b, weight=1):
        self.add_directed_edge(vertex_a, vertex_b, weight)
        self.add_directed_edge(vertex_b, vertex_a, weight)

    def print_graph(self):
        for vertex, list in self.adjacency_list.items():
            print(vertex.address.address1, list)
        print("===========================================")
        i = 0
        for vertex_tuple, weight in self.edge_weights.items():
            i += 1
            for vertex in vertex_tuple:
                print(vertex.address.address1, end='')
                print(" --> ", end='')
            print(weight)
        print(i)
# Name: Thanh Truong. StudentID: #001062385

import csv
from datetime import time
from package import Package
from address import Address
from graph import Vertex, Graph
from truck import Truck


def load_pkg_data(filename):
    # Open file, read package data one line at a time skipping the first row (header).
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile)
        # Skip the header
        next(readCSV)
        for row in readCSV:
            # print(row)
            # Create an address obj
            address = Address(row[1], row[2], row[3], row[4])
            package = Package(row[0], address, row[5])
            # Set delivery deadline
            if not (row[6] == 'EOD'):
                split_time = row[6].split(':')
                hour = int(split_time[0])
                # Split string again to remove 'AM'/'PM'
                minute = int(split_time[1].split(' ')[0])
                deadline = time(hour, minute, 0)
                package.add_delivery_deadline(deadline)

            # Set pickup time
            if not (row[7] == ''):
                split_time = row[7].split(':')
                hour = int(split_time[0])
                # Split string again to remove 'AM'/'PM'
                minute = int(split_time[1].split(' ')[0])
                pickup_time = time(hour, minute, 0)
                package.set_pickup_time(pickup_time)
                # TODO: Save all packages with pickup_time into the pickup_list

            # Set specific truck requirement
            if not (row[8] == ''):
                package.set_truck(row[8])

            # Set combined packages requirement
            # TODO: Change combined_pkg_list to a set implementation
            combined_pkg_list = []
            if not (row[9] == ''):
                split_list = row[9].split(',')
                for item in split_list:
                    combined_pkg_list.append(item)
                package.set_combined_pkg(combined_pkg_list)

    # TODO:
    #  Add each package to a list.
    #  Iterate through the list and set truck requirement using combined_pkg_set.
    #  Return the pkg_list.
    return []

def create_dest_priority(pkg_list):

    # TODO: Dump data for packages into a LinkedList with each Node holding an address and data including a list of all packages that need to deliver to that address
    # TODO:
    #  Sort data into a priority queue using MinHeap.
    #  Packages with combined_pkg set to True will have the same Priority#

    return[]


def load_graph(filename):
    vertex_list = []
    graph = Graph()

    # Open file, read package data one line at a time skipping the first row (header).
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile)
        # Skip the header
        next(readCSV)
        for row in readCSV:
            # print(row)
            # Get the address (first element) then split it by ','.
            # The result is another array of address data
            split_address = row[0].split(',')
            address1 = split_address[0]
            city = split_address[1]
            zip_code = split_address[2]
            state = split_address[3]
            address = Address(address1, city, zip_code, state)
            vertex = Vertex(address)
            vertex_list.append(vertex)

            # Extract distance data from the input string and save into a list
            i = 1
            dist_list = []
            while not float(row[i]) == 0:
                dist_list.append(row[i])
                i += 1

            # Add vertex to graph.
            # Save distances into the adjacency list for the new vertex
            graph.add_vertex(vertex, dist_list)

            # Add undirected edges to graph
            for vertex, list in graph.adjacency_list.items():
                address_list_index = 0
                for distance in list:
                    graph.add_undirected_edge(vertex, vertex_list[address_list_index], distance)
                    address_list_index += 1

            # graph.print_graph()
    return graph


# TODO: Implement pseudocode
def assign_truck (destination):
    # for package in destination -> pkg_list
    # if (package -> truck is not None)
    #     for truck in trucks
    #         if (truck = package -> truck)
    #             return truck
    # else
    #     for truck in trucks
    #         if (MAX_PKG - len(truck -> route)) >= len(temp_list)
            return None


if __name__ == "__main__":
    trucks = []
    #TODO: create a Truck class that includes name, current_location, and route[] for each truck

    # Load data for packages and save them into a priority queue.
    # Priority is assigned based on deadline.
    # Packages with combined packages constraint have the same Priority #
    pkg_filename = input("Enter name of package data file: ")
    pkg_list = load_pkg_data(pkg_filename)
    dest_priority_queue = create_dest_priority(pkg_list)

    # Load data from distance table and save them into an undirected graph
    dist_filename = input("Enter name of distance data file: ")
    graph = load_graph(dist_filename)

    # Create trucks and add to HUB location in graph
    i = 1
    while i < 4:
        truck = Truck('Truck ' + str(i))
        graph.add_truck_to_hub(truck)
        i += 1

    # while (length of dest_priority_queue is >= 0)
    #     pkgs_to_deliver = []
    #     temp_list = []
    #     ready = False
    #
    #     destination = Pop dest_priority_queue
    #     truck = assign_truck(current_destination)
    #
    #     route = graph.get_shortest_path(truck -> current_location, destination)
    #     Add route to truck -> route







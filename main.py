# Name: Thanh Truong. StudentID: #001062385

import csv
from datetime import time
from package import Package
from address import Address
from graph import Vertex, Graph


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

            # Set specific truck requirement
            if not (row[8] == ''):
                package.set_truck(row[8])


def load_graph(filename):
    vertex_list = []
    graph = Graph()

    # Open file, read package data one line at a time skipping the first row (header).
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile)
        # Skip the header
        next(readCSV)
        for row in readCSV:
            print(row)
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

            graph.print_graph()


if __name__ == "__main__":
    pkg_filename = input("Enter name of package data file: ")
    load_pkg_data(pkg_filename)
    dist_filename = input("Enter name of distance data file: ")
    load_graph(dist_filename)

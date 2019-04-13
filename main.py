# Name: Thanh Truong. StudentID: #001062385

import csv

from datetime import time
from queue import PriorityQueue
from package import Package, Deadline
from address import Address
from graph import Vertex, Graph
from truck import Truck

# Dictionary to hold (address/address_id) pairs
address_dict = {}
# Dictionary to hold (address_id/[packages]) pairs
pkg_dict = {}
# Set of delivery deadlines used to set Priority
deadline_set = set()
# Priority queue organized by address_id and priority
dest_priority_queue = PriorityQueue()
# List of all graph with vertices representing packages that are to be delivered together in the same route
same_route_set_list = []
# List of all vertices in graph
vertex_list = []
graph = Graph()


def load_graph(filename):

    # Open file, read package data one line at a time skipping the first row (header).
    with open(filename) as csvfile:
        index = 1  # Index for address_dict key/value pair
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
            # Add address to address_dict
            address_dict[address] = index
            index += 1

            _vertex = Vertex(address)
            vertex_list.append(_vertex)

            # Extract distance data from the input string and save into a list
            j = 1
            dist_list = []
            while not float(row[j]) == 0:
                dist_list.append(row[j])
                j += 1

            # Add vertex to graph.
            # Save distances into the adjacency list for the new vertex
            graph.add_vertex(_vertex, dist_list)

            # Add undirected edges to graph
            for _vertex, adj_list in graph.adjacency_list.items():
                address_list_index = 0
                for distance in adj_list:
                    graph.add_undirected_edge(_vertex, vertex_list[address_list_index], distance)
                    address_list_index += 1

            # graph.print_graph()
    return graph


# This function iterates through the address_dict{} and returns the address_id (key) for a given set of string values
# for (state, zipCode, city, address1)
def get_address_from_address_dict(address1, city, zipCode, state):
    for address_obj, address_id in address_dict.items():
        address = address_obj
        if address.compare_address(address1, city, zipCode, state):
            return address_id, address_obj


def load_pkg_data(filename):
    # Open file, read package data one line at a time skipping the first row (header).
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile)
        # Skip the header
        next(readCSV)

        for row in readCSV:
            # print(row)

            # Get address_id from address_dict{}
            address_tuple = get_address_from_address_dict(row[1], row[2], row[3], row[4])
            _address_id = address_tuple[0]

            # Create package obj
            package = Package(row[0], _address_id, row[5])

            # Set delivery deadline
            # Deadline is hardcoded to 23:00:00 if set to 'EOD'

            if row[6] == 'EOD':
                deadline = Deadline(time(23, 0, 0))

            else:
                split_time = row[6].split(':')
                hour = int(split_time[0])
                # Split string again to remove 'AM'/'PM'
                minute = int(split_time[1].split(' ')[0])
                deadline = Deadline(time(hour, minute, 0))

            # Add each unique deadline to the deadline_set and package
            package.add_delivery_deadline(deadline)
            deadline_set.add(deadline)

            # Set specific truck requirement
            if not (row[8] == ''):
                package.set_truck(int(row[8]))

            # Set combined packages requirement
            if not (row[9] == ''):
                same_route_set = set()
                same_route_set.add(int(package.pkg_id))
                split_list = row[9].split(',')
                for item in split_list:
                    same_route_set.add(int(item))

                same_route_set_list.append(same_route_set)

        print("Printing sets prior to union")
        for package_set in same_route_set_list:
            print(package_set)

        same_route_combined_sets = []
        while len(same_route_set_list) > 0:
            sets_to_remove = []
            for index in range(len(same_route_set_list)):
                if index == 0:
                    first_set = same_route_set_list[index]
                    sets_to_remove.append(same_route_set_list[index])
                else:
                    if len(first_set.intersection(same_route_set_list[index])) > 0:
                        sets_to_remove.append(same_route_set_list[index])

            combined_set = set()
            for index1 in range(len(sets_to_remove)):
                combined_set = combined_set.union(same_route_set_list[index1])
            same_route_combined_sets.append(combined_set)
            for index1 in range(len(sets_to_remove)):
                same_route_set_list.remove(sets_to_remove[index1])



            # Add package to dictionary
            # if package.address_id not in pkg_dict.keys():
            #     pkg_dict[package.address_id] = [package]
            # else:
            #     pkg_list = pkg_dict.get(package.address_id)
            #     pkg_list.append(package)

    # Print address and corresponding address_id
    # for key in address_dict.keys():
    #     print(key.address1 + ' -> ', end='')
    #     print(address_dict.get(key))
    #     print("==============================")

    # print("Printing set")
    # for item in deadline_set:
    #     print(item)

    # Print pkg_dict
    for key in pkg_dict.keys():
        print("address_id key: " + str(key))
        package_list = pkg_dict.get(key)
        for package in package_list:
            print("Package: ", end='')
            print(package)
        print("===============================================")
    print('')
    print("End of pkg_dict")
    print("*****************************************************")

    # TODO:
    #  Add each package to a list.
    #  Iterate through the list and set truck requirement using combined_pkg_set.
    #  Return the pkg_list.
    return pkg_dict


def create_dest_priority(pkg_dict):
    # TODO: Dump data for packages into a LinkedList with each Node holding an address and data including a list of all packages that need to deliver to that address
    # TODO:
    #  Sort data into a priority queue using MinHeap.
    #  Packages with combined_pkg set to True will have the same Priority#

    # print("Printing set prior to sorting")
    # for deadline in deadline_set:
    #     print(deadline.deadline)

    # Iterate through the set of all deadlines and assign priority
    sorted_deadline_set = sorted(deadline_set)
    priority = 1
    print("Printing priority")
    for deadline in sorted_deadline_set:
        print(deadline.deadline)
        deadline.priority = priority
        print("Priority: " + str(priority))
        print("==============================================")
        priority += 1
    print("End of printing priority")

    # TODO: Change to sorted() method
    # Iterate through pkg_dict (address_id/[packages]).
    # For each list of packages, sort the list to find the earliest deadline.
    # Assign priority
    for key in pkg_dict.keys():

        package_list = pkg_dict.get(key)
        if len(package_list) > 1:
            selection_sort(package_list)

        index = 0
        for package in package_list:
            if index == 0:
                earliest_package = package.deadline
            index += 1

        for deadline in deadline_set:
            if deadline == earliest_package:
                priority = deadline.priority

        dest_priority_queue.put((priority, package.address_id))

    # print("Printing destination priority queue")
    # while not dest_priority_queue.empty():
    #     next_item = dest_priority_queue.get()
    #     print(next_item)

    return []


# Merge sort algorithm
def merge(numbers, i, j, k):
    merged_size = k - i + 1  # Size of merged partition
    merged_numbers = [0] * merged_size  # Dynamically allocates temporary array
    # for merged numbers
    merge_pos = 0  # Position to insert merged number
    left_pos = i  # Initialize left partition position
    right_pos = j + 1  # Initialize right partition position

    # Add smallest element from left or right partition to merged numbers
    while left_pos <= j and right_pos <= k:
        if numbers[left_pos] < numbers[right_pos] or numbers[left_pos] == numbers[right_pos]:
            merged_numbers[merge_pos] = numbers[left_pos]
            left_pos += 1
        else:
            merged_numbers[merge_pos] = numbers[right_pos]
            right_pos += 1
        merge_pos = merge_pos + 1

    # If left partition is not empty, add remaining elements to merged numbers
    while left_pos <= j:
        merged_numbers[merge_pos] = numbers[left_pos]
        left_pos += 1
        merge_pos += 1

    # If right partition is not empty, add remaining elements to merged numbers
    while right_pos <= k:
        merged_numbers[merge_pos] = numbers[right_pos]
        right_pos = right_pos + 1
        merge_pos = merge_pos + 1

    # Copy merge number back to numbers
    for merge_pos in range(merged_size):
        numbers[i + merge_pos] = merged_numbers[merge_pos]


# Merge sort
# numbers: list
# i: first index
# k: last index
def merge_sort(numbers, i, k):
    j = 0

    if i < k:
        j = (i + k) // 2  # Find the midpoint in the partition

        # Recursively sort left and right partitions
        merge_sort(numbers, i, j)
        merge_sort(numbers, j + 1, k)

        # Merge left and right partition in sorted order
        merge(numbers, i, j, k)


def selection_sort(numbers):
    # A variable to hold the number of item comparisons
    comparisons = 0

    for i in range(len(numbers) - 1):

        # Find index of smallest remaining element
        index_smallest = i
        for j in range(i + 1, len(numbers)):

            comparisons = comparisons + 1
            if numbers[j] < numbers[index_smallest]:
                index_smallest = j

        # Swap numbers[i] and numbers[index_smallest]
        temp = numbers[i]
        numbers[i] = numbers[index_smallest]
        numbers[index_smallest] = temp

    return comparisons


if __name__ == "__main__":
    # TODO: Modify sorted() using attrgetter (dijkstra)
    trucks = []

    # Load data from distance table and save them into an undirected graph
    dist_filename = input("Enter name of distance data file: ")
    graph = load_graph(dist_filename)

    # Create trucks and add to HUB location in graph
    i = 1
    while i < 4:
        truck = Truck(i)
        trucks.append(truck)
        graph.add_truck_to_hub(truck)
        i += 1

    # print("Printing truck location")
    # graph.find_truck(1)
    # graph.find_truck(2)
    # graph.find_truck(3)

    # Load data for packages and save them into a priority queue.
    # Priority is assigned based on deadline.
    # Packages with combined packages constraint have the same Priority #
    pkg_filename = input("Enter name of package data file: ")
    load_pkg_data(pkg_filename)
    create_dest_priority(pkg_dict)

    while not dest_priority_queue.empty():
        required_truck = None
        # List of all destinations to be routed in sequence
        # in the case of packages that are required to be delivered together
        dest_list = []
        # Pop the next item from queue
        next_dest = dest_priority_queue.get()
        # Append it to the list
        dest_list.append(next_dest[1])
        # print("Destination: " + str(next_dest[1]))
        # Get the list of all packages that are required to be delivered
        # to this next destination.
        same_dest_pkg_list = pkg_dict.get(next_dest[1])

        # For each package in the same_dest_pkg_list, get the list of packages
        # that are required to be delivered together (if any) using the same route.
        # For each package in this "same_route" list, iterate through the package
        # dictionary and get the list of all packages for the corresponding
        # destination from the dictionary.
        # Finally, for each package inside this list from dict, return the key
        # (destination) once the package_id matches that from the
        # same_route_pkg_list.
        for package in same_dest_pkg_list:
            # Set required_truck for package if any
            if required_truck is None:
                required_truck = package.truck
            if len(package.combined_pkg) > 1:
                same_route_pkg_list = package.combined_pkg
                for same_route_index in same_route_pkg_list:
                    for key in pkg_dict.keys():
                        pkg_list_from_dict = pkg_dict.get(key)

                        # Iterate through each list of packages from the dictionary to find the matching package_id
                        # and return te corresponding address_id (key)
                        for i in range(len(pkg_list_from_dict)):
                            package = pkg_list_from_dict[i]
                            if int(package.pkg_id) == same_route_index:
                                # Add the next destination to the list
                                dest_list.append(key)
                                # Set required_truck for package if any
                                if required_truck is None:
                                    required_truck = package.truck

        print("At the end, these are all destination that needs to be delivered in sequence")
        for destination in dest_list:
            print(destination)
        print("=========================================")

        # TODO: Change this algorithm. Currently hard-coded to Truck 1 for testing
        for truck in trucks:
            if required_truck is None:
                selected_truck = trucks[0]
                break
            else:
                if truck.name == required_truck:
                    selected_truck = truck
                    break

        # Start here
        for address_id in dest_list:
            vertex = graph.get_vertex(address_id)
        # truck_location = trucks[0].current_location
        # print(truck_location)
        # truck_location = graph.find_truck(required_truck)

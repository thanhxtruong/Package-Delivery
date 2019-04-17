# Name: Thanh Truong. StudentID: #001062385

import csv
import sys
from inspect import currentframe, getframeinfo
from datetime import datetime, time, timedelta, date
from queue import PriorityQueue
from package import Package, Deadline
from address import Address
from graph import Vertex, Graph
from truck import Truck, Route

# Dictionary to hold (address/address_id) pairs
address_dict = {}
# Dictionary to hold (address_id/[packages]) pairs
pkg_dict = {}
# Set of delivery deadlines used to set Priority
deadline_set = set()
# Priority queue organized by address_id and priority
dest_priority_queue = PriorityQueue()
# List of all graph with vertices representing packages that are to be delivered together in the same route
same_route_combined_sets = []
# List of all vertices in graph
vertex_list = []
graph = Graph()
# Dictionary of packages that require pick-up later
pickup_packages = {}

MAX_PKG_PER_TRUCK = 16
SPEED = 18


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

            _vertex = Vertex(index)
            vertex_list.append(_vertex)

            # Extract distance data from the input string and save into a list
            j = 1
            dist_list = []
            while not float(row[j]) == 0:
                dist_list.append(float(row[j]))
                j += 1

            # Add vertex to graph.
            # Save distances into the adjacency list for the new vertex
            graph.add_vertex(_vertex)

            # Add undirected edges to graph
            address_list_index = 0
            for travel_distance in dist_list:
                graph.add_undirected_edge(_vertex, vertex_list[address_list_index], travel_distance)
                address_list_index += 1
            # for _vertex, adj_list in graph.adjacency_list.items():
            #     address_list_index = 0
            #     for travel_distance in dist_list:
            #         graph.add_undirected_edge(_vertex, vertex_list[address_list_index], travel_distance)
            #         address_list_index += 1

            index += 1

            # graph.print_graph()
    return graph


# This function iterates through the address_dict{} and returns the address_id (key) for a given set of string values
# for (state, zipCode, city, address1)
def get_address_from_address_dict(address1, city, zipCode, state):
    for address_obj, address_id in address_dict.items():
        address = address_obj
        if address.compare_address(address1, city, zipCode, state):
            return address_id, address_obj


# This function return address_id for a given pkg_id in the pkg_dict{}
def get_address_from_pkg_dict(pkg_id):
    for address_id, pkg_list in pkg_dict.items():
        for package in pkg_list:
            if package.pkg_id == pkg_id:
                return address_id


def load_pkg_data(filename):
    same_route_set_list = []
    # Open file, read package data one line at a time skipping the first row (header).
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile)
        # Skip the header
        next(readCSV)

        for row in readCSV:
            # print(row)

            # Get address_id from address_dict{}
            address_tuple = get_address_from_address_dict(row[1], row[2], row[3], row[4])
            hub_address_id = address_tuple[0]

            # Create package obj
            package = Package(int(row[0]), hub_address_id, float(row[5]))

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
                temp_set = set()
                temp_set.add(int(package.pkg_id))
                split_list = row[9].split(',')
                for item in split_list:
                    temp_set.add(int(item))

                same_route_set_list.append(temp_set)

            # Add route back to HUB if package has a pickup_time
            if not (row[7] == ''):
                # Set address_id to HUB
                hub_address_id = 1
                # Create a new deadline using pickup_time
                split_time = row[7].split(':')
                hour = int(split_time[0])
                # Split string again to remove 'AM'/'PM'
                minute = int(split_time[1].split(' ')[0])
                deadline = Deadline(time(hour, minute, 0))
                # Add deadline to deadline_set
                deadline_set.add(deadline)
                # Create a new package obj
                pickup_package = Package(int(row[0]), hub_address_id, float(row[5]))
                pickup_package.add_delivery_deadline(deadline)
                # Add pickup_package to dictionary
                if pickup_package.address_id not in pkg_dict.keys():
                    pkg_dict[pickup_package.address_id] = [pickup_package]
                else:
                    pkg_list1 = pkg_dict.get(pickup_package.address_id)
                    pkg_list1.append(pickup_package)

                # Add delivery package to pickup_packages{}
                if package.address_id not in pickup_packages.keys():
                    pickup_packages[package.address_id] = [package]
                else:
                    pkg_list2 = pickup_packages.get(package.address_id)
                    pkg_list2.append(package)

            else:
                # Add package to dictionary
                if package.address_id not in pkg_dict.keys():
                    pkg_dict[package.address_id] = [package]
                else:
                    pkg_list3 = pkg_dict.get(package.address_id)
                    pkg_list3.append(package)

    # Go through list of same_route_sets to combine sets
    combined_set_list = []
    while len(same_route_set_list) > 0:
        sets_to_remove = []

        first_set = None
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
        combined_set_list.append(combined_set)
        for index1 in range(len(sets_to_remove)):
            same_route_set_list.remove(sets_to_remove[index1])

    # Replace package_id with address_id

    for combined_set in combined_set_list:
        replaced_set = set()
        for pkg_id in combined_set:
            address_id = get_address_from_pkg_dict(pkg_id)
            replaced_set.add(address_id)
        same_route_combined_sets.append(replaced_set)



    # Print address and corresponding address_id
    # for key in address_dict.keys():
    #     print(key.address1 + ' -> ', end='')
    #     print(address_dict.get(key))
    #     print("==============================")

    # print("Printing set")
    # for item in deadline_set:
    #     print(item)

    # print("Printing pkg_dict{}")
    # for key in pkg_dict.keys():
    #     print("address_id key: " + str(key))
    #     package_list = pkg_dict.get(key)
    #     for package in package_list:
    #         print("Package: ", end='')
    #         print(package)
    #     print("===============================================")
    # print('')
    # print("End of pkg_dict")
    # print("*****************************************************")
    return pkg_dict


def prioritize_pkg_dict():

    # print("Printing set prior to sorting")
    # for deadline in deadline_set:
    #     print(deadline.deadline)

    # Iterate through the set of all deadlines and assign priority
    sorted_deadline_set = sorted(deadline_set)
    priority = 1

    # frameinfo = getframeinfo(currentframe())
    # print(frameinfo.filename, frameinfo.lineno, file=sys.stderr)
    # print("Printing priority", file=sys.stderr)
    for deadline in sorted_deadline_set:
        # print(deadline.deadline, file=sys.stderr)
        deadline.priority = priority
        # print("Priority: " + str(priority), file=sys.stderr)
        # print("==============================================", file=sys.stderr)
        priority += 1
    # print("End of printing priority", file=sys.stderr)

    # TODO: Change to sorted() method
    # Iterate through pkg_dict (address_id/[packages]).
    # For each list of packages, sort the list to find the earliest deadline.
    # Assign priority
    for key in pkg_dict.keys():

        package_list = pkg_dict.get(key)
        if len(package_list) > 1:
            selection_sort(package_list)

        if key == 1:
            earliest_package = package_list[len(package_list) - 1].deadline
        else:
            earliest_package = package_list[0].deadline

        for deadline in deadline_set:
            if deadline == earliest_package:
                priority = deadline.priority

        dest_priority_queue.put((priority, key))

    # print("Printing destination priority queue", file=sys.stderr)
    # while not dest_priority_queue.empty():
    #     next_item = dest_priority_queue.get()
    #     print(next_item, file=sys.stderr)

    return dest_priority_queue


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


# This function prints loading of packages onto Truck
def print_pkg_loading(package_list, required_truck, address_id, arrival):
    print("Loading package(s): ", end='')
    for pkg in package_list:
        print(pkg.pkg_id, end=' ')
    print("to Truck " + str(required_truck.id))
    print("\tPackage(s) will be delivered to Destination #" + str(address_id), end='')
    print(" at " + str(arrival))
    print('')


# This function prints packages picked up at HUB
def print_pkg_pickup(package_list, required_truck, arrival):
    print("Picking package(s) at HUB. Package(s) #: ", end='')
    for pkg in package_list:
        print(pkg.pkg_id, end=' ')
    print("loaded to Truck " + str(required_truck.id))
    print("\tPackage(s) will be picked up to at " + str(arrival))
    print('')


if __name__ == "__main__":
    # TODO: Modify sorted() using attrgetter (dijkstra)
    trucks = []

    # Load data from distance table and save them into an undirected graph
    # dist_filename = input("Enter name of distance data file: ")
    dist_filename = "distance_table.csv"
    graph = load_graph(dist_filename)

    # frameinfo = getframeinfo(currentframe())
    # print(frameinfo.filename, frameinfo.lineno, file=sys.stderr)
    # print("Printing shortest path for testing...", file=sys.stderr)
    # start_v = 7
    # graph.dijkstra_shortest_path(graph.get_vertex(start_v))
    # for v in graph.adjacency_list:
    #     print("Vertex %d to %s: %s (total distance: %3.2f)" % (start_v, v.address_id, graph.print_shortest_path(graph.get_vertex(start_v), v), v.distance))
    #
    # for vertex in vertex_list:
    #     vertex.distance = float('inf')
    #
    # print(frameinfo.filename, frameinfo.lineno, file=sys.stderr)
    # print("Printing shortest path for testing...", file=sys.stderr)
    # start_v = 14
    # graph.dijkstra_shortest_path(graph.get_vertex(start_v))
    # for v in graph.adjacency_list:
    #     print("Vertex %d to %s: %s (total distance: %3.2f)" % (start_v, v.address_id, graph.print_shortest_path(graph.get_vertex(start_v), v), v.distance))
    #
    # for vertex in vertex_list:
    #     vertex.distance = float('inf')
    #
    # print(frameinfo.filename, frameinfo.lineno, file=sys.stderr)
    # print("Printing shortest path for testing...", file=sys.stderr)
    # start_v = 16
    # graph.dijkstra_shortest_path(graph.get_vertex(start_v))
    # for v in graph.adjacency_list:
    #     print("Vertex %d to %s: %s (total distance: %3.2f)" % (start_v, v.address_id, graph.print_shortest_path(graph.get_vertex(start_v), v), v.distance))

    # Create trucks and add to HUB location in graph
    i = 1
    while i < 4:
        truck = Truck(i)
        # Add driver to truck
        if i < 3:
            truck.has_driver = True
            truck.departure = time(8, 0, 0)
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
    # pkg_filename = input("Enter name of package data file: ")
    pkg_filename = "package_data.csv"
    load_pkg_data(pkg_filename)
    prioritize_pkg_dict()

    # Update truck's availability based on package-truck constraint
    for address_id in pkg_dict.keys():
        pkg_list = pkg_dict.get(address_id)
        for package in pkg_list:
            for truck in trucks:
                if truck.id == package.truck:
                    truck.reserved_pkg.append(package.pkg_id)
                    truck.total_packages += 1

    # Total packages per routes in dest_in_route[]
    from_vertex = graph.get_vertex(1)
    finished = False
    previous_truck = None

    while not dest_priority_queue.empty():
        total_packages = 0
        required_truck_id = None
        required_truck = None
        dest_in_route = []

        next_address_id = dest_priority_queue.get()

        while next_address_id[1] not in pkg_dict.keys():
            if not dest_priority_queue.empty():
                next_address_id = dest_priority_queue.get()
            else:
                finished = True
                break

        if not finished:

            if next_address_id[1] == 1:
                pickup_package_list = pkg_dict.get(next_address_id[1])
                latest_pickup_time = pickup_package_list[len(pickup_package_list) - 1].deadline.time

                # if departure time for either truck 1 or truck 2 is less than pick_up time
                # continue loading other packages first
                # else if both trucks are ready for pick-up
                # select the truck with the less number of packages
                to_vertex = graph.get_vertex(next_address_id[1])
                available_trucks = []
                ready_for_pickup = False
                for truck in trucks:
                    if truck.has_driver:
                        # Calculate arrival time at HUB if departed from current location now
                        path = graph.get_shortest_path(truck.current_location, to_vertex)
                        distance = to_vertex.distance
                        dt = datetime.combine(date.today(), truck.departure) + timedelta(
                            minutes=int(distance / SPEED * 60))
                        arrival = dt.time()
                        if truck.has_driver and arrival < latest_pickup_time:
                            ready_for_pickup = False
                            hold_address_tuple = next_address_id
                            next_address_id = dest_priority_queue.get()

                            while next_address_id[1] not in pkg_dict.keys():
                                if not dest_priority_queue.empty():
                                    next_address_id = dest_priority_queue.get()
                                else:
                                    finished = True
                                    break

                            dest_priority_queue.put((hold_address_tuple[0], hold_address_tuple[1]))
                            required_truck_id = None
                            break
                        elif truck.has_driver and arrival >= latest_pickup_time:
                            ready_for_pickup = True
                            available_trucks.append(truck)

                # TODO: This may not work if package has specific truck requirement. May need to move this after the required_truck for loop
                if ready_for_pickup:
                    min_pkg_truck = available_trucks[0]
                    for truck in available_trucks:
                        if truck.total_packages < min_pkg_truck.total_packages:
                            min_pkg_truck = truck
                            required_truck_id = min_pkg_truck.id

            dest_in_route.append(next_address_id[1])

            for same_route_set in same_route_combined_sets:
                if next_address_id[1] in same_route_set:
                    for item in same_route_set:
                        if not item == next_address_id[1]:
                            dest_in_route.append(item)
                    break
            for address_id in dest_in_route:
                packages_to_deliver = pkg_dict.get(address_id)
                if required_truck_id is None:
                    for package in packages_to_deliver:
                        if package.truck is not None:
                            required_truck_id = package.truck
                            break
                # If picking up packages from HUB or package does not have a requirement
                # for specific trick, then do NOT add to total packages
                if required_truck_id is None and not address_id == 1:
                    total_packages += len(packages_to_deliver)

            if required_truck_id is None:
                # For each truck that has driver, if the truck can carry the additional
                # total packages, add it to the available_trucks list
                # If the available_trucks list is not empty, select the truck with less
                # total packages
                # Else if the list is empty, select the back-up truck and
                # set the back-up truck's departure to the earliest arrival truck with driver

                available_trucks = []
                for truck in trucks:
                    if truck.has_driver and total_packages <= truck.max_capacity - truck.total_packages:
                        available_trucks.append(truck)
                if len(available_trucks) > 0:
                    min_pkg_truck = available_trucks[0]
                    for truck in available_trucks:
                        if truck.total_packages < min_pkg_truck.total_packages:
                            min_pkg_truck = truck
                    required_truck = min_pkg_truck
                else:
                    for truck in trucks:
                        if not truck.has_driver:
                            required_truck = truck
                            break
            else:
                for truck in trucks:
                    if truck.id == required_truck_id:
                        required_truck = truck
                        break

            for address_id in dest_in_route:
                path = []
                packages_per_route = 0

                # If address_id is not HUB, calculate total_packages for each route
                # If address_id is HUB, truck is picking up packages; therefore, it does not count
                packages_to_deliver = pkg_dict.get(address_id)
                if not address_id == 1:
                    for package in packages_to_deliver:
                        if package.truck is None:
                            packages_per_route += 1
                        else:
                            index_to_remove = []
                            for index in range(len(required_truck.reserved_pkg)):
                                if required_truck.reserved_pkg[index] == package.pkg_id:
                                    index_to_remove.append(index)
                                    break
                            for index in index_to_remove:
                                required_truck.reserved_pkg.pop(index)
                # Get to_vertex from graph using address_id
                to_vertex = graph.get_vertex(address_id)
                # Get shortest path and calculate arrival time
                path = graph.get_shortest_path(required_truck.current_location, to_vertex)

                if len(path) > 2:
                    sub_route_departure = required_truck.departure
                    # Start with the second address_id and ignore the first and last
                    for index in range(len(path)):
                        if 0 < index < len(path) - 1:
                            if path[index] in pkg_dict and not path[index] == 1:
                                pkg_list = pkg_dict.get(path[index])
                                if len(pkg_list) <= truck.max_capacity - truck.total_packages:
                                    sub_route_distance = graph.get_vertex(index).distance
                                    dt = datetime.combine(date.today(), sub_route_departure) + timedelta(minutes=int(sub_route_distance / SPEED * 60))
                                    arrival = dt.time()

                                    print_pkg_loading(pkg_list, required_truck, index, arrival)

                                    pkg_dict.pop(path[index])
                                    required_truck.total_packages += len(pkg_list)
                                    required_truck.departure = arrival
                                    index += 1

                distance = to_vertex.distance
                dt = datetime.combine(date.today(), required_truck.departure) + timedelta(minutes=int(distance/SPEED*60))
                arrival = dt.time()
                # Create new route and add to required_truck -> routes{}
                # Update total_packages for required_truck
                route = Route(from_vertex, to_vertex, required_truck.departure, arrival)
                required_truck.add_route(route, path)
                required_truck.total_packages += packages_per_route

                if address_id == 1:
                    print_pkg_pickup(packages_to_deliver, required_truck, arrival)
                    # Load hold packages from pickup_packages{} loaded earlier into pkg_dict
                    # Array holding address_id to be later removed from pickup_packages{}
                    address_to_remove = []
                    for hold_address in pickup_packages.keys():
                        hold_packages = pickup_packages.get(hold_address)
                        for hold_pkg in hold_packages:
                            for item in packages_to_deliver:
                                if hold_pkg.pkg_id == item.pkg_id:
                                    pkgs_to_transfer = pickup_packages.get(hold_address)
                                    # Set required_truck for each package to the truck
                                    # selected for pick-up earlier
                                    for package in pkgs_to_transfer:
                                        package.truck = required_truck_id
                                    # Transfer hold packages to pkg_dict{}
                                    if hold_address not in pkg_dict.keys():
                                        pkg_dict[hold_address] = pkgs_to_transfer
                                    else:
                                        pkg_list = pkg_dict.get(hold_address)
                                        for package in pkgs_to_transfer:
                                            pkg_list.append(package)
                                    address_to_remove.append(hold_address)
                                    break
                    for address in address_to_remove:
                        pickup_packages.pop(address)
                    prioritize_pkg_dict()
                else:
                    print_pkg_loading(packages_to_deliver, required_truck, address_id, arrival)

                # Update departure, start location for next route, truck's location,
                # and remove delivered destination from pkg_dict
                required_truck.departure = arrival
                from_vertex = to_vertex
                required_truck.current_location = to_vertex
                pkg_dict.pop(address_id)
                # Clear shortest path calculation
                for vertex in vertex_list:
                    vertex.distance = float('inf')
                # Check if truck has delivered its final package and send it back to HUB
                # to pick up more packages
                if required_truck.total_packages == MAX_PKG_PER_TRUCK and len(required_truck.reserved_pkg) < 1:
                    hub_vertex = graph.get_vertex(1)
                    path = graph.get_shortest_path(required_truck.current_location, hub_vertex)
                    distance = hub_vertex.distance
                    dt = datetime.combine(date.today(), required_truck.departure) + timedelta(
                        minutes=int(distance / SPEED * 60))
                    arrival = dt.time()
                    # Create new route and add to required_truck -> routes{}
                    # Update total_packages for required_truck
                    route = Route(from_vertex, hub_vertex, required_truck.departure, arrival)
                    required_truck.add_route(route, path)
                    print("Sending Truck %d back to HUB. Truck will arrive at HUB at %s" % (required_truck.id, arrival))

                    # Update departure, start location for next route, truck's location,
                    # and remove delivered destination from pkg_dict
                    required_truck.departure = arrival
                    from_vertex = hub_vertex
                    required_truck.current_location = hub_vertex

                    for truck in trucks:
                        if not truck.has_driver and truck.departure is None:
                            truck.departure = required_truck.departure
                            print("Driver from Truck %d will be delivering packages from Truck %d" % (required_truck.id, truck.id))
                            print('')

    print("==============================================================================")
    for truck in trucks:
        print("Routes for Truck %d: " % truck.id)
        for route in truck.routes.keys():
            print(route)
            print(truck.routes.get(route))
        print("Total packages delivered: " + str(truck.total_packages))
        print("==========================================================================")






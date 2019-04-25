# Name: Thanh Truong. StudentID: #001062385

import csv
import sys
from inspect import currentframe, getframeinfo
from datetime import datetime, time, timedelta, date
from operator import attrgetter
from queue import PriorityQueue
from package import Package, Deadline
from address import Address
from graph import Vertex, Graph
from truck import Truck, Route
from chaininghashtable import ChainingHashTable

# Dictionary to hold (address/address_id) pairs
address_dict = {}
# Dictionary to hold (address_id/[packages]) pairs
pkg_dict = {}
# Set of delivery deadlines used to set Priority
deadline_set = set()
# List of all sets in the same route
same_route_set_list = []
# Priority queue organized by address_id and priority
dest_priority_queue = PriorityQueue()
# List of all graph with vertices representing packages that are to be delivered together in the same route
same_route_combined_sets = []
# List of all vertices in graph
vertex_list = []
graph = Graph()
# Dictionary of packages that require pick-up later
pickup_packages = {}
# Chaining Hash Table
pkg_hash_table = ChainingHashTable()

MAX_PKG_PER_TRUCK = 16
SPEED = 18
trucks = []


def load_graph(filename):

    # Open file, read package data one line at a time skipping the first row (header).
    with open(filename) as csvfile:
        # Flag to save address for HUB
        hub_address_saved = False
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
            while not hub_address_saved:
                hub_address = address
                hub_address_saved = True
            # Add address to address_dict
            # TODO: Remove address_dict
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
    return hub_address


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


# pkg_id  - int
# weight - float
# deadline - Deadline
# required_truck - int
# same_route_packages - [int]
# pickup_time - Deadline
def add_package_to_pkg_dict(pkg_id, street_address, city, zip_code, state, weight, deadline, later_pickup_time, delivery_truck, same_route_packages):
    # Get address_id from address_dict{}
    address_tuple = get_address_from_address_dict(street_address, city, zip_code, state)
    vertex_address = address_tuple[1]

    # Create package obj
    new_package = Package(pkg_id, vertex_address, weight)

    # Set delivery deadline
    # Deadline is hardcoded to 23:00:00 if set to 'EOD'

    # Add each unique deadline to the deadline_set and package
    new_package.add_delivery_deadline(deadline.time)
    deadline_set.add(deadline)

    # Set specific truck requirement
    if not (delivery_truck == ''):
        new_package.set_truck(delivery_truck)

    # Set combined packages requirement
    if len(same_route_packages) > 0:
        temp_set = set()
        temp_set.add(int(new_package.pkg_id))
        for package_id in same_route_packages:
            temp_set.add(package_id)

        same_route_set_list.append(temp_set)

    # Add route back to HUB if package has a pickup_time
    if not (later_pickup_time == ''):
        # Add deadline to deadline_set
        deadline_set.add(later_pickup_time)
        # Create a new package obj
        pickup_package = Package(pkg_id, hub_address, weight)
        pickup_package.add_delivery_deadline(later_pickup_time.time)
        # Add pickup_package to dictionary
        if pickup_package.address not in pkg_dict.keys():
            pkg_dict[pickup_package.address] = [pickup_package]
        else:
            pkg_list1 = pkg_dict.get(pickup_package.address)
            pkg_list1.append(pickup_package)

        # Add delivery package to pickup_packages{} for delivery after pickup
        if new_package.address not in pickup_packages.keys():
            pickup_packages[new_package.address] = [new_package]
        else:
            pkg_list2 = pickup_packages.get(new_package.address)
            pkg_list2.append(new_package)

    else:
        # Add package to dictionary
        if new_package.address not in pkg_dict.keys():
            pkg_dict[new_package.address] = [new_package]
        else:
            pkg_list3 = pkg_dict.get(new_package.address)
            pkg_list3.append(new_package)

    return pkg_dict


def update_pkg_dict():
    deadline_set.clear()
    same_route_set_list.clear()
    packages_to_remove = []
    for package_list in pkg_dict.values():
        for package in package_list:
            if package.deadline is not None:
                # Add deadline to deadline_set
                delivery_deadline = Deadline(package.deadline)
                deadline_set.add(delivery_deadline)

                # Set combined packages requirement
                if len(package.combined_pkg) > 0:
                    temp_set = set()
                    temp_set.add(int(package.pkg_id))
                    for package_id in package.combined_pkg:
                        temp_set.add(package_id)

                    same_route_set_list.append(temp_set)

                # If package has later_pickup_time, transfer the package with actual destination
                # to pickup_package{} to be later added to pkg_dict after pickup

                if package.address == hub_address:
                    # Find the actual package
                    for package_list2 in pkg_dict.values():
                        for package2 in package_list2:
                            if package2.pkg_id == package.pkg_id and not package2.address == hub_address:
                                delivered_package = package2
                                packages_to_remove.append(delivered_package)

                                # Add delivery package to pickup_packages{} for delivery after pickup
                                if delivered_package.address not in pickup_packages.keys():
                                    pickup_packages[delivered_package.address] = [delivered_package]
                                else:
                                    pkg_list2 = pickup_packages.get(delivered_package.address)
                                    pkg_list2.append(delivered_package)

    for package in packages_to_remove:
        package_list = pkg_dict.get(package.address)
        if len(package_list) > 1:
            package_list.remove(package)
        else:
            pkg_dict.pop(package.address)


def load_pkg_data(filename):
    with open(pkg_filename) as csvfile:
        readCSV = csv.reader(csvfile)
        # Skip the header
        next(readCSV)

        for row in readCSV:
            pkg_id = int(row[0])
            street_address = row[1]
            city = row[2]
            zip_code = row[3]
            state = row[4]
            weight = float(row[5])

            if row[6] == 'EOD':
                deadline = Deadline(time(23, 0, 0))

            else:
                split_time = row[6].split(':')
                hour = int(split_time[0])
                # Split string again to remove 'AM'/'PM'
                minute = int(split_time[1].split(' ')[0])
                deadline = Deadline(time(hour, minute, 0))

            if not (row[7] == ''):
                # Create a new Deadline using pickup_time
                split_time = row[7].split(':')
                hour = int(split_time[0])
                # Split string again to remove 'AM'/'PM'
                minute = int(split_time[1].split(' ')[0])
                pickup_deadline = Deadline(time(hour, minute, 0))
            else:
                pickup_deadline = row[7]

            # Set specific truck requirement
            if not (row[8] == ''):
                delivery_truck = int(row[8])
            else:
                delivery_truck = row[8]

            # Set combined packages requirement
            same_route_packages = []
            if not (row[9] == ''):
                split_list = row[9].split(',')
                for item in split_list:
                    same_route_packages.append(int(item))
            else:
                same_route_packages = row[9]

            add_package_to_pkg_dict(pkg_id, street_address, city, zip_code, state, weight, deadline, pickup_deadline, delivery_truck, same_route_packages)

    # Go through list of same_route_sets to combine sets
    combined_set_list = []
    while len(same_route_set_list) > 0:
        sets_to_remove = []

        first_set = None
        for set_index in range(len(same_route_set_list)):
            if set_index == 0:
                first_set = same_route_set_list[set_index]
                sets_to_remove.append(same_route_set_list[set_index])
            else:
                if len(first_set.intersection(same_route_set_list[set_index])) > 0:
                    sets_to_remove.append(same_route_set_list[set_index])

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


def prioritize_pkg_dict():

    # Iterate through the set of all deadlines and assign priority
    sorted_deadline_set = sorted(deadline_set)
    priority = 1

    for deadline in sorted_deadline_set:
        deadline.priority = priority
        priority += 1

    # Iterate through pkg_dict (address_id/[packages]).
    # For each list of packages, sort the list to find the earliest deadline.
    # Assign priority
    for key in pkg_dict.keys():

        package_list = pkg_dict.get(key)
        if len(package_list) > 1:
            package_list = sorted(package_list, key=attrgetter('deadline'))

        if key == hub_address:
            earliest_package = package_list[len(package_list) - 1].deadline
        else:
            earliest_package = package_list[0].deadline

        for deadline in deadline_set:
            if deadline.time == earliest_package:
                priority = deadline.priority

        dest_priority_queue.put((priority, key))

    return dest_priority_queue


def create_hash_table():
    for address in pkg_dict.keys():
        package_list = pkg_dict.get(address)
        for package in package_list:
            pkg_hash_table.insert(package)


# This function prints loading of packages onto Truck
def print_pkg_loading(package_list, required_truck, address, arrival):
    pkg_loading_file = open('package_loading.csv', 'a')
    pkg_loading_file.seek(0, 2)
    wr = csv.DictWriter(pkg_loading_file, fieldnames=pkg_fields, lineterminator='\n')

    for pkg in package_list:
        pkg.pickup_time = required_truck.pickup_time
        pkg.delivered_time = arrival
        wr.writerow({'PackageID': pkg.pkg_id, 'Truck': required_truck.id, 'Delivery Address': address, 'Delivered Time': str(arrival)})

    pkg_loading_file.close()


def output_truck_routes():
    # Set up output file for trucks' routes
    truck_route = open('routes.csv', 'w')

    truck_fields = ('Truck', 'Departure', 'Departure Time', 'Arrival', 'Arrival Time', 'Route', 'Package(s) Delivered')
    truck_wr = csv.DictWriter(truck_route, fieldnames=truck_fields, lineterminator='\n')

    truck_wr.writeheader()
    truck_route.seek(0, 2)
    wr = csv.DictWriter(truck_route, fieldnames=truck_fields, lineterminator='\n')

    for truck in trucks:
        for route in truck.routes.keys():
            departure_address = list(address_dict.keys())[route.start_vertex.address_id - 1]
            destination_address = list(address_dict.keys())[route.end_vertex.address_id - 1]
            wr.writerow({'Truck': truck.id, 'Departure': departure_address, 'Departure Time': str(route.departure), 'Arrival': destination_address, 'Arrival Time': route.arrival})
            count = 0
            for dest_pkg_tuple in truck.routes.get(route):
                destination_address = list(address_dict.keys())[dest_pkg_tuple[0] - 1]
                package_list = dest_pkg_tuple[1]
                if len(package_list) > 0:
                    packages = ''
                    for package_index in range(len(package_list)):
                        if package_index == len(package_list) - 1:
                            packages += str(package_list[package_index].pkg_id)
                        else:
                            packages += str(package_list[package_index].pkg_id) + ', '
                    wr.writerow({'Route': destination_address, 'Package(s) Delivered': packages})
                else:
                    wr.writerow({'Route': destination_address})


# This function prints packages picked up at HUB
def print_pkg_pickup(package_list, required_truck, arrival):
    print("Picking package(s) at HUB. Package(s) #: ", end='')
    for pkg in package_list:
        pkg.pickup_time = required_truck.pickup_time
        pkg.delivered_time = arrival
        print(pkg.pkg_id, end=' ')
    print("loaded to Truck " + str(required_truck.id))
    print("\tPackage(s) will be picked up to at " + str(arrival))
    print('')


def get_user_input():
    prompts = ["Enter a package ID: ", "Enter delivery address: ", "Enter delivery city: ", "Enter delivery zip code: ", "Enter delivery state: ", "Enter delivery deadline: ", "Enter package weight: "]
    input_parameters = ['27', '1060 Dalton Ave S', 'Salt Lake City', '84104', 'UT', 'EOD', '5']
    # input_parameters = []
    # print("Enter the following information for the package to check status:")
    # for prompt_index in range(len(prompts)):
    #     user_input = input(prompts[prompt_index])
    #     input_parameters.append(user_input)

    input_address = Address(input_parameters[1], input_parameters[2], input_parameters[3], input_parameters[4])
    input_package = Package(int(input_parameters[0]), input_address, float(input_parameters[6]))

    str_time = input_parameters[5]
    valid_selection = False
    while not valid_selection:
        if ':' in str_time:
            split_time = input_parameters[5].split(':')
            hour = split_time[0]
            minute = split_time[1]
            if not hour.isnumeric() or not minute.isnumeric():
                str_time = input("Invalid time. Please, re-enter time (HH:MM): ")
            elif int(hour) <= 0 or int(hour) > 23 or int(minute) < 0 or int(minute) > 60:
                str_time = input("Invalid time. Please, re-enter time (HH:MM): ")
            else:
                deadline = time(int(hour), int(minute, 0))
                valid_selection = True
        elif str_time == 'EOD':
            deadline = time(23, 0, 0)
            valid_selection = True

    input_package.add_delivery_deadline(deadline)
    return input_package


def update_pkg_status(current_time):
    for bucket in pkg_hash_table.table:
        for item in bucket:
            if current_time < item.pickup_time:
                item.add_status(0)
            elif item.pickup_time <= current_time < item.delivered_time:
                item.add_status(1)
            else:
                item.add_status(2)


def update_truck_routes(current_time):
    for truck in trucks:
        for route in truck.routes.keys():
            if route.departure <= current_time <= route.arrival:
                truck.departure = route.arrival
                truck.current_location = route.end_vertex


def create_delivery_route():

    # Update truck's availability based on package-truck constraint
    for address_key in pkg_dict.keys():
        required_truck = None
        pkg_list = pkg_dict.get(address_key)
        for package in pkg_list:
            if package.truck is not None:
                for truck in trucks:
                    if truck.id == package.truck:
                        required_truck = truck
                        break
        if required_truck is not None:
            for package in pkg_list:
                package.truck = required_truck.id
                truck.reserved_pkg.append(package.pkg_id)
                truck.total_packages += 1

    # Total packages per routes in dest_in_route[]
    finished = False

    while not dest_priority_queue.empty():
        total_packages = 0
        required_truck_id = None
        required_truck = None
        dest_in_route = []

        next_address = dest_priority_queue.get()

        while next_address[1] not in pkg_dict.keys():
            if not dest_priority_queue.empty():
                next_address = dest_priority_queue.get()
            else:
                finished = True
                break

        if not finished:

            if next_address[1] == hub_address:
                pickup_package_list = pkg_dict.get(next_address[1])
                latest_pickup_time = pickup_package_list[len(pickup_package_list) - 1].deadline

                # if departure time for either truck 1 or truck 2 is less than pick_up time
                # continue loading other packages first
                # else if both trucks are ready for pick-up
                # select the truck with the less number of packages
                # Get to_vertex from graph using address_id
                next_address_id = None
                for address, id_value in address_dict.items():
                    if address == next_address[1]:
                        next_address_id = id_value
                        break
                to_vertex = graph.get_vertex(next_address_id)
                available_trucks = []
                ready_for_pickup = False
                for truck in trucks:
                    if truck.driver is not None:
                        # Calculate arrival time at HUB if departed from current location now
                        path = graph.get_shortest_path(truck.current_location, to_vertex)
                        distance = to_vertex.distance
                        dt = datetime.combine(date.today(), truck.departure) + timedelta(
                            minutes=int(distance / SPEED * 60))
                        arrival = dt.time()

                        # Clear shortest path calculation
                        for vertex in vertex_list:
                            vertex.distance = float('inf')

                        if truck.driver is not None and arrival < latest_pickup_time:
                            ready_for_pickup = False
                            hold_address_tuple = next_address
                            next_address = dest_priority_queue.get()

                            while next_address[1] not in pkg_dict.keys():
                                if not dest_priority_queue.empty():
                                    next_address = dest_priority_queue.get()
                                else:
                                    finished = True
                                    break

                            dest_priority_queue.put((hold_address_tuple[0], hold_address_tuple[1]))
                            required_truck_id = None
                            break
                        elif truck.driver is not None and arrival >= latest_pickup_time:
                            ready_for_pickup = True
                            available_trucks.append(truck)

                # TODO: This may not work if package has specific truck requirement. May need to move this after the required_truck for loop
                if ready_for_pickup:
                    min_pkg_truck = available_trucks[0]
                    for truck in available_trucks:
                        if truck.total_packages < min_pkg_truck.total_packages:
                            min_pkg_truck = truck
                            required_truck_id = min_pkg_truck.id

            dest_in_route.append(next_address[1])

            for same_route_set in same_route_combined_sets:
                if next_address[1] in same_route_set:
                    for item in same_route_set:
                        if not item == next_address[1]:
                            dest_in_route.append(item)
                    break
            for address_key in dest_in_route:
                if address_key in pkg_dict.keys():
                    packages_to_deliver = pkg_dict.get(address_key)
                    if required_truck_id is None:
                        for package in packages_to_deliver:
                            if package.truck is not None:
                                required_truck_id = package.truck
                                break
                    # If picking up packages from HUB or package does not have a requirement
                    # for specific trick, then do NOT add to total packages
                    if required_truck_id is None and not address_key == hub_address:
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
                    if truck.driver is not None and total_packages <= MAX_PKG_PER_TRUCK - truck.total_packages:
                        available_trucks.append(truck)
                if len(available_trucks) > 0:
                    min_pkg_truck = available_trucks[0]
                    for truck in available_trucks:
                        if truck.total_packages < min_pkg_truck.total_packages:
                            min_pkg_truck = truck
                    required_truck = min_pkg_truck
                else:
                    for truck in trucks:
                        if truck.driver is None:
                            required_truck = truck
                            break
            else:
                for truck in trucks:
                    if truck.id == required_truck_id:
                        required_truck = truck
                        break

            for address_key in dest_in_route:
                if address_key in pkg_dict.keys():
                    packages_per_route = 0

                    # If address_id is not HUB, calculate total_packages for each route
                    # If address_id is HUB, truck is picking up packages; therefore, it does not count
                    packages_to_deliver = pkg_dict.get(address_key)
                    if not address_key == hub_address:
                        for pkg in packages_to_deliver:
                            if pkg.truck is None:
                                packages_per_route += 1
                            else:
                                index_to_remove = []
                                for index in range(len(required_truck.reserved_pkg)):
                                    if required_truck.reserved_pkg[index] == pkg.pkg_id:
                                        index_to_remove.append(index)
                                        break
                                for index in index_to_remove:
                                    required_truck.reserved_pkg.pop(index)
                    # Get to_vertex from graph using address_id
                    address_id = None
                    for address, id_value in address_dict.items():
                        if address == address_key:
                            address_id = id_value
                    to_vertex = graph.get_vertex(address_id)
                    # Get shortest path and calculate arrival time
                    path = graph.get_shortest_path(required_truck.current_location, to_vertex)
                    # Add packages_to_deliver to path's destination
                    path[len(path) - 1][1].extend(packages_to_deliver)

                    if len(path) > 2:
                        sub_route_departure = required_truck.departure
                        # Start with the second address_id and ignore the first and last
                        for index in range(len(path)):
                            if 0 < index < len(path) - 1:
                                destination_address = list(address_dict.keys())[list(address_dict.values()).index(path[index][0])]
                                if destination_address in pkg_dict.keys() and not destination_address == hub_address:
                                    pkg_list = pkg_dict.get(destination_address)
                                    if len(pkg_list) <= MAX_PKG_PER_TRUCK - truck.total_packages:
                                        # Distance is the total distance from path[0][1]
                                        sub_route_distance = graph.get_vertex(path[index][0]).distance
                                        dt = datetime.combine(date.today(), sub_route_departure) + timedelta(minutes=int(sub_route_distance / SPEED * 60))
                                        arrival = dt.time()

                                        print_pkg_loading(pkg_list, required_truck, destination_address, arrival)

                                        pkg_dict.pop(destination_address)
                                        required_truck.total_packages += len(pkg_list)
                                        # required_truck.departure = arrival
                                        path[index][1].extend(pkg_list)
                                        index += 1

                    distance = to_vertex.distance
                    dt = datetime.combine(date.today(), required_truck.departure) + timedelta(
                        minutes=int(distance / SPEED * 60))
                    arrival = dt.time()
                    # Create new route and add to required_truck -> routes{}
                    # Update total_packages for required_truck
                    route = Route(required_truck.current_location, to_vertex, required_truck.departure, arrival)
                    required_truck.add_route(route, path)
                    required_truck.total_packages += packages_per_route

                    # Clear shortest path calculation
                    for vertex in vertex_list:
                        vertex.distance = float('inf')
                        vertex.pred_vertex = None

                    if address_key == hub_address:
                        print_pkg_loading(packages_to_deliver, required_truck, hub_address, arrival)

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
                        print_pkg_loading(packages_to_deliver, required_truck, address_key, arrival)

                    # Update departure, start location for next route, truck's location,
                    # and remove delivered destination from pkg_dict
                    required_truck.departure = arrival
                    from_vertex = to_vertex
                    required_truck.current_location = to_vertex
                    pkg_dict.pop(address_key)

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
                        print('*************************************************************')
                        print("Sending Truck %d back to HUB. Truck will arrive at HUB at %s" % (required_truck.id, arrival))

                        # Update departure, start location for next route, truck's location,
                        # and remove delivered destination from pkg_dict
                        required_truck.departure = arrival
                        from_vertex = hub_vertex
                        required_truck.current_location = hub_vertex
                        required_truck.completed_all_routes = True
                        # Clear shortest path calculation
                        for vertex in vertex_list:
                            vertex.distance = float('inf')
                            vertex.pred_vertex = None

                        for truck in trucks:
                            if truck.departure is None:
                                truck.departure = required_truck.departure
                                truck.pickup_time = required_truck.departure
                                driver = required_truck.id
                                print("Driver from Truck %d will be delivering packages from Truck %d" % (
                                required_truck.id, truck.id))
                        print('')
                        print('*************************************************************')

                        # If all trucks with driver have delivered all packages, switch
                        # back-up truck -> has_driver to True
                        for truck in trucks:
                            if truck.driver is not None:
                                if truck.completed_all_routes:
                                    mission_completed = True
                                else:
                                    mission_completed = False
                                    break
                        if mission_completed:
                            for truck in trucks:
                                if truck.driver is None:
                                    truck.driver = driver

    output_truck_routes()


def update_delivery_route(truck):

    # Total packages per routes in dest_in_route[]
    finished = False

    while not dest_priority_queue.empty():
        # total_packages = 0
        # required_truck_id = None
        # required_truck = None
        dest_in_route = []

        next_address = dest_priority_queue.get()

        while next_address[1] not in pkg_dict.keys():
            if not dest_priority_queue.empty():
                next_address = dest_priority_queue.get()
            else:
                finished = True
                break

        if not finished:

            if next_address[1] == hub_address:
                pickup_package_list = pkg_dict.get(next_address[1])
                latest_pickup_time = pickup_package_list[len(pickup_package_list) - 1].deadline

                # if departure time for either truck 1 or truck 2 is less than pick_up time
                # continue loading other packages first
                # else if both trucks are ready for pick-up
                # select the truck with the less number of packages
                # Get to_vertex from graph using address_id
                next_address_id = None
                for address, id_value in address_dict.items():
                    if address == next_address[1]:
                        next_address_id = id_value
                        break
                to_vertex = graph.get_vertex(next_address_id)
                # Determine if package is ready for pickup
                path = graph.get_shortest_path(truck.current_location, to_vertex)
                distance = to_vertex.distance
                dt = datetime.combine(date.today(), truck.departure) + timedelta(minutes=int(distance / SPEED * 60))
                arrival = dt.time()

                if arrival < latest_pickup_time:
                    hold_address_tuple = next_address
                    next_address = dest_priority_queue.get()

                    while next_address[1] not in pkg_dict.keys():
                        if not dest_priority_queue.empty():
                            next_address = dest_priority_queue.get()
                        else:
                            finished = True

                    dest_priority_queue.put((hold_address_tuple[0], hold_address_tuple[1]))

                # Clear shortest path calculation
                for vertex in vertex_list:
                    vertex.distance = float('inf')

            dest_in_route.append(next_address[1])

            for same_route_set in same_route_combined_sets:
                if next_address[1] in same_route_set:
                    for item in same_route_set:
                        if not item == next_address[1]:
                            dest_in_route.append(item)
                    break

            for address_key in dest_in_route:
                if address_key in pkg_dict.keys():
                    # packages_per_route = 0

                    # If address_id is not HUB, calculate total_packages for each route
                    # If address_id is HUB, truck is picking up packages; therefore, it does not count
                    packages_to_deliver = pkg_dict.get(address_key)
                    # packages_per_route += len(packages_to_deliver)

                    # Get to_vertex from graph using address_id
                    address_id = None
                    for address, id_value in address_dict.items():
                        if address == address_key:
                            address_id = id_value
                    to_vertex = graph.get_vertex(address_id)
                    # Get shortest path and calculate arrival time
                    path = graph.get_shortest_path(truck.current_location, to_vertex)
                    # Add packages_to_deliver to path's destination
                    path[len(path) - 1][1].extend(packages_to_deliver)

                    if len(path) > 2:
                        sub_route_departure = truck.departure
                        # Start with the second address_id and ignore the first and last
                        for index in range(len(path)):
                            if 0 < index < len(path) - 1:
                                destination_address = list(address_dict.keys())[list(address_dict.values()).index(path[index][0])]
                                if destination_address in pkg_dict.keys() and not destination_address == hub_address:
                                    pkg_list = pkg_dict.get(destination_address)
                                    # packages_per_route += len(pkg_list)
                                    # Distance is the total distance from path[0][1]
                                    sub_route_distance = graph.get_vertex(path[index][0]).distance
                                    dt = datetime.combine(date.today(), sub_route_departure) + timedelta(
                                        minutes=int(sub_route_distance / SPEED * 60))
                                    arrival = dt.time()

                                    print_pkg_loading(pkg_list, truck, destination_address, arrival)

                                    pkg_dict.pop(destination_address)
                                    # truck.total_packages += len(pkg_list)
                                    # required_truck.departure = arrival
                                    path[index][1].extend(pkg_list)
                                    index += 1

                    distance = to_vertex.distance
                    dt = datetime.combine(date.today(), truck.departure) + timedelta(
                        minutes=int(distance / SPEED * 60))
                    arrival = dt.time()
                    # Create new route and add to truck -> routes{}
                    # Update total_packages for truck
                    route = Route(truck.current_location, to_vertex, truck.departure, arrival)
                    truck.add_route(route, path)
                    # truck.total_packages += packages_per_route

                    # Clear shortest path calculation
                    for vertex in vertex_list:
                        vertex.distance = float('inf')
                        vertex.pred_vertex = None

                    if address_key == hub_address:
                        print_pkg_loading(packages_to_deliver, truck, hub_address, arrival)
                        # Load hold packages from pickup_packages{} loaded earlier into pkg_dict
                        # Array holding address_id to be later removed from pickup_packages{}
                        address_to_remove = []
                        for hold_address in pickup_packages.keys():
                            hold_packages = pickup_packages.get(hold_address)
                            for hold_pkg in hold_packages:
                                for item in packages_to_deliver:
                                    if hold_pkg.pkg_id == item.pkg_id:
                                        pkgs_to_transfer = pickup_packages.get(hold_address)
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
                        print_pkg_loading(packages_to_deliver, truck, address_key, arrival)

                    # Update departure, start location for next route, truck's location,
                    # and remove delivered destination from pkg_dict
                    truck.departure = arrival
                    from_vertex = to_vertex
                    truck.current_location = to_vertex
                    pkg_dict.pop(address_key)

    hub_vertex = graph.get_vertex(1)
    path = graph.get_shortest_path(truck.current_location, hub_vertex)
    distance = hub_vertex.distance
    dt = datetime.combine(date.today(), truck.departure) + timedelta(
        minutes=int(distance / SPEED * 60))
    arrival = dt.time()
    # Create new route and add to truck -> routes{}
    # Update total_packages for truck
    route = Route(from_vertex, hub_vertex, truck.departure, arrival)
    truck.add_route(route, path)
    print('*************************************************************')
    print("Sending Truck %d back to HUB. Truck will arrive at HUB at %s" % (truck.id, arrival))

    # Update departure, start location for next route, truck's location,
    # and remove delivered destination from pkg_dict
    truck.departure = arrival
    from_vertex = hub_vertex
    truck.current_location = hub_vertex
    truck.completed_all_routes = True
    # Clear shortest path calculation
    for vertex in vertex_list:
        vertex.distance = float('inf')
        vertex.pred_vertex = None

    output_truck_routes()


def simulate_delivery_routes(current_time):
    for truck in trucks:
        for route in list(truck.routes.keys()):
            if route.departure <= current_time <= route.arrival:
                path = truck.routes.get(route)

                for path_index in range(len(path)):
                    if path_index == 0:
                        departure_address = list(address_dict.keys())[path[path_index][0] - 1]
                        print("Truck %d departed %s at %s." % (truck.id, departure_address, route.departure))
                        print('')
                    else:
                        package_list = path[path_index][1]
                        if len(package_list) > 0:
                            concatenated_pkg = ''
                            destination = list(address_dict.keys())[path[path_index][0] - 1]
                            for package in package_list:
                                concatenated_pkg += str(package.pkg_id) + ', '
                                deliver_time = package.delivered_time
                            concatenated_pkg = concatenated_pkg[:-1:]
                            print("\tPackage %s will be delivered to %s at %s." % (
                            concatenated_pkg, destination, str(deliver_time)))
                            print('')
        print('====================================================================')


def get_new_time(prompt):
    valid_selection = False

    while not valid_selection:
        new_time = input(prompt)
        if ':' in new_time:
            split_time = new_time.split(':')
            hour = split_time[0]
            minute = split_time[1]
            if not hour.isnumeric() or not minute.isnumeric():
                prompt = "Invalid time. Please, re-enter time (HH:MM): "
            elif int(hour) <= 0 or int(hour) > 23 or int(minute) < 0 or int(minute) > 60:
                prompt = "Invalid time. Please, re-enter time (HH:MM): "
            else:
                current_time = time(int(hour), int(minute), 0)
                valid_selection = True
        else:
            prompt = "Invalid time. Please, re-enter time (HH:MM): "

    print("Current time updated to: " + str(current_time.strftime('%H:%M')))
    return current_time


def remove_package(package_to_remove):
    # Remove pkg from pkg_dict and pkg_hash_table
    pkg_hash_table.remove(package_to_remove)
    for package in pkg_dict.get(package_to_remove.address):
        if package == package_to_remove:
            package_list = pkg_dict.get(package_to_remove.address)
            if len(package_list) > 1:
                package_list.remove(package_to_remove)
            else:
                pkg_dict.pop(package_to_remove.address)

def print_main_menu():
    print("Menu:")
    print("\t1. Start delivery")
    print("\t2. Change current time")
    print("\t3. Check package status")
    print("\t4. Update package")
    print("\t5. Exit")


if __name__ == "__main__":
    # Set up output file for package loading
    pkg_loading_file = open('package_loading.csv', 'w')

    pkg_fields = ('PackageID', 'Truck', 'Delivery Address', 'Delivered Time')
    pkg_wr = csv.DictWriter(pkg_loading_file, fieldnames=pkg_fields, lineterminator='\n')

    pkg_wr.writeheader()
    pkg_loading_file.close()

    trucks = []

    # Load data from distance table and save them into an undirected graph
    # dist_filename = input("Enter name of distance data file: ")
    dist_filename = "distance_table.csv"
    hub_address = load_graph(dist_filename)

    # Create trucks and add to HUB location in graph
    i = 1
    while i < 4:
        truck = Truck(i)
        # Add driver to truck
        if i < 3:
            truck.driver = i
            truck.departure = time(8, 0, 0)
            truck.pickup_time = time(8, 0, 0)
        trucks.append(truck)
        graph.add_truck_to_hub(truck)
        i += 1

    # Load data for packages and save them into a priority queue.
    # Priority is assigned based on deadline.
    # Packages with combined packages constraint have the same Priority #
    # pkg_filename = input("Enter name of package data file: ")
    pkg_filename = "package_data.csv"
    load_pkg_data(pkg_filename)

    create_hash_table()
    prioritize_pkg_dict()

    create_delivery_route()

    # Reset truck's data
    for truck in trucks:
        truck.current_location = graph.get_vertex(address_dict.get(hub_address))
        truck.departure = time

    # Delivery simulation and UI
    print_main_menu()

    user_selection = 1

    while not user_selection == 5:
        user_selection = input("Select a number from 1-5 from the menu above: ")
        valid_selection = False
        while not valid_selection:
            if not user_selection.isnumeric():
                user_selection = input("Invalid selection. Enter a number from 1 - 4: ")
            elif int(user_selection) < 1 or int(user_selection) > 5:
                user_selection = input("Invalid selection. Enter a number from 1 - 4: ")
            else:
                user_selection = int(user_selection)
                valid_selection = True

        if user_selection == 1:
            current_time = time(8, 0, 0)
            print('')
            print("The current time is:\t" + current_time.strftime('%H: %M'))
            print('')
            simulate_delivery_routes(current_time)

        if user_selection == 2:
            prompt = "Enter a new time (HH:MM): "
            current_time = get_new_time(prompt)
            update_pkg_status(current_time)
            update_truck_routes(current_time)
            simulate_delivery_routes(current_time)

        if user_selection == 3:
            current_time = time(8, 0, 0)
            print('')
            print("The current time is:\t" + current_time.strftime('%H: %M'))
            print('')
            # Update package status
            update_pkg_status(current_time)
            update_truck_routes(current_time)

            pkg_to_search = get_user_input()

            pkg_found = pkg_hash_table.search(pkg_to_search)

            if pkg_found.deadline == time(23, 0, 0):
                converted_deadline = 'EOD'
            else:
                converted_deadline = pkg_found.deadline

            print("====================================================================")
            print("Package Number: " + str(pkg_found.pkg_id))
            print("Delivery Address: ")
            print(pkg_found.address)
            print("Weight: " + str(pkg_found.weight))
            print("Delivery Deadline: " + str(converted_deadline))
            if current_time >= pkg_found.delivered_time:
                print("Current Status: %s at %s" % (pkg_found.status, pkg_found.delivered_time))
            else:
                print("Current Status: " + pkg_found.status)
            print("====================================================================")

        if user_selection == 4:
            prompt = "Enter a new time (HH:MM): "
            current_time = get_new_time(prompt)
            # Update package status
            update_pkg_status(current_time)
            update_truck_routes(current_time)

            pkg_to_update = get_user_input()

            # Get the truck carrying the package
            for truck in trucks:
                for route in truck.routes.keys():
                    for dest_pkg_tuple in truck.routes.get(route):
                        destination_address = list(address_dict.keys())[dest_pkg_tuple[0] - 1]
                        if destination_address == pkg_to_update.address:
                            package_list = dest_pkg_tuple[1]
                            if len(package_list) > 0:
                                for package in package_list:
                                    if package.pkg_id == pkg_to_update.pkg_id:
                                        affected_truck = truck
                                        break

            # Iterate through the truck's routes and add all packages to pkg_dict
            for route in affected_truck.routes.keys():
                for dest_pkg_tuple in affected_truck.routes.get(route):
                    if len(dest_pkg_tuple[1]) > 0:
                        for package in dest_pkg_tuple[1]:
                            if not package.status == 'Delivered':
                                package.truck = affected_truck.id
                                if package.address not in pkg_dict.keys():
                                    pkg_dict[package.address] = [package]
                                else:
                                    package_list = pkg_dict.get(package.address)
                                    package_list.append(package)

            if pkg_hash_table.search(pkg_to_update) is not None:
                pkg_to_update = pkg_hash_table.search(pkg_to_update)
                if pkg_to_update.status == 'Delivered':
                    print('')
                    print("Package has been delivered")
                    print('')
                else:
                    print("Choose an option below to modify delivery requirements")
                    print("Menu:")
                    print("\t1. Change delivery address")
                    print("\t2. Change delivery deadline")
                    print("\t3. Go back")

                    user_selection = 1
                    while not int(user_selection) == 3:
                        user_selection = input("Select a number from 1-3 from the menu above: ")
                        valid_selection = False
                        while not valid_selection:
                            if not user_selection.isnumeric():
                                user_selection = input("Invalid selection. Enter a number from 1 - 3: ")
                            elif int(user_selection) < 1 or int(user_selection) > 3:
                                user_selection = input("Invalid selection. Enter a number from 1 - 3: ")
                            else:
                                user_selection = int(user_selection)
                                valid_selection = True

                        if 1 <= user_selection <= 2:
                            if user_selection == 1:
                                # new_street = input("Enter a street address: ")
                                # new_city = input("Enter a new city: ")
                                # new_zipCode = input("Enter a new zip code: ")
                                # new_state = input("Enter a new state: ")

                                new_street = '410 S State St'
                                new_city = 'Salt Lake City'
                                new_zipCode = '84111'
                                new_state = 'UT'

                                new_address = Address(new_street, new_city, new_zipCode, new_state)
                                # Get address from address_dict{}
                                new_address = list(address_dict.keys())[address_dict.get(new_address)-1]

                                # Remove pkg from pkg_dict and pkg_hash_table
                                remove_package(pkg_to_update)

                                # Update package's address
                                pkg_to_update.address = new_address

                            elif user_selection == 2:
                                prompt = "Enter new delivery deadline: "
                                new_delivery_deadline = get_new_time(prompt)
                                remove_package(pkg_to_update)
                                pkg_to_update.deadline = new_delivery_deadline

                            # Add package back into hash_table and pkg_dict
                            pkg_hash_table.insert(pkg_to_update)
                            if pkg_to_update.address not in pkg_dict.keys():
                                pkg_dict[pkg_to_update.address] = [pkg_to_update]
                            else:
                                package_list = pkg_dict.get(pkg_to_update.address)
                                package_list.append(pkg_to_update)

                            # Iterate through the truck's routes and transfer package to existing route
                            for route in affected_truck.routes.keys():
                                for dest_pkg_tuple in affected_truck.routes.get(route):
                                    if len(dest_pkg_tuple[1]) > 0:
                                        for package in dest_pkg_tuple[1]:
                                            package.truck = affected_truck.id

                            update_pkg_dict()

                            # Clear truck's routes
                            affected_truck.routes.clear()
                            affected_truck.reserved_pkg.clear()
                            affected_truck.completed_all_routes = False

                            prioritize_pkg_dict()
                            update_delivery_route(affected_truck)

                        else:
                            print_main_menu()












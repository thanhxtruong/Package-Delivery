# Name: Thanh Truong. StudentID: #001062385

import csv
from datetime import datetime, time, timedelta, date
from operator import attrgetter
from queue import PriorityQueue
from package import Package, Deadline
from address import Address
from graph import Vertex, Graph
from truck import Truck, Route
from chaininghashtable import ChainingHashTable

# Dictionary to hold (address/address_id) pairs
# This dictionary is used for easy look-up of address using address_id, which is used in
# graph's vertices
address_dict = {}
# Dictionary to hold (address_id/[packages]) pairs
# Package data from raw csv file is loaded into this dictionary, which is then use to create
# the PriorityQueue.
# By the time the PriorityQueue is created, pkg_dict will be empty
pkg_dict = {}
# All packages' delivery deadlines are put into this set, which is later used to assign priority
deadline_set = set()
# List of all sets of package_id in the same route
# The list of all packages that are required to be delivered together in the same route are
# first put into a set
# This list contains all of the created sets
same_route_set_list = []
# Priority queue organized by address and priority.
# By the time all packages have been loaded onto trucks, PriorityQueue will be empty.
dest_priority_queue = PriorityQueue()
# List of all sub-graph with vertices to which packages are to be delivered together in the same route.
# This list is created by replacing the pkg_id in same_route_set_list[] with address_id
same_route_combined_sets = []
# List of all vertices in a graph
vertex_list = []
graph = Graph()
# Chaining Hash Table holding package data for easy status look-up
pkg_hash_table = ChainingHashTable()
# List of all trucks available at WGUPS
trucks = []
# Departure time for Truck 3, which is set based on the earliest completion truck.
truck3_departure = None

# Maximum number of packages a truck can carry
MAX_PKG_PER_TRUCK = 16
# Truck's speed
SPEED = 18


# This function is used to load raw distance data from csv file into a Graph data structure.
# This function returns the address at HUB (hub_address).
# NOTE: In order for this function to work properly, the csv file MUST be formatted as
# shown.
def load_graph(filename):

    # Open file, read package data one line at a time skipping the first row (header).
    with open(filename) as csvfile:

        # Flag to save address for HUB. Once the HUB address is obtain, this flag
        # will be changed to True to stop break from the while loop.
        hub_address_saved = False
        # Index to assign address_id for each address
        index = 1

        readCSV = csv.reader(csvfile)
        # Skip the header
        next(readCSV)

        for row in readCSV:
            # String split raw data to get each component of the Address object
            split_address = row[0].split(',')
            address1 = split_address[0]
            city = split_address[1]
            zip_code = split_address[2]
            state = split_address[3]

            # Create a new Address object
            address = Address(address1, city, zip_code, state)

            # Assuming the csv file is formatted with the first row containing the HUB
            # address, this address will be saved into the global hub_address object.
            while not hub_address_saved:
                hub_address = address
                hub_address_saved = True

            # Add address to address_dict{}
            address_dict[address] = index

            # Create a new Vertex object for the new Address object and append it to
            # the global vertex_list[]
            _vertex = Vertex(index)
            vertex_list.append(_vertex)

            # Extract distance data from the csv file and save into a list
            j = 1
            dist_list = []
            while not float(row[j]) == 0:
                dist_list.append(float(row[j]))
                j += 1

            # Add vertex to the global Graph object.
            # Save distances into the adjacency list for the new vertex
            graph.add_vertex(_vertex)

            # Add undirected edges to graph
            address_list_index = 0
            for travel_distance in dist_list:
                graph.add_undirected_edge(_vertex, vertex_list[address_list_index], travel_distance)
                address_list_index += 1

            index += 1

    return hub_address


# This function iterates through the address_dict{} and returns the address_id (value) for a given set of string values
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


# This function takes all values for Package's attributes, create a new Package object, and add it to pkg_dict{}
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

    # Create a new Package object.
    new_package = Package(pkg_id, vertex_address, weight)

    # Set delivery deadline.
    # Add each unique deadline to the deadline_set.
    new_package.deadline = deadline.time
    deadline_set.add(deadline)

    # Set specific truck requirement
    if not (delivery_truck == ''):
        new_package.truck = trucks[delivery_truck - 1]

    # Add all packages that are required to be delivered together in the same route to
    # a set, which is then appended to the same_route_set_list[same_route_sets].
    # This list of sets will be used to ensure packages are delivered together.
    if len(same_route_packages) > 0:
        temp_set = set()
        temp_set.add(int(new_package.pkg_id))
        for package_id in same_route_packages:
            temp_set.add(package_id)

        same_route_set_list.append(temp_set)

    # If package has a specific pickup time requirement, add that package to Truck 1
    if not (later_pickup_time == ''):
        new_package.truck = trucks[0]

    # Add package to pkg_dict{}
    if new_package.address not in pkg_dict.keys():
        pkg_dict[new_package.address] = [new_package]
    else:
        pkg_list3 = pkg_dict.get(new_package.address)
        pkg_list3.append(new_package)

    return pkg_dict


# This function add a list of packages to the specified truck -> reserved_pkg{} at the specified address and
# remove the packages from the global pkg_dict{}.
def add_packages_to_truck(truck, address, packages):
    if not address in truck.reserved_pkg.keys():
        truck.reserved_pkg[address] = packages
    else:
        truck.reserved_pkg[address].extend(packages)

    # Set package -> truck for each package
    for package in packages:
        package.truck = truck

    # Recalculate truck -> total_packages
    truck.total_packages += len(packages)
    pkg_dict.pop(address)


# This function iterate through pkg_dict{} and load packages with pre-determined truck to the corresponding truck
def add_pkg_with_preset_truck():
    for address, packages in list(pkg_dict.items()):

        # Iterate through the list of packages at each address, check if any package has a pre-determined truck.
        # If True, set value for preset_truck and exit the for loop.
        preset_truck = None
        for package in packages:
            if package.truck is not None:
                preset_truck = package.truck
                break

        # If any of the package in the package list at the current address has a pre-determined truck,
        # add the entire package list at that address to truck -> reserved_pkg{} and remove them from pkg_dict{}
        # Recalculate truck -> total_packages
        if preset_truck is not None:
            add_packages_to_truck(preset_truck, address, packages)


# This function loads the remaining packages in pkg_dict{} (that were put into the PriorityQueue) onto
# Truck 1 and Truck 2 alternatively as long as they're fit. Once both Truck 1 and Truck 2 are full, packages
# will be loaded onto Truck 3.
def load_remaining_packages():

    # Keep track of previously selected truck
    selected_truck = trucks[1]
    while not dest_priority_queue.empty():

        address = dest_priority_queue.get()[1]
        # If all packages in package_list can fit into the selected truck, load packages onto that truck.
        # Else, load into the other truck.
        # If neither Truck 1 nor Truck 2 can carry these packages, load onto Truck 3
        package_list = pkg_dict.get(address)
        if len(package_list) <= MAX_PKG_PER_TRUCK - selected_truck.total_packages:
            add_packages_to_truck(selected_truck, address, package_list)
        else:
            # Select the other alternative (Truck 2 if Truck 1 does not fit and vice versa)
            if selected_truck == trucks[1]:
                selected_truck = trucks[0]
                if len(package_list) <= MAX_PKG_PER_TRUCK - selected_truck.total_packages:
                    add_packages_to_truck(selected_truck, address, package_list)
                # If the other truck still does not fit, load onto Truck 3
                else:
                    selected_truck = trucks[2]
                    add_packages_to_truck(selected_truck, address, package_list)

        # Alternate truck
        # If BOTH Truck 1 and Truck 2 are NOT full, switch between Truck 1 and Truck 2.
        # If Truck 1 was previously selected, switch to Truck 2 and vice versa.
        # If Truck 3 was previously selected, switch back to Truck 1.
        if trucks[0].total_packages < MAX_PKG_PER_TRUCK and trucks[1].total_packages < MAX_PKG_PER_TRUCK:
            if selected_truck == trucks[0]:
                selected_truck = trucks[1]
            elif selected_truck == trucks[1]:
                selected_truck = trucks[0]
            elif selected_truck == trucks[2]:
                selected_truck = trucks[0]
        # If Truck 1 is NOT full, but Truck 2 is full, switch back to Truck 1 regardless.
        elif trucks[0].total_packages < MAX_PKG_PER_TRUCK:
            if selected_truck == trucks[2]:
                selected_truck = trucks[0]
            else:
                selected_truck = trucks[0]
        # If Truck 2 is NOT full, but Truck 1 is full, switch back to Truck 2 regardless.
        elif trucks[1].total_packages < MAX_PKG_PER_TRUCK:
            if selected_truck == trucks[2]:
                selected_truck = trucks[1]
            else:
                selected_truck = trucks[1]
        # If BOTH Truck 1 and 2 are full, set to Truck 3.
        else:
            selected_truck = trucks[2]


# This function loads package data from the csv file into the global
# pkg_dict{Address: [Packages]} dictionary.
# NOTE: In order for this function to work properly, the csv file MUST be formatted
# as shown.
def load_pkg_data(filename):
    with open(filename) as csvfile:
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

            # Packages with deadline as 'EOD' are hard-coded to the last hour 23:00.
            # Assuming it's not feasible to have deadlines that pass business hours,
            # this is the work-around in order to assign priority.
            if row[6] == 'EOD':
                deadline = Deadline(time(23, 0, 0))

            else:
                split_time = row[6].split(':')
                hour = int(split_time[0])
                # Split string again to remove 'AM'/'PM'
                minute = int(split_time[1].split(' ')[0])
                deadline = Deadline(time(hour, minute, 0))

            # If the package has a specific pick-up time requirement, create a new
            # Deadline object for the required time.
            if not (row[7] == ''):
                # Create a new Deadline using pickup_time
                split_time = row[7].split(':')
                hour = int(split_time[0])
                # Split string again to remove 'AM'/'PM'
                minute = int(split_time[1].split(' ')[0])
                pickup_deadline = Deadline(time(hour, minute, 0))
            else:
                pickup_deadline = row[7]

            # Set specific truck requirement.
            if not (row[8] == ''):
                delivery_truck = int(row[8])
            else:
                delivery_truck = row[8]

            # Append all packages that are required to be delivered together to the
            # same_route_packages[] list.
            same_route_packages = []
            if not (row[9] == ''):
                split_list = row[9].split(',')
                for item in split_list:
                    same_route_packages.append(int(item))
            else:
                same_route_packages = row[9]

            # Create a new Package object and add it to the pkg_dict{} dictionary.
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


# This function iterates through the pkg_dict{} dictionary and create a PriorityQueue.
# Priority is assigned based on delivery deadline.
# Packages with no specified delivery deadline but are required to be delivered together
# will take the priority of the package with the earliest delivery deadline in the group.
def prioritize_pkg_dict(package_dict):

    # Sort the deadline_set by deadline
    sorted_deadline_set = sorted(deadline_set)

    # Iterate through the sorted deadline_set and assign priority in increment of 1.
    priority = 1
    for deadline in sorted_deadline_set:
        deadline.priority = priority
        priority += 1

    # Iterate through pkg_dict{} dictionary.
    # For each list of packages, sort the list to find the earliest deadline.
    # Assign priority for the delivery address_id based on the earliest deadline.
    for key in package_dict.keys():

        package_list = package_dict.get(key)
        if len(package_list) > 1:
            package_list = sorted(package_list, key=attrgetter('deadline'))

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
def output_pkg_loading(package_list, required_truck, address, arrival):
    pkg_loading_file = open('package_loading.csv', 'a')
    pkg_loading_file.seek(0, 2)
    wr = csv.DictWriter(pkg_loading_file, fieldnames=pkg_fields, lineterminator='\n')

    for pkg in package_list:
        pkg.pickup_time = required_truck.pickup_time
        pkg.delivered_time = arrival
        wr.writerow({'PackageID': pkg.pkg_id, 'Truck': required_truck.id, 'Delivery Address': address, 'Delivered Time': str(arrival)})

    pkg_loading_file.close()


def output_truck_routes(truck3_driver):
    # Set up output file for trucks' routes
    print('')
    print("Delivery routes for each truck is output to routes.csv file")
    print('=========================================================================================')
    truck_route = open('routes.csv', 'w')

    truck_fields = ('Truck', 'Departure', 'Departure Time', 'Arrival', 'Arrival Time', 'Route', 'Package(s) Delivered')
    truck_wr = csv.DictWriter(truck_route, fieldnames=truck_fields, lineterminator='\n')

    truck_wr.writeheader()
    truck_route.seek(0, 2)
    wr = csv.DictWriter(truck_route, fieldnames=truck_fields, lineterminator='\n')

    total_mileage = 0
    for truck in trucks:
        # Calculate the sum of total mileage for all trucks
        total_mileage += truck.total_miles

        # Print driver for Truck 3
        if truck == trucks[2]:
            print("Driver from %s will deliver packages for Truck 3" %truck3_driver)

        print("Total packages packages delivered by Truck %d is %d packages." %(truck.id, truck.total_packages))
        print("Total mileage traveled by Truck %d is %.2f miles." %(truck.id, truck.total_miles))
        print('')

        # Output each route to CSV file.
        for route in truck.routes.keys():
            departure_address = list(address_dict.keys())[route.start_vertex.address_id - 1]
            destination_address = list(address_dict.keys())[route.end_vertex.address_id - 1]
            wr.writerow({'Truck': truck.id, 'Departure': departure_address, 'Departure Time': str(route.departure), 'Arrival': destination_address, 'Arrival Time': route.arrival})
            count = 0
            for dest_pkg_tuple in truck.routes.get(route):
                destination_address = list(address_dict.keys())[dest_pkg_tuple[0] - 1]
                package_list = dest_pkg_tuple[2]
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

    # Print the total mileages travelled by all trucks
    print("The total mileages traveled by all trucks is: %.2f miles." % total_mileage)


def get_user_input():
    prompts = ["Enter a package ID: ", "Enter delivery address: ", "Enter delivery city: ", "Enter delivery zip code: ", "Enter delivery state: ", "Enter delivery deadline: ", "Enter package weight: "]
    input_parameters = ['27', '1060 Dalton Ave S', 'Salt Lake City', '84104', 'UT', 'EOD', '5']
    # input_parameters = ['9', '300 State St', 'Salt Lake City', '84103', 'UT', 'EOD', '2']
    input_parameters = []
    print("Enter the following information for the package:")
    for prompt_index in range(len(prompts)):
        user_input = input(prompts[prompt_index])
        input_parameters.append(user_input)

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

    input_package.deadline = deadline
    return input_package


# This function iterate through the pkg_hash_table and update package -> status based on the
# current time
def update_pkg_status(current_time):
    for bucket in pkg_hash_table.table:
        for item in bucket:
            if current_time < item.pickup_time:
                item.add_status(0)
            elif item.pickup_time <= current_time < item.delivered_time:
                item.add_status(1)
            else:
                item.add_status(2)


# This function updates truck's current location and departure time based on the input current time.
# The affected_truck -> routes {} is also iterated to add all packages that have not been delivered to the
# affected_truck -> reserved_pkg{} list for recalculation of delivery routes after changes to package data.
def update_truck_routes(current_time, affected_truck):
    for truck in trucks:
        if truck == affected_truck:
            truck.total_miles = 0
            for route in truck.routes.keys():
                # Re-set truck's departure and current location to the route that falls between the current time.
                # Re-calculate truck -> total_miles after delivering packages up to this point.
                if route.departure <= current_time <= route.arrival:
                    truck.departure = route.arrival
                    truck.current_location = route.end_vertex
                    truck.total_miles += route.miles
                elif route.arrival <= current_time:
                    truck.total_miles += route.miles
                # Add packages that have not been delivered back to affected_truck -> reserved_pkg{}
                elif route.arrival >= current_time:
                    for dest_distance_pkg_tuple in truck.routes.get(route):
                        if len(dest_distance_pkg_tuple[2]) > 0:
                            address = list(address_dict.keys())[dest_distance_pkg_tuple[0] - 1]
                            truck.reserved_pkg[address] = dest_distance_pkg_tuple[2]
        else:
            for route in truck.routes.keys():
                # Re-set truck's departure and current location to the route that falls between the current time.
                if route.departure <= current_time <= route.arrival:
                    truck.departure = route.arrival
                    truck.current_location = route.end_vertex


# This function pop a specific item from the truck_pkg_priority_queue
def pop_item_from_queue(address, priority_queue):
    item_found = False
    items_to_put_back = []
    # Keep popping items from the PriorityQueue until the item is found or the queue is empty.
    # All popped items that are not the searched item will be appended to the items_to_put_back[]
    while not item_found and not priority_queue.empty():
        next_address = priority_queue.get()
        if not next_address[1] == address:
            item_found = False
            items_to_put_back.append(next_address)
        else:
            item_found = True

    # Add items in items_to_put_back[] back into the queue
    for priority_address_tuple in items_to_put_back:
        priority_queue.put(priority_address_tuple)


# This function re-prioritize packages in the selected truck -> reserved_pkg {} based on delivery deadline after all
# packages have been loaded onto truck.
# If packages have the same delivery deadline (therefore, priority), packages that are closest to the current truck's
# location will be delivered first.
# As each address is popped from the queue, a delivery route will be created and added to truck -> routes {}.
def create_delivery_route(truck):

    # Prioritize truck -> reserved_pkg {}
    truck_pkg_priority_queue = prioritize_pkg_dict(truck.reserved_pkg)

    same_priority_address = []
    # Pop the next address in queue.
    # Keep popping until all addresses in the queue with the same priority are added to the
    # same_priority_address[] list.
    while not truck_pkg_priority_queue.empty():
        same_priority = True
        priority_address_tuple = truck_pkg_priority_queue.get()
        current_priority = priority_address_tuple[0]
        same_priority_address.append(priority_address_tuple)
        while same_priority and not truck_pkg_priority_queue.empty():
            priority_address_tuple = truck_pkg_priority_queue.get()
            if priority_address_tuple[0] == current_priority:
                same_priority_address.append(priority_address_tuple)
            else:
                truck_pkg_priority_queue.put((priority_address_tuple[0], priority_address_tuple[1]))
                same_priority = False

        # Iterate through the same_priority_address[] list to find the shortest_distance
        if len(same_priority_address) > 1:
            shortest_distance = float('inf')
            for priority_address_tuple in same_priority_address:
                to_vertex = graph.get_vertex(address_dict.get(priority_address_tuple[1]))
                path = graph.get_shortest_path(truck.current_location, to_vertex)
                if shortest_distance > path[len(path) - 1][1]:
                    shortest_distance = path[len(path) - 1][1]
                    shortest_path = path
                    next_priority_address_tuple = priority_address_tuple
                    next_vertex = to_vertex
                graph.reset_adjacency_list()
        else:
            next_priority_address_tuple = same_priority_address[0]
            next_vertex = graph.get_vertex(address_dict.get(next_priority_address_tuple[1]))
            shortest_path = graph.get_shortest_path(truck.current_location, next_vertex)
            graph.reset_adjacency_list()

        # Remove the address with the shortest distance from the list.
        # Add the remaining addresses back to the PriorityQueue.
        same_priority_address.remove(next_priority_address_tuple)
        if len(same_priority_address) >= 1:
            for priority_address_tuple in same_priority_address:
                truck_pkg_priority_queue.put((priority_address_tuple[0], priority_address_tuple[1]))
        same_priority_address.clear()

        # Iterate through shortest_path[] to add list of packages to each destination along the path.
        for path_index in range(len(shortest_path)):
            # Skip the first departure address in path
            if 0 < path_index < len(shortest_path):
                # Get the (addressId, distance, [packages]) tuple
                addressId_dist_packages_tuple = shortest_path[path_index]
                # Get the Address object
                address = list(address_dict.keys())[addressId_dist_packages_tuple[0] - 1]
                # If intermediate address has packages that needs to be delivered by this truck,
                # pop this address from the queue.
                # Append the list of packages previously loaded onto truck to the [packages].
                # Remove packages from truck -> reserved_pkg{}
                if address in truck.reserved_pkg.keys():
                    if path_index < len(shortest_path) - 1:
                        pop_item_from_queue(address, truck_pkg_priority_queue)
                    addressId_dist_packages_tuple[2].extend(truck.reserved_pkg.pop(address))

                    # Get the destination vertex value
                    next_vertex = graph.get_vertex(addressId_dist_packages_tuple[0])

                    # Calculate arrival time
                    dt = datetime.combine(date.today(), truck.departure) + timedelta(minutes=int(shortest_path[path_index][1] / SPEED * 60))
                    arrival = dt.time()

                    # Create a new Route object and add to truck -> routes {}
                    route = Route(truck.current_location, next_vertex, truck.departure, arrival, shortest_path[path_index][1])
                    truck.add_route(route, shortest_path)

                    # Output new route to CSV file
                    output_pkg_loading(addressId_dist_packages_tuple[2], truck, address, arrival)

                    # Reset truck -> location and truck -> departure.
                    # Recalculate truck -> total_miles
                    truck.current_location = next_vertex
                    truck.departure = arrival
                    truck.total_miles += route.miles

    # If truck has finished all deliveries, send it back to HUB.
    # Recalculate truck -> departure.
    next_vertex = graph.get_vertex(1)
    shortest_path = graph.get_shortest_path(truck.current_location, next_vertex)
    dt = datetime.combine(date.today(), truck.departure) + timedelta(
        minutes=int(shortest_path[len(shortest_path) - 1][1] / SPEED * 60))
    arrival = dt.time()
    # Create a new Route object and add to truck -> routes {}
    route = Route(truck.current_location, next_vertex, truck.departure, arrival, shortest_path[len(shortest_path) - 1][1])
    truck.add_route(route, shortest_path)
    # Reset truck -> location and truck -> departure.
    # Recalculate truck -> total_miles
    truck.current_location = next_vertex
    truck.departure = arrival
    truck.total_miles += route.miles


# This function simulate truck delivery based on the created delivery routes and the input time.
# The active route will be printed to the console.
def simulate_delivery_routes(current_time):

    delivered_all_packages = False

    # For each truck's delivery routes, print the route that falls between the input time.
    for truck in trucks:
        route_list = list(truck.routes.keys())
        first_route = route_list[0]
        if first_route.departure <= current_time:
            for route in list(truck.routes.keys()):
                # Select the active route.
                if route.departure <= current_time <= route.arrival:

                    # List of all destination in the active route
                    path = truck.routes.get(route)

                    for path_index in range(len(path)):

                        # Output print for vertex departure
                        if path_index == 0:
                            departure_address = list(address_dict.keys())[path[path_index][0] - 1]
                            print("Truck %d departed %s at %s." % (truck.id, departure_address, route.departure))
                            print('')

                        # Output print for package delivery at each destination
                        else:
                            package_list = path[path_index][2]
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

                    delivered_all_packages = False
                    break

                else:
                    delivered_all_packages = True

            if delivered_all_packages:
                print("All packages have been delivered by Truck %d." %(truck.id))
            print('====================================================================')


# This functions prompts user to input a new time and validate user input before returning the valid time.
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


def remove_package(package_to_remove, affected_truck):
    # Remove pkg from pkg_dict and pkg_hash_table
    pkg_hash_table.remove(package_to_remove)
    for package in affected_truck.reserved_pkg.get(package_to_remove.address):
        if package == package_to_remove:
            package_list = affected_truck.reserved_pkg.get(package_to_remove.address)
            if len(package_list) > 1:
                package_list.remove(package_to_remove)
            else:
                affected_truck.reserved_pkg.pop(package_to_remove.address)


# This function prints the main menu to the console
def print_main_menu():
    print("Menu:")
    print("\t1. Start delivery")
    print("\t2. Change current time")
    print("\t3. Check package status")
    print("\t4. Update package")
    print("\t5. Exit")


# This function print package's status to the console
def print_package_status(package, current_time):
    # Convert delivery deadline for console output
    if package.deadline == time(23, 0, 0):
        converted_deadline = 'EOD'
    else:
        converted_deadline = package.deadline

    # Output package's status to console
    print("======================================================================================")
    print("Package Number: " + str(package.pkg_id), end='\t')
    print("Weight: " + str(package.weight), end='\t')
    print("Delivery Deadline: " + str(converted_deadline), end='\t')
    if current_time >= package.delivered_time:
        print("Current Status: %s at %s" % (package.status, package.delivered_time), end='\t')
    else:
        print("Current Status: " + package.status, end='\t')
    print("Delivery Address: ", end='\t')
    print(package.address)


# This function output delivery for ALL packages to a CSV file
def output_package_status(package, current_time):

    # Convert delivery deadline for console output
    if package.deadline == time(23, 0, 0):
        converted_deadline = 'EOD'
    else:
        converted_deadline = package.deadline

    pkg_status_file = open('package_status.csv', 'a')
    pkg_status_file.seek(0, 2)
    wr = csv.DictWriter(pkg_status_file, fieldnames=status_fields, lineterminator='\n')
    if current_time >= package.delivered_time:
        wr.writerow({'PackageID': package.pkg_id, 'Weight': package.weight, 'Delivery Deadline': converted_deadline, 'Current Status': package.status + " at " + str(package.delivered_time), 'Delivery Address': package.address})
    else:
        wr.writerow({'PackageID': package.pkg_id, 'Weight': package.weight, 'Delivery Deadline': converted_deadline, 'Current Status': package.status, 'Delivery Address': package.address})

    pkg_status_file.close()


# This function sets initial departure time for each truck
def set_up_trucks():
    trucks[0].departure = time(9, 5, 0)
    trucks[0].pickup_time = time(9, 5, 0)

    trucks[1].departure = time(8, 0, 0)
    trucks[1].pickup_time = time(8, 0, 0)

    trucks[2].departure = truck3_departure
    trucks[2].pickup_time = truck3_departure

    for truck in trucks:
        truck.current_location = hub_vertex


if __name__ == "__main__":
    # Set up output file for package loading
    # Data including package, truck carrier, delivery address and delivered time  are output into
    # a csv file named "packaged_loading.csv"
    pkg_loading_file = open('package_loading.csv', 'w')
    pkg_fields = ('PackageID', 'Truck', 'Delivery Address', 'Delivered Time')
    pkg_wr = csv.DictWriter(pkg_loading_file, fieldnames=pkg_fields, lineterminator='\n')
    pkg_wr.writeheader()
    pkg_loading_file.close()

    # Load data from distance table and save them into an undirected graph
    dist_filename = "distance_table.csv"
    # Get the address at HUB
    hub_address = load_graph(dist_filename)
    hub_vertex = graph.get_vertex(address_dict.get(hub_address))

    # test_address = list(address_dict.keys())[3]
    # test_vertex = graph.get_vertex(address_dict.get(test_address))
    #
    # path = graph.get_shortest_path(hub_vertex, test_vertex)
    # # Clear shortest path calculation
    # for vertex in vertex_list:
    #     vertex.distance = float('inf')
    #     vertex.pred_vertex = None

    # Create trucks
    i = 1
    while i < 4:
        truck = Truck(i)
        trucks.append(truck)
        i += 1

    # Set Truck 1's departure to 9:05 AM and Truck 2's departure to 8 AM
    # Add trucks to HUB location in graph
    set_up_trucks()

    # Load data for packages and save them into the global pkg_dict{} dictionary
    pkg_filename = "package_data.csv"
    load_pkg_data(pkg_filename)
    print('')
    print("Loaded packages on each truck is output to package_loadng.csv file")

    # Create the chaining hash table using data from pkg_dict{} dictionary.
    create_hash_table()

    # Load packages with pre-determined truck to truck -> reserved_pkg[] list
    add_pkg_with_preset_truck()

    # Create a PriorityQueue to prioritize package delivery using data from pkg_dict{}.
    prioritize_pkg_dict(pkg_dict)

    # Load the remaining packages in pkg_dict {} onto the corresponding truck
    load_remaining_packages()

    # Create delivery routes and add to truck -> routes {} for Truck 1 and Truck 2 first.
    for truck_index in range(len(trucks)):
        if truck_index < 2:
            create_delivery_route(trucks[truck_index])

    # Determine which driver finished first and assign Truck 3 to that driver.
    if trucks[0].departure < trucks[1].departure:
        trucks[2].departure = trucks[0].departure
        trucks[2].pickup_time = trucks[0].departure
        truck3_departure = trucks[0].departure
        truck3_driver = 'Truck 1'
    else:
        trucks[2].departure = trucks[1].departure
        trucks[2].pickup_time = trucks[1].departure
        truck3_departure = trucks[1].departure
        truck3_driver = 'Truck 2'

    # Once driver has been assigned, start loading packages onto Truck 3.
    create_delivery_route(trucks[2])

    # Output truck -> routes{} to CSV file.
    output_truck_routes(truck3_driver)

    # Once delivery routes have been established, reset truck's current location and departure for
    # delivery simulation
    set_up_trucks()

    # Delivery simulation and UI
    user_selection = 1

    while not user_selection == 5:
        print_main_menu()
        user_selection = input("Select a number from 1-5 from the menu above: ")

        # User-input validation
        valid_selection = False
        while not valid_selection:
            if not user_selection.isnumeric():
                user_selection = input("Invalid selection. Enter a number from 1 - 4: ")
            elif int(user_selection) < 1 or int(user_selection) > 5:
                user_selection = input("Invalid selection. Enter a number from 1 - 4: ")
            else:
                user_selection = int(user_selection)
                valid_selection = True

        # Simulate a delivery route
        if user_selection == 1:
            current_time = time(8, 0, 0)
            print('')
            print("The current time is:\t" + current_time.strftime('%H: %M'))
            print('')
            simulate_delivery_routes(current_time)

        # Change current time and simulate delivery route at the new time
        if user_selection == 2:
            prompt = "Enter a new time (HH:MM): "
            current_time = get_new_time(prompt)

            # Update package's status and truck's current location and departure
            update_pkg_status(current_time)
            update_truck_routes(current_time, None)

            # Simulate and output active delivery route
            simulate_delivery_routes(current_time)

        # Display package status to the console
        if user_selection == 3:

            # Prompt user to set a time
            prompt = "Enter a new time (HH:MM): "
            current_time = get_new_time(prompt)

            # Update packages' status and truck's current location and departure time
            update_pkg_status(current_time)
            update_truck_routes(current_time, None)

            # Prompt user to select printing status for all or a specific package
            option = input("Would you like to display delivery status for all packages? (Y/N): ")

            # Print status for all packages
            if option.capitalize() == 'Y':
                pkg_status_file = open('package_status.csv', 'w')
                status_fields = ('PackageID', 'Weight', 'Delivery Deadline', 'Current Status', 'Delivery Address')
                status_wr = csv.DictWriter(pkg_status_file, fieldnames=status_fields, lineterminator='\n')
                status_wr.writeheader()
                pkg_status_file.close()

                print('')
                print("Results are output to the package_status.csv file")
                print('')
                for bucket in pkg_hash_table.table:
                    for package in bucket:
                        output_package_status(package, current_time)

            # Prompt user for a specific package and print status for the matching package
            elif option.capitalize() == 'N':

                # Prompt user to input the package of interest
                pkg_to_search = get_user_input()
                # Get the matched package from hash table
                pkg_found = pkg_hash_table.search(pkg_to_search)
                print_package_status(pkg_found, current_time)

        # Update package requirement and recalculate delivery routes
        if user_selection == 4:

            # Prompt user for a new time
            prompt = "Enter a new time (HH:MM): "
            current_time = get_new_time(prompt)

            # Prompt user to input the package of interest
            pkg_to_update = get_user_input()
            # Get the matched package from hash table
            pkg_found = pkg_hash_table.search(pkg_to_update)

            if pkg_found is not None:

                # Get the truck carrying the package
                affected_truck = pkg_found.truck

                # Update packages' status and truck's current location and departure time
                update_pkg_status(current_time)
                update_truck_routes(current_time, affected_truck)

                # Output to console if package has been delivered and therefore can't be modified.
                if pkg_found.status == 'Delivered':
                    print('')
                    print("Package has been delivered")
                    print('')

                # Else if package has not been delivered, prompt user for additional options.
                else:
                    print("Choose an option below to modify delivery requirements")
                    print("Menu:")
                    print("\t1. Change delivery address")
                    print("\t2. Change delivery deadline")
                    print("\t3. Go back")

                    # Update package's delivery address and recalculate delivery routes for the
                    # affected truck.
                    user_selection2 = 1

                    while not int(user_selection2) == 3:
                        user_selection2 = input("Select a number from 1-3 from the menu above: ")

                        # User-input validation
                        valid_selection = False
                        while not valid_selection:
                            if not user_selection2.isnumeric():
                                user_selection2 = input("Invalid selection. Enter a number from 1 - 3: ")
                            elif int(user_selection2) < 1 or int(user_selection2) > 3:
                                user_selection2 = input("Invalid selection. Enter a number from 1 - 3: ")
                            else:
                                user_selection2 = int(user_selection2)
                                valid_selection = True

                        if 1 <= user_selection2 <= 2:

                            # Prompt user for the new address.
                            # Remove current package from pkg_dict{} and hash table.
                            # Update package's address.
                            if user_selection2 == 1:
                                new_street = input("Enter a street address: ")
                                new_city = input("Enter a new city: ")
                                new_zipCode = input("Enter a new zip code: ")
                                new_state = input("Enter a new state: ")

                                # new_street = '410 S State St'
                                # new_city = 'Salt Lake City'
                                # new_zipCode = '84111'
                                # new_state = 'UT'

                                new_address = Address(new_street, new_city, new_zipCode, new_state)
                                # Get address from address_dict{}
                                new_address = list(address_dict.keys())[address_dict.get(new_address)-1]

                                # Remove pkg from pkg_hash_table and affected_truck -> reserved_pkg{}
                                remove_package(pkg_found, affected_truck)

                                # Update package's address
                                pkg_found.address = new_address

                            # Prompt user for the new delivery deadline
                            # Remove current package from pkg_dict{} and hash table.
                            # Update package's delivery deadline.
                            elif user_selection2 == 2:
                                prompt = "Enter new delivery deadline: "
                                new_delivery_deadline = get_new_time(prompt)
                                remove_package(pkg_found, affected_truck)
                                pkg_found.deadline = new_delivery_deadline

                            # End of if-else for user-selection filter

                            # Add package back into hash_table and affected_truck -> reserved_pkg{}
                            pkg_hash_table.insert(pkg_found)
                            if pkg_found.address not in affected_truck.reserved_pkg.keys():
                                affected_truck.reserved_pkg[pkg_found.address] = [pkg_found]
                            else:
                                package_list = affected_truck.reserved_pkg.get(pkg_found.address)
                                package_list.append(pkg_found)

                            # Clear truck -> routes
                            affected_truck.routes.clear()

                            # Update affected_truck's delivery routes
                            create_delivery_route(affected_truck)

                            print("Delivery routes re-calculated")
                            # Output truck -> routes{} to CSV file.
                            output_truck_routes(truck3_driver)

                            # Update packages' status and truck's current location and departure time
                            update_pkg_status(current_time)
                            update_truck_routes(current_time, affected_truck)

                            break

                        else:
                            print_main_menu()

            else:
                print("Package does not exist.")
                print_main_menu()












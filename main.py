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
# Dictionary of packages that require pick-up later
# While downloading raw data from the csv file, packages that have a specific pick-up time
# requirements are temporarily added to this dictionary, which will be later added to pkg_dict{}
# after picked up at HUB
pickup_packages = {}
# Chaining Hash Table holding package data for easy status look-up
pkg_hash_table = ChainingHashTable()
# List of all trucks available at WGUPS
trucks = []

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
    selected_truck = trucks[0]
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
            if selected_truck == trucks[0]:
                selected_truck = trucks[1]
                if len(package_list) <= MAX_PKG_PER_TRUCK - selected_truck.total_packages:
                    add_packages_to_truck(selected_truck, address, package_list)
                # If the other truck still does not fit, load onto Truck 3
                else:
                    selected_truck = trucks[2]
                    add_packages_to_truck(selected_truck, address, package_list)

        # Alternate truck
        if trucks[0].total_packages < MAX_PKG_PER_TRUCK and trucks[1].total_packages < MAX_PKG_PER_TRUCK:
            if selected_truck == trucks[0]:
                selected_truck = trucks[1]
            elif selected_truck == trucks[1]:
                selected_truck = trucks[0]
            elif selected_truck == trucks[2]:
                selected_truck = trucks[0]
        elif trucks[0].total_packages < MAX_PKG_PER_TRUCK:
            if selected_truck == trucks[2]:
                selected_truck = trucks[0]
            else:
                selected_truck = trucks[0]
        elif trucks[1].total_packages < MAX_PKG_PER_TRUCK:
            if selected_truck == trucks[2]:
                selected_truck = trucks[1]
            else:
                selected_truck = trucks[1]
        else:
            selected_truck = trucks[2]


# This function is similar to the add_package_to_pkg_dict() function, except for it iterate through
# a created pkg_dict{} dictionary instead of creating new Package objects and add to dictionary.
# The intent is to re-create the deadline_set and same_route_set_list[] data structure for the selected
# pkg_dict{}, which is later used in update_delivery_routes().
def update_pkg_dict():
    # Clear previous data structure
    deadline_set.clear()
    same_route_set_list.clear()
    packages_to_remove = []

    for package_list in pkg_dict.values():
        for package in package_list:

            # Re-create deadline_set
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
            # if package.address == hub_address:
            #     # Find the actual package
            #     for package_list2 in pkg_dict.values():
            #         for package2 in package_list2:
            #             if package2.pkg_id == package.pkg_id and not package2.address == hub_address:
            #                 delivered_package = package2
            #                 packages_to_remove.append(delivered_package)
            #
            #                 # Add delivery package to pickup_packages{} for delivery after pickup
            #                 if delivered_package.address not in pickup_packages.keys():
            #                     pickup_packages[delivered_package.address] = [delivered_package]
            #                 else:
            #                     pkg_list2 = pickup_packages.get(delivered_package.address)
            #                     pkg_list2.append(delivered_package)

    # Remove packages with actual delivery address that have been transferred to pickup_packages{} from
    # pkg_dict{}
    # for package in packages_to_remove:
    #     package_list = pkg_dict.get(package.address)
    #     if len(package_list) > 1:
    #         package_list.remove(package)
    #     else:
    #         pkg_dict.pop(package.address)


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
def prioritize_pkg_dict():

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
    for key in pkg_dict.keys():

        package_list = pkg_dict.get(key)
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
    print('')
    print("Delivery routes for each truck is output to routes.csv file")
    print('=========================================================================================')
    truck_route = open('routes.csv', 'w')

    truck_fields = ('Truck', 'Departure', 'Departure Time', 'Arrival', 'Arrival Time', 'Route', 'Package(s) Delivered')
    truck_wr = csv.DictWriter(truck_route, fieldnames=truck_fields, lineterminator='\n')

    truck_wr.writeheader()
    truck_route.seek(0, 2)
    wr = csv.DictWriter(truck_route, fieldnames=truck_fields, lineterminator='\n')

    for truck in trucks:
        print("Total packages packages delivered by Truck %d is %d packages." %(truck.id, truck.total_packages))
        print("Total mileage traveled by Truck %d is %.2f miles." %(truck.id, truck.total_miles))
        print('')
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
    # input_parameters = ['27', '1060 Dalton Ave S', 'Salt Lake City', '84104', 'UT', 'EOD', '5']
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


# This function update truck's current location and departure time based on the input current time.
def update_truck_routes(current_time):
    for truck in trucks:
        truck.total_miles = 0
        for route in truck.routes.keys():
            # Re-set truck's departure and current location to the route that falls between
            # the current time.
            if route.departure <= current_time <= route.arrival:
                truck.departure = route.arrival
                truck.current_location = route.end_vertex
                truck.total_miles += route.miles
            elif route.arrival < current_time:
                truck.total_miles += route.miles


# This function iterates through the PriorityQueue and loads packages onto truck based on user's
# requirements and truck's availability.
def create_delivery_route():

    # Update truck's availability based on user's specified carrier truck requirement.
    # Iterate through the entire pkg_dict{}.
    for address_key in pkg_dict.keys():

        required_truck = None
        pkg_list = pkg_dict.get(address_key)

        # For each package in the list of all packages with the same delivery address, if package has a
        # specific carrier truck requirement:
        #       set required_truck to that truck, set carrier truck of all
        #       packages in the list to the same truck
        #       append those packages to truck -> reserved_pkg[] list
        #       pre-increment the total_packages count.
        # NOTE: reserved_pkg[] and pre-incrementing of total_packages are implemented to prevent truck
        # overloading.
        for package in pkg_list:
            if package.truck is not None:
                for truck in trucks:
                    if truck.id == package.truck:
                        required_truck = truck
                        break
        if required_truck is not None:
            for package in pkg_list:
                package.truck = required_truck.id
                required_truck.reserved_pkg.append(package.pkg_id)
                required_truck.total_packages += 1

    # Used as a flag that package loading is completed in order to break from the while loop.
    finished = False

    # Iterate through the PriorityQueue until empty
    while not dest_priority_queue.empty():
        total_packages = 0
        required_truck_id = None
        required_truck = None
        # List of all delivery addresses/destinations in this route, which may include intermidiate
        # destinations as a result of shortest path optimization and meeting the requirement for packages
        # that are to be delivered together in the same route.
        dest_in_route = []

        # Pop the next address from queue
        next_address = dest_priority_queue.get()

        # If package has been delivered (address NOT in pkg_dic{}), keep popping.
        # If the queue is empty, switch "finished" flag to True to exit the while loop.
        while next_address[1] not in pkg_dict.keys():
            if not dest_priority_queue.empty():
                next_address = dest_priority_queue.get()
            else:
                finished = True
                break

        # Once a valid delivery address has been selected and if queue is not empty
        if not finished:

            # Append the delivery address to dest_in_route[] list.
            dest_in_route.append(next_address[1])

            # If delivery address (id) is an element of the list of sets of destinations that are to be
            # in the same truck's routes, append the delivery address in the set to dest_in_route[].
            for same_route_set in same_route_combined_sets:
                if next_address[1] in same_route_set:
                    for item in same_route_set:
                        if not item == next_address[1]:
                            dest_in_route.append(item)
                    break

            # Now that the list of all delivery addresses that must be included in this route is
            # established, gather all the packages at each destination.
            # If a truck still has not been selected by this time, check if any of the package has a
            # specific truck requirement and set required_truck_id accordingly.
            # If package does not have specific truck requirement,
            # increment the total_packages, which is used for optimal truck selection.
            for address_key in dest_in_route:
                if address_key in pkg_dict.keys():
                    packages_to_deliver = pkg_dict.get(address_key)
                    if required_truck_id is None:
                        for package in packages_to_deliver:
                            if package.truck is not None:
                                required_truck_id = package.truck
                                break
                    # If package does not have a requirement for specific truck, then do NOT add to total packages
                    if required_truck_id is None:
                        total_packages += len(packages_to_deliver)

            # If a truck has been determine after the for-loop above, set package -> truck for all packages in dest_in_route.
            if required_truck_id is not None:
                for address_key in dest_in_route:
                    if address_key in pkg_dict.keys():
                        packages_to_deliver = pkg_dict.get(address_key)
                        for package in packages_to_deliver:
                            package.truck = required_truck_id
                            if not package.pkg_id in trucks[required_truck_id - 1].reserved_pkg:
                                trucks[required_truck_id - 1].total_packages += 1

            # By this time, if the carrier truck still has not been selected, select the optimal truck
            # by choosing the one with less total of packages up to this point.
            if required_truck_id is None:
                # For each truck that has driver, if the truck can carry the additional
                # total packages, add it to the available_trucks[] list
                # If the available_trucks list is not empty, select the truck with less
                # total packages
                # Else if the list is empty, select the back-up truck.

                # List of candidate trucks
                available_trucks = []

                for truck in trucks:
                    # If truck has a driver and total_packages has not exceeded to maximum allowance,
                    # append truck to available_trucks[]
                    if truck.driver is not None and total_packages <= MAX_PKG_PER_TRUCK - truck.total_packages:
                        available_trucks.append(truck)

                # If the list of candidate trucks is not empty, choose the truck with less total_packages
                if len(available_trucks) > 0:
                    min_pkg_truck = available_trucks[0]
                    for truck in available_trucks:
                        if truck.total_packages < min_pkg_truck.total_packages:
                            min_pkg_truck = truck
                    required_truck = min_pkg_truck

                # Else if none of the active truck is available, choose the back-up with no driver
                else:
                    if trucks[2].driver is not None:
                        required_truck = trucks[2]


            # Else if required_truck_id has been determined from the above algorithm, set required_truck
            else:
                for truck in trucks:
                    if truck.id == required_truck_id:
                        required_truck = truck
                        break

            # Start loading packages for this route.
            for address_key in dest_in_route:

                if address_key in pkg_dict.keys():
                    # Keep track of additional packages loaded to trucks that are not part of
                    # truck -> reserved_pkg[] determined from above
                    packages_per_route = 0

                    # Get the list of all packages at the delivery address
                    packages_to_deliver = pkg_dict.get(address_key)

                    # Calculate total packages for each route
                    for pkg in packages_to_deliver:
                        # If package does NOT have specific truck requirement, increment
                        # packages_per_route
                        if pkg.truck is None:
                            packages_per_route += 1

                        # Else if package is part of truck -> reserved_pkg[] determined earlier,
                        # remove it from reserved_pkg[]
                        else:
                            index_to_remove = []
                            for index in range(len(required_truck.reserved_pkg)):
                                if required_truck.reserved_pkg[index] == pkg.pkg_id:
                                    index_to_remove.append(index)
                                    break
                            for index in index_to_remove:
                                required_truck.reserved_pkg.pop(index)

                    required_truck.total_packages += packages_per_route

                    # Get to_vertex from graph using address_id
                    address_id = address_dict.get(address_key)
                    to_vertex = graph.get_vertex(address_id)

                    # Get shortest path and calculate arrival time
                    path = graph.get_shortest_path(required_truck.current_location, to_vertex)
                    # Add packages_to_deliver to path's destination (to_vertex)
                    path[len(path) - 1][1].extend(packages_to_deliver)

                    # If path contains intermediate destinations, determine if additional packages
                    # can be picked up from each intermidiate destination.
                    if len(path) > 2:
                        sub_route_departure = required_truck.departure
                        # Start with the second address_id and ignore the first and last
                        for index in range(len(path)):
                            if 0 < index < len(path) - 1:
                                destination_address = list(address_dict.keys())[list(address_dict.values()).index(path[index][0])]

                                # If destination address has packages to deliver and is not HUB,
                                # pick up the packages.
                                # Avoiding picking up packages at HUB to simplify this algorithm.
                                # if destination_address in pkg_dict.keys() and not destination_address == hub_address:
                                if destination_address in pkg_dict.keys():
                                    pkg_list = pkg_dict.get(destination_address)
                                    if len(pkg_list) <= MAX_PKG_PER_TRUCK - truck.total_packages:
                                        # Distance is the total distance from path[0][1]
                                        sub_route_distance = graph.get_vertex(path[index][0]).distance
                                        dt = datetime.combine(date.today(), sub_route_departure) + timedelta(minutes=int(sub_route_distance / SPEED * 60))
                                        arrival = dt.time()

                                        print_pkg_loading(pkg_list, required_truck, destination_address, arrival)

                                        pkg_dict.pop(destination_address)
                                        required_truck.total_packages += len(pkg_list)
                                        path[index][1].extend(pkg_list)
                                        index += 1
                    # End of sub-route if statement

                    # Calculate arrival time
                    distance = to_vertex.distance
                    dt = datetime.combine(date.today(), required_truck.departure) + timedelta(
                        minutes=int(distance / SPEED * 60))
                    arrival = dt.time()

                    # Create new route and add to required_truck -> routes{}
                    # Update total_packages for required_truck
                    route = Route(required_truck.current_location, to_vertex, required_truck.departure, arrival, distance)
                    required_truck.total_miles += distance
                    required_truck.add_route(route, path)

                    # Clear shortest path calculation
                    for vertex in vertex_list:
                        vertex.distance = float('inf')
                        vertex.pred_vertex = None

                    # Else if delivery address is not at HUB, simply output to csv file.
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

                        # Calculate shortest path and time when truck arrives at HUB
                        hub_vertex = graph.get_vertex(1)
                        path = graph.get_shortest_path(required_truck.current_location, hub_vertex)
                        distance = hub_vertex.distance
                        dt = datetime.combine(date.today(), required_truck.departure) + timedelta(
                            minutes=int(distance / SPEED * 60))
                        arrival = dt.time()

                        # Create new route and add to required_truck -> routes{}
                        # Update total_packages for required_truck
                        route = Route(from_vertex, hub_vertex, required_truck.departure, arrival, distance)
                        required_truck.add_route(route, path)
                        required_truck.total_miles += distance
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

                        # Driver of the back-up truck
                        driver = None

                        # Set driver of the back-up to the first truck that this code of block is
                        # executed (earliest arrival).
                        # However, packages will not be loaded onto back-up truck until all active trucks
                        # have completed their routes.
                        for truck in trucks:
                            if truck.departure is None:
                                truck.departure = required_truck.departure
                                truck.pickup_time = required_truck.departure
                                driver = required_truck.id
                                print("Driver from Truck %d will be delivering packages from Truck %d" % (required_truck.id, truck.id))
                        print('')
                        print('*************************************************************')

                        # If all trucks with driver have delivered all packages, set mission_completed
                        # to True and switch back-up truck -> has_driver to True. Packages can then be
                        # loaded onto back-up truck.
                        mission_completed = False
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

    # Output routes to the csv file.
    output_truck_routes()


# This function is very similar to the create_delivery_route() function above. The only difference is
# that it create delivery route for a specific truck only.
def update_delivery_route(truck):

    # Used as a flag that package loading is completed in order to break from the while loop.
    finished = False

    # Iterate through the PriorityQueue until empty
    while not dest_priority_queue.empty():
        # List of all delivery addresses/destinations in this route, which may include intermidiate
        # destinations as a result of shortest path optimization and meeting the requirement for packages
        # that are to be delivered together in the same route.
        dest_in_route = []

        # Pop the next address from queue
        next_address = dest_priority_queue.get()

        # If package has been delivered (address NOT in pkg_dic{}), keep popping.
        # If the queue is empty, switch "finished" flag to True to exit the while loop.
        while next_address[1] not in pkg_dict.keys():
            if not dest_priority_queue.empty():
                next_address = dest_priority_queue.get()
            else:
                finished = True
                break

        # Once a valid delivery address has been selected and if queue is not empty
        if not finished:

            # If delivery address is at HUB, sort the list of packages at HUB by deadline and set the
            # latest_pickup_time to the deadline of the last package in the list.
            # The lastest_pickup_time is used to determine if the packages are ready for pick-up or not.
            if next_address[1] == hub_address:
                pickup_package_list = pkg_dict.get(next_address[1])
                latest_pickup_time = pickup_package_list[len(pickup_package_list) - 1].deadline

                # if departure time for either truck 1 or truck 2 is less than pick_up time
                # continue loading other packages first
                # else if both trucks are ready for pick-up
                # select the truck with the less number of packages
                # Get to_vertex from graph using address_id

                # Get the address_id for the delivery address in order to get the vertex from graph
                next_address_id = None
                for address, id_value in address_dict.items():
                    if address == next_address[1]:
                        next_address_id = id_value
                        break
                to_vertex = graph.get_vertex(next_address_id)

                # Calculate arrival time at HUB if departed from current location now
                path = graph.get_shortest_path(truck.current_location, to_vertex)
                distance = to_vertex.distance
                dt = datetime.combine(date.today(), truck.departure) + timedelta(minutes=int(distance / SPEED * 60))
                arrival = dt.time()

                # If arrival time is before pickup_time:
                #   save the HUB address to hold_address_tuple
                #   pop the next address in queue
                #   insert the hold HUB address back into queue
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

            # Append the delivery address to dest_in_route[] list.
            dest_in_route.append(next_address[1])

            # If delivery address (id) is an element of the list of sets of destinations that are to be
            # in the same truck's routes, append the delivery address in the set to dest_in_route[].
            for same_route_set in same_route_combined_sets:
                if next_address[1] in same_route_set:
                    for item in same_route_set:
                        if not item == next_address[1]:
                            dest_in_route.append(item)
                    break

            # Now that the list of all delivery addresses that must be included in this route is
            # established, gather all the packages at each destination.
            for address_key in dest_in_route:
                if address_key in pkg_dict.keys():

                    # Get the list of all packages at the delivery address
                    packages_to_deliver = pkg_dict.get(address_key)

                    # Get to_vertex from graph using address_id
                    address_id = address_dict.get(address_key)
                    to_vertex = graph.get_vertex(address_id)
                    # Get shortest path and calculate arrival time
                    path = graph.get_shortest_path(truck.current_location, to_vertex)
                    # Add packages_to_deliver to path's destination
                    path[len(path) - 1][1].extend(packages_to_deliver)

                    # If path contains intermediate destinations, determine if additional packages
                    # can be picked up from each intermidiate destination.
                    if len(path) > 2:
                        sub_route_departure = truck.departure
                        # Start with the second address_id and ignore the first and last
                        for index in range(len(path)):
                            if 0 < index < len(path) - 1:
                                destination_address = list(address_dict.keys())[list(address_dict.values()).index(path[index][0])]

                                # If destination address has packages to deliver and is not HUB,
                                # pick up the packages.
                                # Avoiding picking up packages at HUB to simplify this algorithm.
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
                    route = Route(truck.current_location, to_vertex, truck.departure, arrival, distance)
                    truck.add_route(route, path)
                    truck.total_miles += distance
                    # truck.total_packages += packages_per_route

                    # Clear shortest path calculation
                    for vertex in vertex_list:
                        vertex.distance = float('inf')
                        vertex.pred_vertex = None

                    # If delivery destination is at HUB, transfer packages saved in pickup_packages[]
                    # earlier and re-prioritize the queue.
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

                    # Else if delivery address is not at HUB, simply output to csv file.
                    else:
                        print_pkg_loading(packages_to_deliver, truck, address_key, arrival)

                    # Update departure, start location for next route, truck's location,
                    # and remove delivered destination from pkg_dict
                    truck.departure = arrival
                    from_vertex = to_vertex
                    truck.current_location = to_vertex
                    pkg_dict.pop(address_key)

    # After all packages have been delivered, send truck back to HUB.
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

    # Used for testing shortest path calculation
    # test_address = list(address_dict.keys())[10]
    # test_vertex = graph.get_vertex(address_dict.get(test_address))
    # path = graph.get_shortest_path(hub_vertex, test_vertex)

    # Create trucks and add trucks to HUB location in graph
    # Add drivers to Truck 1 and Truck 2
    # Set Truck 1's departure to 9:05 AM and Truck 2's departure to 8 AM
    i = 1
    while i < 4:
        truck = Truck(i)
        # Add driver to Truck 1 and 2
        if i < 3:
            truck.driver = i
        if i == 1:
            truck.departure = time(9, 5, 0)
            truck.pickup_time = time(9, 5, 0)
        elif i == 2:
            truck.departure = time(8, 0, 0)
            truck.pickup_time = time(8, 0, 0)
        truck.current_location = hub_vertex
        trucks.append(truck)
        i += 1

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
    prioritize_pkg_dict()

    # Load the remaining packages in pkg_dict {} onto the corresponding truck
    load_remaining_packages()

    # Pop delivery address_id from the created PriorityQueue one at a time.
    # For each address_id, gather the list of packages and start loading them onto trucks.
    create_delivery_route()

    # Once delivery routes have been established, reset truck's current location and departure for
    # delivery simulation
    for truck in trucks:
        truck.current_location = graph.get_vertex(address_dict.get(hub_address))
        truck.departure = time(8, 0, 0)

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
            update_truck_routes(current_time)

            # Simulate and output active delivery route
            simulate_delivery_routes(current_time)

        # Display package status to the console
        if user_selection == 3:

            # Output current time, which is default to 8 AM
            # current_time = time(8, 0, 0)
            # print('')
            # print("The current time is:\t" + current_time.strftime('%H: %M'))
            # print('')

            # Prompt user to set a time
            prompt = "Enter a new time (HH:MM): "
            current_time = get_new_time(prompt)

            # Update packages' status and truck's current location and departure time
            update_pkg_status(current_time)
            update_truck_routes(current_time)

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

            # Update packages' status and truck's current location and departure time
            update_pkg_status(current_time)
            update_truck_routes(current_time)

            # Prompt user to input the package of interest
            pkg_to_update = get_user_input()

            # Get the truck carrying the package
            affected_truck = None
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

            # Iterate through the truck's routes and add all packages that have not been delivered
            # to pkg_dict{}
            for route in affected_truck.routes.keys():
                for dest_pkg_tuple in affected_truck.routes.get(route):
                    if len(dest_pkg_tuple[1]) > 0:
                        for package in dest_pkg_tuple[1]:
                            if not package.status == 'Delivered':
                                # Lock in delivery truck
                                package.truck = affected_truck.id
                                if package.address not in pkg_dict.keys():
                                    pkg_dict[package.address] = [package]
                                else:
                                    package_list = pkg_dict.get(package.address)
                                    package_list.append(package)

            # Check if the package input by user exists in the hash table.
            if pkg_hash_table.search(pkg_to_update) is not None:

                pkg_to_update = pkg_hash_table.search(pkg_to_update)

                # Output to console if package has been delivered and therefore can't be modified.
                if pkg_to_update.status == 'Delivered':
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
                    user_selection = 1

                    while not int(user_selection) == 3:
                        user_selection = input("Select a number from 1-3 from the menu above: ")

                        # User-input validation
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

                            # Prompt user for the new address.
                            # Remove current package from pkg_dict{} and hash table.
                            # Update package's address.
                            if user_selection == 1:
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

                                # Remove pkg from pkg_dict and pkg_hash_table
                                remove_package(pkg_to_update)

                                # Update package's address
                                pkg_to_update.address = new_address

                            # Prompt user for the new delivery deadline
                            # Remove current package from pkg_dict{} and hash table.
                            # Update package's delivery deadline.
                            elif user_selection == 2:
                                prompt = "Enter new delivery deadline: "
                                new_delivery_deadline = get_new_time(prompt)
                                remove_package(pkg_to_update)
                                pkg_to_update.deadline = new_delivery_deadline

                            # End of if-else for user-selection filter

                            # Add package back into hash_table and pkg_dict
                            pkg_hash_table.insert(pkg_to_update)
                            if pkg_to_update.address not in pkg_dict.keys():
                                pkg_dict[pkg_to_update.address] = [pkg_to_update]
                            else:
                                package_list = pkg_dict.get(pkg_to_update.address)
                                package_list.append(pkg_to_update)

                            # Iterate through the truck's routes and set package -> truck to the
                            # affected_truck in order to lock it in.
                            for route in affected_truck.routes.keys():
                                for dest_pkg_tuple in affected_truck.routes.get(route):
                                    if len(dest_pkg_tuple[1]) > 0:
                                        for package in dest_pkg_tuple[1]:
                                            package.truck = affected_truck.id

                            # Update deadline_set and same_route_set_list[] for affected_truck's packages
                            update_pkg_dict()

                            # Clear truck's routes
                            affected_truck.routes.clear()
                            affected_truck.reserved_pkg.clear()
                            affected_truck.completed_all_routes = False

                            # Re-priortize affected_truck's packages
                            prioritize_pkg_dict()

                            # Update affected_truck's delivery routes
                            update_delivery_route(affected_truck)

                        else:
                            print_main_menu()












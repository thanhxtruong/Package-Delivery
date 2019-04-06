# Name: Thanh Truong. StudentID: #001062385

import csv
from package import Package
from datetime import time


def load_pkg_data(_filename):
    # Open file, read package data one line at a time skipping the first row (header).
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile)
        # Skip the header
        next(readCSV)
        for row in readCSV:
            print(row)
            package = Package(row[0], row[1], row[2], row[3], row[4], row[5])
            # Set delivery deadline
            if not (row[6] == 'EOD'):
                split_time = row[6].split(':')
                hour = int(split_time[0])
                # Split string again to remove 'AM'/'PM'
                minute = int(split_time[1].split(' ')[0])
                deadline = time(hour, minute, 0)
                package.add_delivery_deadline(deadline)

            # Set pickup time
            if not (row[7] == ' '):
                split_time = row[7].split(':')
                hour = int(split_time[0])
                # Split string again to remove 'AM'/'PM'
                minute = int(split_time[1].split(' ')[0])
                pickup_time = time(hour, minute, 0)
                package.set_pickup_time(pickup_time)

            # Set specific truck requirement
            if not (row[8] == ' '):
                package.set_truck(row[8])
                print(package.truck)


if __name__ == "__main__":
    filename = input("Enter name of package data file: ")
    load_pkg_data(filename)
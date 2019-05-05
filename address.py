# This class holds all data related to an address as downloaded from the csv file.
# The built-in functions are overridden to compare and hash using all attributes of
# the Address class.


class Address:
    def __init__(self, address, city, zip_code, state):
        self.address1 = address
        self.city = city
        self.zipCode = zip_code
        self.state = state

    def __str__(self):
        return str(self.address1 + '\n' + self.city + ', ' + self.state + ' ' + self.zipCode)

    def __eq__(self, other):
        if isinstance(other, Address):
            return self.address1 == other.address1 and self.city == other.city and self.zipCode == other.zipCode and self.state == other.state
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self):
        return hash((self.address1, self.city, self.zipCode, self.state))

    def __lt__(self, other):
        if isinstance(other, Address):
            return self.address1 < other.address1 and self.city < other.city and self.zipCode < other.zipCode and self.state < other.state
        else:
            return NotImplemented

    # Override greater than comparison to compare based on delivery deadline
    def __gt__(self, other):
        if isinstance(other, Address):
            return self.address1 > other.address1 and self.city > other.city and self.zipCode > other.zipCode and self.state > other.state
        else:
            return NotImplemented

    # This function returns True if the given state, zipCode, city, and address1
    # match values in the compared Address object
    def compare_address(self, address1, city, zipCode, state):
        if self.state == state and self.zipCode == zipCode and self.city == city and self.address1 == address1:
            return True
        else:
            return False


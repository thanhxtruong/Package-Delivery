class Address:
    def __init__(self, address, city, zip_code, state):
        self.address1 = address
        self.city = city
        self.zipCode = zip_code
        self.state = state

    def __str__(self):
        return self.address1

    # Override equality comparison to compare based on delivery deadline
    def __eq__(self, other):
        if isinstance(other, Address):
            return self.address1 == other.address1 and self.city == other.city and self.zipCode == other.zipCode and self.state == other.state
        else:
            return NotImplemented

    def __hash__(self):
        return hash((self.address1, self.city, self.zipCode, self.state))

    # This function returns true if the given state, zipCode, city, and address1
    # match values in the compared address object
    def compare_address(self, address1, city, zipCode, state):
        if self.state == state and self.zipCode == zipCode and self.city == city and self.address1 == address1:
            return True
        else:
            return False


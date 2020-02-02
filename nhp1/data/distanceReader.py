from nhp1.package.address import Address


# Class to read in the addresses from a csv file
class DistanceReader():
    # Constructor for the DistanceReader class
    def __init__(self, csv): # O(1)
        self.csv = csv
        self.addresses = []
        self.distance_matrix = []

    # Load the data from the csv file into the package list
    def load(self): # O(addresses^2)
        # Get all the data out of the csv file first
        distance_file_as_list = []
        with open(self.csv, 'r') as file:
            for line in file: # O(Addresses)
                if line == '': continue
                distance_file_as_list.append(line.split(';'))

        # Create a distance matrix of appropriate size
        self.distance_matrix = [[0.0 for x in range(len(distance_file_as_list))] for x in
                                range(len(distance_file_as_list))]

        # load addresses and distances
        for i, record in enumerate(distance_file_as_list): # O(Addresses^2)
            self.addresses.append(Address(record[0]))  # Loads the address as an Address object
            del record[0]
            for j, dist in enumerate(record): # O(addresses)
                if dist != '' and dist != '\n':
                    dist = float(dist.replace('\n', ''))
                    self.distance_matrix[i][j] = dist
                    self.distance_matrix[j][i] = dist

class Node:
    def __init__(self, id, x, y, is_critical=True):
        self.id = id
        self.x = x
        self.y = y
        self.is_critical = is_critical
        self.neighbors = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

class QuadrantMap:
    def __init__(self):
        # Dictionary to store the mapping of (xmin, xmax, ymin, ymax) to a string
        self.quadrant_dict = {}

    def _key(self, xmin, xmax, ymin, ymax):
        # Create a tuple key from the coordinates
        return (xmin, xmax, ymin, ymax)

    def add_quadrant(self, xmin, xmax, ymin, ymax, value):
        # Add a new quadrant with the associated string value
        key = self._key(xmin, xmax, ymin, ymax)
        self.quadrant_dict[key] = value

    def get_value_by_coordinate(self, x, y):
        # Retrieve the string value associated with the coordinates (x, y)
        for (xmin, xmax, ymin, ymax), value in self.quadrant_dict.items():
            if xmin <= x <= xmax and ymin <= y <= ymax:
                return value
        return None  # Return None if no quadrant contains the point

    def __str__(self):
        # String representation of the quadrant map
        return str(self.quadrant_dict)

    @staticmethod
    def for_mode(mode):
        if mode == "REGULAR":
            return QuadrantMap.for_regular_mode()
        elif mode == "SPEED":
            return QuadrantMap.for_speed_mode()
        else:
            raise ValueError(f"Invalid mode: {mode}")

    @staticmethod
    def for_regular_mode():
        quadrant_map = QuadrantMap()
        quadrant_map.add_quadrant(0, 100, 0, 100, "Quadrant 1")
        quadrant_map.add_quadrant(100, 200, 0, 100, "Quadrant 2")
        quadrant_map.add_quadrant(0, 100, 100, 200, "Quadrant 3")
        quadrant_map.add_quadrant(100, 200, 100, 200, "Quadrant 4")
        return quadrant_map

    @staticmethod
    def for_speed_mode():
        quadrant_map = QuadrantMap()
        quadrant_map.add_quadrant(0, 200, 0, 200, "Quadrant A")
        return quadrant_map

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
        # Xmin, Xmax, Ymin, Ymax
        quadrant_map = QuadrantMap()
        quadrant_map.add_quadrant(16.7, 17.46, 1.39, 2.53,
                                  {
                                      'name': "Curva 1",
                                      'data': {
                                          'possible_signs': ['crosswalk']
                                      }
                                  })

        quadrant_map.add_quadrant(16.25, 17.46, 3.3, 4.38,
                                  {
                                      'name': "Cruce BUS-MINIAUTOPISTA",
                                      'data': {
                                          'possible_signs': ['stop']
                                      }
                                  })
        quadrant_map.add_quadrant(15.86, 16.62, 8.64, 9.4,
                                  {
                                      'name': "Entrada Rotonda",
                                      'data': {
                                          'possible_signs': ['roundabout']
                                      }
                                  })

        quadrant_map.add_quadrant(15.52, 16.28, 11.63, 12.39,
                                  {
                                      'name': "Reentrada Rotonda",
                                      'data': {
                                          'possible_signs': ['roundabout']
                                      }
                                  })

        quadrant_map.add_quadrant(14.32, 15.08, 10.39, 11.15,
                                  {
                                      'name': "Entrada Autopista",
                                      'data': {
                                          'possible_signs': ['highway_entrance', 'highway_exit']
                                      }
                                  })

        quadrant_map.add_quadrant(6.7, 7.92, 11.98, 12.97,
                                  {
                                      'name': "Salida Autopista",
                                      'data': {
                                          'possible_signs': ['highway_entrance', 'highway_exit']
                                      }
                                  })

        quadrant_map.add_quadrant(0, 0.72, 10.57, 11.19,
                                  {
                                      'name': "Primer Stop",
                                      'data': {
                                          'possible_signs': ['stop']
                                      }
                                  })

        quadrant_map.add_quadrant(0, 1.29, 9.25, 10.57,
                                  {
                                      'name': "Entrada SpeedCurve",
                                      'data': {
                                          'possible_signs': ['crosswalk']
                                      }
                                  })

        quadrant_map.add_quadrant(4.26, 5.14, 8.04, 8.78,
                                  {
                                      'name': "Salida SpeedCurve",
                                      'data': {
                                          'possible_signs': ['crosswalk']
                                      }
                                  })

        quadrant_map.add_quadrant(3.47, 5.14, 6.51, 7.48,
                                  {
                                      'name': "Speed Challenge End",
                                      'data': {
                                          'possible_signs': ['stop']
                                      }
                                  })

        quadrant_map.add_quadrant(2.14, 2.9, 4.61, 5.17,
                                  {
                                      'name': "Only Semaphore",
                                      'data': {
                                          'possible_signs': []
                                      }
                                  })

        quadrant_map.add_quadrant(2.14, 2.9, 1.3, 1.93,
                                  {
                                      'name': "City Center Exit",
                                      'data': {
                                          'possible_signs': ['stop']
                                      }
                                  })

        quadrant_map.add_quadrant(7.41, 8.92, 0.52, 1.28,
                                  {
                                      'name': "Parking Start",
                                      'data': {
                                          'possible_signs': ['parking', 'crosswalk']
                                      }
                                  })

        quadrant_map.add_quadrant(11.27, 12.15, 1.3, 2.8,
                                  {
                                      'name': "Start Position",
                                      'data': {
                                          'possible_signs': []
                                      }
                                  })

        quadrant_map.add_quadrant(7.47, 8.23, 3.63, 4.39,
                                  {
                                      'name': "Bus Lane Exit",
                                      'data': {
                                          'possible_signs': []
                                      }
                                  })

        return quadrant_map

    @staticmethod
    def for_speed_mode():
        quadrant_map = QuadrantMap()
        quadrant_map.add_quadrant(11.27, 12.15, 1.3, 2.8,
                                  {
                                      'name': "Start Position",
                                      'data': {
                                          'possible_signs': []
                                      }
                                  })

        quadrant_map.add_quadrant(16.25, 17.46, 3.3, 4.38,
                                  {
                                      'name': "Cruce BUS-MINIAUTOPISTA",
                                      'data': {
                                          'possible_signs': ['stop']
                                      }
                                  })

        quadrant_map.add_quadrant(0, 0.72, 10.57, 11.19,
                                  {
                                      'name': "Primer Stop",
                                      'data': {
                                          'possible_signs': ['stop']
                                      }
                                  })

        quadrant_map.add_quadrant(3.47, 5.14, 6.51, 7.48,
                                  {
                                      'name': "Speed Challenge End",
                                      'data': {
                                          'possible_signs': ['stop']
                                      }
                                  })
        return quadrant_map

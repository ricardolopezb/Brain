import math

from src.austral.configs import USE_DEMO_ROUTE
from src.austral.gps.lib.gps.demo_route_calculator import DemoRouteCalculator


class DirectionProvider:
    def __init__(self, map):
        self.map = map
        self.previous_node = None
        self.path = None

    def set_route(self, start_coordinates, target_coordinates):
        start_node = self.map.get_closest_node(*start_coordinates)
        target_node = self.map.get_closest_node(*target_coordinates)

        print(f"GOING FROM Node-{start_node.id} TO Node-{target_node.id}")

        # Maybe change the method params for the coordinates directly
        if USE_DEMO_ROUTE:
            path = DemoRouteCalculator.calculate_route()
        else:
            path = self.map.get_shortest_path(start_node.id, target_node.id)
        self.path = path
        print("PATH TO FOLLOW:", path)
        self.previous_node = start_node

    def get_direction(self, current_x, current_y, is_blind=False):
        current_node = self.map.get_closest_node(current_x, current_y)
        if not current_node.is_critical and not is_blind:
            self.previous_node = current_node # should remove this, we are not saving the previous node anymore
            return {'status': 'unmodified', 'steer': 0} # should not send anything
        if current_node.id not in self.path:
            print(f"NODE {current_node.id} not found in path")
            return {'status': 'not found', 'steer': 0}
        current_node_index = self.path.index(current_node.id)
        if current_node_index + 1 == len(self.path):
            return {'status': 'reached destination', 'steer': 0}
        next_node_id = self.path[current_node_index + 1]
        next_node = self.map.get_node_by_id(next_node_id)

        if current_node_index - 1 < 0:
            return {'status': 'starting', 'steer': 0}
        previous_node_id = self.path[current_node_index - 1]
        previous_node = self.map.get_node_by_id(previous_node_id)

        trajectory_vector = self._get_trajectory_vector(current_node, previous_node)
        route_vector = self._get_route_vector(current_node, next_node)
        correction_vector = self._get_correction_vector(trajectory_vector, route_vector)
        correction_vector_angle = self.angle_between_vectors(trajectory_vector, route_vector)
        angle = self._calculate_steering_angle(correction_vector, correction_vector_angle)
        return {'status': 'steering', 'steer': angle}

    def _get_route_vector(self, current_node, next_node):
        return next_node.x - current_node.x, next_node.y - current_node.y

    def _get_trajectory_vector(self, current_node, previous_node):
        return current_node.x - previous_node.x, current_node.y - previous_node.y

    def _get_correction_vector(self, trajectory_vector, route_vector):
        return trajectory_vector[0] - route_vector[0], trajectory_vector[1] - route_vector[1]

    def _calculate_steering_angle(self, correction_vector, correction_angle):
        print("Vector: ", correction_vector)
        print("Angle: ", correction_angle)
        steering_angle = 0

        if correction_angle == 0:
            return steering_angle
        if -15 <= correction_angle <= 15:
            return steering_angle

        if -50 <= correction_angle < 50:
            steering_angle = 12
        if -90 <= correction_angle <= 90:
            steering_angle = 22
        if correction_angle < 0:
            steering_angle = -steering_angle  # Turn left

        return steering_angle

    def dot_product(self, v1, v2):
        return v1[0] * v2[0] + v1[1] * v2[1]

    def magnitude(self, v):
        return math.sqrt(v[0] ** 2 + v[1] ** 2)

    def angle_between_vectors(self, v1, v2):
        dot = self.dot_product(v1, v2)
        mag1 = self.magnitude(v1)
        mag2 = self.magnitude(v2)
        if mag1 == 0 or mag2 == 0:
            return None  # Undefined angle for zero vectors
        angle = math.degrees(math.acos(dot / (mag1 * mag2)))
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        if cross_product < 0:
            angle = -angle
        return angle

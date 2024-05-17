import time

import cv2
import numpy as np
import math

from src.austral.configs import PID_TOLERANCE, PID_KP, PID_KI, PID_KD, LOW_SPEED, BASE_SPEED, THRESHOLD, ROI, KERNEL, \
    NECESSARY_VOTES, NEW_VOTES_LOGIC_ENABLED, set_new_votes_logic, get_new_votes_logic, PROP_CONSTANT, HIGH_SPEED
from src.utils.messages.allMessages import SpeedMotor


class PIDController:
    def __init__(self, Kp, Ki, Kd, tolerancia):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.prev_error = 0
        self.integral = 0
        self.iteration_count = 0
        self.integral_reset_interval = 10
        self.tolerancia = tolerancia

    def compute(self, error, dt, integral_reset_interval=None):
        if integral_reset_interval is not None:
            self.integral_reset_interval = integral_reset_interval

        proportional = error
        self.integral = self.integral + error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        self.iteration_count = self.iteration_count + 1

        # Reiniciar el término integral si se alcanza el intervalo deseado
        if self.iteration_count % self.integral_reset_interval == 0:
            self.integral = 0

        if abs(error) < self.tolerancia:
            control_signal = -3
        else:
            control_signal = self.Kp * proportional + self.Ki * self.integral + self.Kd * derivative
            control_signal = max(min(control_signal, 22), -22)
        return control_signal


class StanleyLaneDetector:
    def __init__(self, queue_list):
        self.consecutive_frames_without_left_line = 0
        self.consecutive_frames_without_right_line = 0
        self.consecutive_frames_with_horizontal_line = 0
        self.dt = 0.2
        self.kp = PID_KP
        self.ki = PID_KI
        self.kd = PID_KD
        self.tolerancia = PID_TOLERANCE
        self.prop_constant = PROP_CONSTANT
        self.allowed_frames = 4
        self.prev_steering_angle = 0
        self.prev_horizontal_line = 0
        self.pid_controller = PIDController(self.kp, self.ki, self.kd, self.tolerancia)
        self.threshold_value = THRESHOLD
        self.kernel_value = KERNEL
        self.ROI_value = ROI / 100
        self.necessary_votes = NECESSARY_VOTES
        self.queue_list = queue_list
        self.consecutive_single_right_lines = 0
        self.consecutive_single_left_lines = 0
        self.just_seen_two_lines = False
        self.lowered_speed = False
        self.should_decrease_votes = False
        self.first_time_in_votes_logic = True
        self.new_votes_logic_start_time = 0
        self.last_three_steering_angles = []

    def follow_left_line(self, line):
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        dy = y2 - y1
        if dx != 0:
            pendiente = math.degrees(abs(dy / dx))

            steering_angle = self.slope_mapper(pendiente)
        return steering_angle

    def follow_right_line(self, line):
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        dy = y2 - y1
        if dx != 0:
            pendiente = math.degrees(abs(dy / dx))
            steering_angle = self.slope_mapper(pendiente) * -1
        return steering_angle

    def control_signal(self, error):
        steering_angle = self.pid_controller.compute(error)
        return round(steering_angle)

    # ------------------------------------------------------------------------------------------

    def signal_detector(self):
        signal_detected = 1
        return signal_detected

    def follow_mid_line(self, image, average_horizontal_line, height, width):
        x1, y1, x2, y2 = average_horizontal_line[0]
        mid_point_horizontal_line_x = (x1 + x2) // 2
        mid_point_horizontal_line_y = (y1 + y2) // 2
        bottom_center_x = width // 2
        error = mid_point_horizontal_line_x - bottom_center_x
        steering_angle = self.control_signal(error)
        cv2.line(image, (mid_point_horizontal_line_x, mid_point_horizontal_line_y), (bottom_center_x, height),
                 (165, 0, 255), 2)
        return steering_angle

    def lower_speed(self):
        self.lowered_speed = True
        self.queue_list['Warning'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": LOW_SPEED
        })

    def normalize_speed(self):
        self.lowered_speed = False
        self.queue_list['Warning'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": BASE_SPEED
        })

    def increase_speed(self):
        self.queue_list['Warning'].put({
            "Owner": SpeedMotor.Owner.value,
            "msgID": SpeedMotor.msgID.value,
            "msgType": SpeedMotor.msgType.value,
            "msgValue": HIGH_SPEED
        })

    def get_steering_angle(self, image):
        average_left_line, average_right_line, height, width, canny_image = self.image_processing(image)

        if average_left_line is not None and average_right_line is not None:
            # self.normalize_speed()
            point_A, point_B, point_C = self.getting_error(image, average_left_line, average_right_line, height, width)
            vector = self.prop_constant * (point_C - point_A) + (point_A - point_B)
            if abs(vector) > self.tolerancia:
                if vector > 0:
                    steering_angle = self.kp * abs(vector)
                else:
                    steering_angle = (-1) * self.kp * (vector)
            else:
                steering_angle = -3

            # cv2.circle(image, (point_A, height), 5, (255, 0, 0), -1)
            # cv2.circle(image, (point_B, height), 5, (0, 255, 0), -1)
            # cv2.circle(image, (point_C, height), 5, (0, 0, 255), -1)

        elif average_left_line is not None:
            # self.lower_speed()
            x1_left, y1_left, x2_left, y2_left = average_left_line[0]
            point_A = int(x1_left + (height - y1_left) * (x2_left - x1_left) / (y2_left - y1_left))
            point_B = width / 2
            point_C = int(x1_left + (0 - y1_left) * (x2_left - x1_left) / (y2_left - y1_left))
            if point_C > point_B and abs(point_C - point_A) > self.tolerancia:
                steering_angle = self.kp * abs(point_C - point_A)
            else:
                steering_angle = -3

                # cv2.circle(image, (point_B, height), 5, (0, 255, 0), -1)
            # cv2.circle(image, (point_C, height), 5, (0, 0, 255), -1)

        elif average_right_line is not None:
            # self.lower_speed()
            x1_right, y1_right, x2_right, y2_right = average_right_line[0]
            point_A = int(x1_right + (height - y1_right) * (x2_right - x1_right) / (y2_right - y1_right))
            point_B = width / 2
            point_C = int(x1_right + (0 - y1_right) * (x2_right - x1_right) / (y2_right - y1_right))
            if point_C < point_B and abs(point_C - point_A) > self.tolerancia:
                steering_angle = (-1) * self.kp * abs(point_C - point_A)
            else:
                steering_angle = -3

                # cv2.circle(image, (point_B, height), 5, (0, 255, 0), -1)
            # cv2.circle(image, (point_C, height), 5, (0, 0, 255), -1)

        else:
            steering_angle = self.prev_steering_angle

        if steering_angle < 14:
            if steering_angle < 7:
                if steering_angle < -7:
                    if steering_angle < -14:
                        steering_angle = -22
                    else:
                        steering_angle = -11
                else:
                    steering_angle = -3
            else:
                steering_angle = 11
        else:
            steering_angle = 22
        self.prev_steering_angle = steering_angle
        self.check_last_three_steering_angles(steering_angle, average_right_line, average_left_line)
        return steering_angle

    def check_last_three_steering_angles(self, steering_angle, average_right_line, average_left_line):
        if len(self.last_three_steering_angles) < 3:
            self.last_three_steering_angles.append(steering_angle)
            return
        else:
            if average_right_line is None or average_left_line is None:
                self.lower_speed()
            elif steering_angle != -3:
                self.normalize_speed()
            elif steering_angle == -3 and all(last_angle == steering_angle for last_angle in self.last_three_steering_angles):
                self.increase_speed()

            self.last_three_steering_angles.pop(0)
            self.last_three_steering_angles.append(steering_angle)

    def is_detecting_both_lines(self, average_left_line, average_right_line):
        return average_left_line is not None and average_right_line is not None

    def control_signal(self, error):
        steering_angle = self.pid_controller.compute(error, self.dt)
        return round(steering_angle)

    def lines_classifier(self, lines):
        left_lines = []
        right_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 - x1 == 0:
                    slope = np.pi / 2
                else:
                    slope = np.arctan((y2 - y1) / (x2 - x1))

                angle_degrees = np.degrees(abs(slope))
                if angle_degrees > 20 or (angle_degrees < 180 and angle_degrees > 160):
                    if slope < 0:
                        left_lines.append(line)
                    else:
                        right_lines.append(line)
                else:
                    continue
        return left_lines, right_lines

    def average_lines(self, lines):
        if len(lines) > 0:
            lines_array = np.array(lines)
            average_line = np.mean(lines_array, axis=0, dtype=np.int32)
            return average_line
        else:
            return None

    def get_intersection_point(self, line, y):
        x1, y1, x2, y2 = line[0]
        slope = (y2 - y1) / (x2 - x1)
        if slope == 0:
            return x1, y
        else:
            x = int(x1 + (y - y1) / slope)
            return x, y

    def line_drawing(self, image, line, height):
        x1, y1, x2, y2 = line[0]
        extended_line = np.array([
            self.get_intersection_point(line, 0),
            self.get_intersection_point(line, height)
        ], dtype=np.int32)
        cv2.line(image, (extended_line[0][0], extended_line[0][1]), (extended_line[1][0], extended_line[1][1]),
                 (0, 0, 255),
                 2)

    def lane_detection(self, left_lines, right_lines):
        # Si se detectaron líneas tanto a la izquierda como a la derecha
        if len(left_lines) > 0 and len(right_lines) > 0:
            self.consecutive_frames_without_left_line = 0
            self.consecutive_frames_without_right_line = 0
        # Si solo se detectaron líneas a la izquierda
        elif len(left_lines) > 0:
            self.consecutive_frames_without_left_line = 0
            self.consecutive_frames_without_right_line = self.consecutive_frames_without_right_line + 1
            print("Consecutive frames without right line:", self.consecutive_frames_without_right_line)
        # Si solo se detectaron líneas a la derecha
        elif len(right_lines) > 0:
            self.consecutive_frames_without_left_line = self.consecutive_frames_without_left_line + 1
            self.consecutive_frames_without_right_line = 0
            print("Consecutive frames without left line:", self.consecutive_frames_without_left_line)
        # Si no se detectaron líneas en ninguno de los lados
        else:
            self.consecutive_frames_without_left_line = self.consecutive_frames_without_left_line + 1
            self.consecutive_frames_without_right_line = self.consecutive_frames_without_right_line + 1

    def getting_error(self, image, average_left_line, average_right_line, height, width):
        x1_left, y1_left, x2_left, y2_left = average_left_line[0]
        x1_right, y1_right, x2_right, y2_right = average_right_line[0]

        # Calcular los puntos donde las líneas promedio izquierda y derecha intersectan el borde inferior de la imagen
        bottom_left_x = int(x1_left + (height - y1_left) * (x2_left - x1_left) / (y2_left - y1_left))
        bottom_right_x = int(x1_right + (height - y1_right) * (x2_right - x1_right) / (y2_right - y1_right))

        # Calcular el punto medio entre estos puntos
        midpoint_x = (bottom_left_x + bottom_right_x) // 2
        midpoint_y = height

        # Calcular la intersección de las líneas promedio izquierda y derecha
        if x2_left - x1_left == 0:
            x2_left = x1_left + 0.01

        if x2_right - x1_right == 0:
            x2_right = x1_right + 0.01

        slope_left = (y2_left - y1_left) / (x2_left - x1_left)
        slope_right = (y2_right - y1_right) / (x2_right - x1_right)

        # Manejar el caso cuando las líneas son paralelas
        if slope_left == slope_right:
            slope_right = slope_right + 0.01

        print(y1_right, y1_left, x1_right, x1_left, slope_left, slope_right)
        intersection_x = int(
            (y1_right - y1_left + slope_left * x1_left - slope_right * x1_right) / (slope_left - slope_right))
        intersection_y = int(slope_left * (intersection_x - x1_left) + y1_left)

        # Dibujar puntos y líneas en la imagen (opcional)
        cv2.circle(image, (intersection_x, intersection_y), 5, (255, 0, 255), -1)
        cv2.circle(image, (midpoint_x, midpoint_y), 5, (0, 255, 255), -1)
        cv2.line(image, (intersection_x, intersection_y), (midpoint_x, midpoint_y), (0, 165, 255), 2)
        bottom_center_x = width // 2
        bottom_center_y = height
        cv2.circle(image, (bottom_center_x, bottom_center_y), 5, (0, 255, 0), -1)

        point_A = int(midpoint_x)
        point_B = int(bottom_center_x)
        point_C = int(
            intersection_x + (0 - intersection_y) * (midpoint_x - intersection_x) / (midpoint_y - intersection_y))

        cv2.circle(image, (point_C, width), 5, (255, 255, 0), -1)

        return point_A, point_B, point_C

    # OLD
    # def getting_error(self, image, average_left_line, average_right_line, height, width):
    #     x1_left, y1_left, x2_left, y2_left = average_left_line[0]
    #     x1_right, y1_right, x2_right, y2_right = average_right_line[0]
    #
    #     # Calcular los puntos donde las líneas promedio izquierda y derecha intersectan el borde inferior de la imagen
    #     a = (y2_left - y1_left)
    #     if y2_left - y1_left == 0:
    #         a = 0.01
    #     bottom_left_x = int(x1_left + (height - y1_left) * (x2_left - x1_left) / a)
    #
    #     b = (y2_right - y1_right)
    #     if y2_right - y1_right == 0:
    #         b = 0.01
    #     bottom_right_x = int(x1_right + (height - y1_right) * (x2_right - x1_right) / b)
    #
    #     # Calcular el punto medio entre estos puntos
    #     midpoint_x = (bottom_left_x + bottom_right_x) // 2
    #     midpoint_y = height
    #
    #     # Calcular la intersección de las líneas promedio izquierda y derecha
    #     c = (x2_left - x1_left)
    #     if x2_left - x1_left == 0:
    #         c = 0.01
    #     slope_left = (y2_left - y1_left) / c
    #
    #     d = (x2_right - x1_right)
    #     if x2_right - x1_right == 0:
    #         d = 0.01
    #     slope_right = (y2_right - y1_right) / d
    #
    #     e = (slope_left - slope_right)
    #     if slope_left - slope_right == 0:
    #         e = 0.01
    #     intersection_x = int(
    #         (y1_right - y1_left + slope_left * x1_left - slope_right * x1_right) / e)
    #     intersection_y = int(slope_left * (intersection_x - x1_left) + y1_left)
    #
    #     cv2.circle(image, (intersection_x, intersection_y), 5, (255, 0, 255), -1)
    #
    #     cv2.circle(image, (midpoint_x, midpoint_y), 5, (0, 255, 255), -1)
    #
    #     cv2.line(image, (intersection_x, intersection_y), (midpoint_x, midpoint_y), (0, 165, 255), 2)
    #
    #     bottom_center_x = width // 2
    #     bottom_center_y = height
    #     cv2.circle(image, (bottom_center_x, bottom_center_y), 5, (0, 255, 0), -1)
    #     error = midpoint_x - bottom_center_x
    #     return error

    def merge_lines(self, lines):
        merged_lines = []
        for line in lines:
            if len(merged_lines) == 0:
                merged_lines.append(line)
            else:
                # Comprobar si la línea actual está lo suficientemente cerca de alguna de las líneas fusionadas
                merge_flag = False
                for i, merged_line in enumerate(merged_lines):
                    if abs(line[0][0] - merged_line[0][
                        2]) < 175:  # Cambiar el valor según la distancia de fusión deseada
                        merged_lines[i] = np.array([[merged_line[0][0], merged_line[0][1], line[0][2], line[0][3]]])
                        merge_flag = True
                        break
                if not merge_flag:
                    merged_lines.append(line)
        return merged_lines

    def slope_mapper(self, angle):
        to_return = 0
        if angle > 50:
            to_return = 3
        elif angle > 40:
            to_return = 11
        elif angle > 0:
            to_return = 22
        elif angle > -40:
            to_return = -22
        elif angle > -50:
            to_return = -11
        else:
            to_return = -3
        # print('### MAPEADO', to_return)
        return to_return

    def conditioning(self, frame, gauss_size, deviation):
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grey[:117, :] = 140
        avg_brightness = np.mean(grey)
        if avg_brightness < 129:
            frame = cv2.convertScaleAbs(frame, 1000, 0.52)
        elif avg_brightness > 128:
            frame = cv2.convertScaleAbs(frame, 1000, 3)
        conditioned = cv2.GaussianBlur(frame, (gauss_size, gauss_size), deviation)
        return conditioned

    def image_processing(self, image):

        if self.kernel_value % 2 == 0:
            self.kernel_value = self.kernel_value + 1

        height, width = image.shape[:2]

        x1 = 0
        y1 = int(self.ROI_value * height)
        x2 = width
        y2 = (height)
        x3 = 365
        y3 = 230
        x4 = 145

        roi_vertices = np.array([[(x1, y1), (x2, y1), (x2, y2), (x3, y2), (x3, y3), (x4, y3), (x4, y2), (x1, y2)]],
                                dtype=np.int32)
        # image = self.conditioning(image, 5, 0.9)
        mask = np.zeros_like(image)
        cv2.fillPoly(mask, roi_vertices, (255, 255, 255))
        masked_image = cv2.bitwise_and(image, mask)

        grey_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(grey_image, self.threshold_value, 255, cv2.THRESH_BINARY)
        noiseless_image = cv2.medianBlur(binary_image, self.kernel_value)
        canny_image = cv2.Canny(noiseless_image, 100, 150)

        lines = cv2.HoughLinesP(canny_image, 1, np.pi / 180, self.necessary_votes, minLineLength=50, maxLineGap=150)

        left_lines, right_lines = self.lines_classifier(lines)

        merged_left_lines = self.merge_lines(left_lines)
        merged_right_lines = self.merge_lines(right_lines)

        average_left_line = self.average_lines(merged_left_lines)
        if average_left_line is not None:
            self.line_drawing(image, average_left_line, height=height)

        average_right_line = self.average_lines(merged_right_lines)
        if average_right_line is not None:
            self.line_drawing(image, average_right_line, height=height)

        return average_left_line, average_right_line, height, width, canny_image

    def plan_c(self, canny, width, height):
        slope = 70
        for y in np.linspace(0, int(height * 0.35) - 2, int(height * 0.35) - 1):
            for x in np.linspace(0, int(width) - 2, int(width) - 1):
                x = int(x)
                y = int(y)
                value = canny[y][x]
                if value == 255:
                    a = y - height
                    if a == 0:
                        a = 0.01

                    slope = np.abs((x - (width / 2)) / a)
                    x = width - 1
                    y = height * 0.35 - 1

        slope = math.degrees(slope)
        steering_angle = self.slope_mapper(slope)
        return steering_angle

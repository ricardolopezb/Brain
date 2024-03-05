import cv2
import numpy as np
import math



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
        print(proportional)
        print(self.integral)
        print(derivative)
        return control_signal


class LaneDetector:
    def __init__(self):
        self.consecutive_frames_without_left_line = 0
        self.consecutive_frames_without_right_line = 0
        self.consecutive_frames_with_horizontal_line = 0
        self.dt = 0.2
        self.kp = 0.1
        self.ki = 0.05
        self.kd = 0.05
        self.tolerancia = 50
        self.allowed_frames = 4
        self.prev_steering_angle = 0
        self.prev_horizontal_line = 0
        self.pid_controller = PIDController(self.kp, self.ki, self.kd, self.tolerancia)

    def follow_left_line(self, line):
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        dy = y2 - y1
        if dx != 0:
            pendiente = math.degrees(abs(dy / dx))
            print('PENDIENTE', pendiente)
            if pendiente > 30:
                steering_angle = round(22 - ((pendiente - 30) * (22 / 60)))
            else:
                steering_angle = 22
        return steering_angle

    def follow_right_line(self, line):
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        dy = y2 - y1
        if dx != 0:
            pendiente = math.degrees(abs(dy / dx))
            print('PENDIENTE', pendiente)
            if pendiente > 30:
                steering_angle = round(- (22 - ((pendiente - 30) * (22 / 60))))
            else:
                steering_angle = -22
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

    def get_steering_angle(self, image):
        average_left_line, average_right_line, average_horizontal_line, height, width, canny_image = self.image_processing(
            image=image)
        if average_horizontal_line is not None:
            self.consecutive_frames_with_horizontal_line = self.consecutive_frames_with_horizontal_line + 1
        else:
            self.consecutive_frames_with_horizontal_line = 0

        if average_horizontal_line is not None and self.consecutive_frames_with_horizontal_line > 20:
            self.prev_horizontal_line = 1
            steering_angle = self.follow_mid_line(image, average_horizontal_line, height, width)
        else:
            if self.is_detecting_both_lines(average_left_line, average_right_line):
                error = self.getting_error(image, average_left_line, average_right_line, height, width)
                steering_angle = self.control_signal(error)
            elif average_left_line is not None:
                steering_angle = self.follow_left_line(average_left_line)
            elif average_right_line is not None:
                steering_angle = self.follow_right_line(average_right_line)
            else:
                steering_angle = self.prev_steering_angle
        self.prev_steering_angle = steering_angle
        return self.standarize_angle(steering_angle)

    def is_detecting_both_lines(self, average_left_line, average_right_line):
        return average_left_line is not None and average_right_line is not None

    def control_signal(self, error):
        steering_angle = self.pid_controller.compute(error, self.dt)
        return round(steering_angle)

    def image_processing(self, image):
        threshold_value = 165
        kernel_value = 7
        ROI_value = 0.45

        height, width = image.shape[:2]

        x1 = 0
        y1 = int(ROI_value * height)
        x2 = width
        y2 = height

        roi_vertices = np.array([[(x1, y1), (x2, y1), (x2, y2), (x1, y2)]], dtype=np.int32)
        mask = np.zeros_like(image)
        cv2.fillPoly(mask, roi_vertices, (255, 255, 255))
        masked_image = cv2.bitwise_and(image, mask)

        grey_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(grey_image, threshold_value, 255, cv2.THRESH_BINARY)
        noiseless_image = cv2.medianBlur(binary_image, kernel_value)
        canny_image = cv2.Canny(noiseless_image, 100, 150)

        lines = cv2.HoughLinesP(canny_image, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=150)

        left_lines, right_lines, horizontal_lines = self.lines_classifier(lines=lines)

        merged_left_lines = self.merge_lines(left_lines)
        merged_right_lines = self.merge_lines(right_lines)
        merged_horizontal_lines = self.merge_lines(horizontal_lines)

        average_left_line = self.average_lines(merged_left_lines)
        if average_left_line is not None:
            self.line_drawing(image, average_left_line, height=height)

        average_right_line = self.average_lines(merged_right_lines)
        if average_right_line is not None:
            self.line_drawing(image, average_right_line, height=height)

        average_horizontal_line = self.average_lines(merged_horizontal_lines)
        if average_horizontal_line is not None:
            x1, y1, x2, y2 = average_horizontal_line[0]
            cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

        return average_left_line, average_right_line, average_horizontal_line, height, width, canny_image

    # def lines_classifier(self, lines):
    #     left_lines = []
    #     right_lines = []
    #     if lines is not None:
    #         for line in lines:
    #             x1, y1, x2, y2 = line[0]
    #             # Calcular la pendiente de la línea
    #             if x2 - x1 == 0:  # Evitar división por cero
    #                 slope = np.pi / 2  # Línea vertical, pendiente infinita
    #             else:
    #                 slope = np.arctan((y2 - y1) / (x2 - x1))
    #
    #             # Convertir la pendiente a grados
    #             angle_degrees = np.degrees(abs(slope))
    #
    #             # Verificar si la línea es horizontal (dentro del margen de +/- 20 grados)
    #             if angle_degrees > 80 and angle_degrees < 100:  # Cambia los valores según el margen deseado
    #                 continue
    #
    #             # Clasificar la línea como izquierda o derecha basándose en la pendiente
    #             if slope < 0:
    #                 left_lines.append(line)
    #             else:
    #                 right_lines.append(line)
    #     return left_lines, right_lines

    def lines_classifier(self, lines):
        left_lines = []
        right_lines = []
        horizontal_lines = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Calcular la pendiente de la línea
                if x2 - x1 == 0:  # Evitar división por cero
                    slope = np.pi / 2  # Línea vertical, pendiente infinita
                else:
                    slope = np.arctan((y2 - y1) / (x2 - x1))

                # Convertir la pendiente a grados
                angle_degrees = np.degrees(abs(slope))

                # Verificar si la línea es horizontal (dentro del margen de +/- 20 grados)
                if abs(angle_degrees) < 7 or abs(
                        angle_degrees - 180) < 7:  # Considera líneas dentro de +/- 20 grados de horizontal
                    horizontal_lines.append(line)
                    continue

                # Clasificar la línea como izquierda o derecha basándose en la pendiente
                if abs(angle_degrees) > 50 or abs(angle_degrees - 180) > 50:
                    if slope < 0:
                        left_lines.append(line)
                    else:
                        right_lines.append(line)
                else:
                    continue

        return left_lines, right_lines, horizontal_lines

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
        a = (y2_left - y1_left)
        if y2_left - y1_left == 0:
            a = 0.01
        bottom_left_x = int(x1_left + (height - y1_left) * (x2_left - x1_left) / a)

        b = (y2_right - y1_right)
        if y2_right - y1_right == 0:
            b = 0.01
        bottom_right_x = int(x1_right + (height - y1_right) * (x2_right - x1_right) / b)

        # Calcular el punto medio entre estos puntos
        midpoint_x = (bottom_left_x + bottom_right_x) // 2
        midpoint_y = height

        # Calcular la intersección de las líneas promedio izquierda y derecha
        c = (x2_left - x1_left)
        if x2_left - x1_left == 0:
            c = 0.01
        slope_left = (y2_left - y1_left) / c

        d = (x2_right - x1_right)
        if x2_right - x1_right == 0:
            d = 0.01
        slope_right = (y2_right - y1_right) / d

        e = (slope_left - slope_right)
        if slope_left - slope_right == 0:
            e = 0.01
        intersection_x = int(
            (y1_right - y1_left + slope_left * x1_left - slope_right * x1_right) / e)
        intersection_y = int(slope_left * (intersection_x - x1_left) + y1_left)

        cv2.circle(image, (intersection_x, intersection_y), 5, (255, 0, 255), -1)

        cv2.circle(image, (midpoint_x, midpoint_y), 5, (0, 255, 255), -1)

        cv2.line(image, (intersection_x, intersection_y), (midpoint_x, midpoint_y), (0, 165, 255), 2)

        bottom_center_x = width // 2
        bottom_center_y = height
        cv2.circle(image, (bottom_center_x, bottom_center_y), 5, (0, 255, 0), -1)
        error = midpoint_x - bottom_center_x
        return error

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
                        2]) < 100:  # Cambiar el valor según la distancia de fusión deseada
                        merged_lines[i] = np.array([[merged_line[0][0], merged_line[0][1], line[0][2], line[0][3]]])
                        merge_flag = True
                        break
                if not merge_flag:
                    merged_lines.append(line)
        return merged_lines

    def standarize_angle(self, angle):
        if -22 <= angle <= -16:
            return -22
        elif -15 <= angle <= -7:
            return -11
        elif -6 <= angle <= 6:
            return -3
        elif 7 <= angle <= 15:
            return 11
        elif 16 <= angle <= 22:
            return 22


    def between(self, current, min, max):
        return min <= current <= max






# lane_detector = LaneDetector()
# while True:
#     ret, image = camera.read()
#     if not ret:
#         print("Error al capturar la imagen desde la cámara.")
#         break
#
#     steering_angle = lane_detector.get_steering_angle(image)
#     prev_steering_angle = steering_angle
#     cv2.imshow("Imagen", image)
#     cv2.waitKey(0)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#     elif cv2.waitKey(1) & 0xFF == ord(' '):
#         continue
#
# camera.release()
# cv2.destroyAllWindows()

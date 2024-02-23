import cv2
import numpy as np

# Inicializar contadores y variables
frames_consecutivos_sin_linea_izquierda = 0
frames_consecutivos_sin_linea_derecha = 0
umbral = 5  # Umbral para considerar que una línea ha desaparecido


def average_lines(lines):
    if len(lines) > 0:
        lines_array = np.array(lines)
        average_line = np.mean(lines_array, axis=0, dtype=np.int32)
        return average_line
    else:
        return None


def get_error(imagen):
    global frames_consecutivos_sin_linea_derecha
    global frames_consecutivos_sin_linea_izquierda
    valor_umbral = 190
    valor_kernel = 11
    valor_ROI = 0.5

    height, width = imagen.shape[:2]

    # Definir la región de interés (ROI) como un cuarto de la imagen en la parte inferior
    x1 = 0
    y1 = int(valor_ROI * height)
    x2 = width
    y2 = height

    # Definir los vértices de la región de interés (ROI) como un rectángulo
    roi_vertices = np.array([[(x1, y1), (x2, y1), (x2, y2), (x1, y2)]], dtype=np.int32)
    mask = np.zeros_like(imagen)
    cv2.fillPoly(mask, roi_vertices, (255, 255, 255))
    masked_image = cv2.bitwise_and(imagen, mask)
    imagen_escala_gris = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
    _, imagen_blanco_y_negro = cv2.threshold(imagen_escala_gris, valor_umbral, 255, cv2.THRESH_BINARY)
    imagen_sin_ruido = cv2.medianBlur(imagen_blanco_y_negro, valor_kernel)
    imagen_canny = cv2.Canny(imagen_sin_ruido, 50, 150)
    lines = cv2.HoughLinesP(imagen_canny, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=150)

    left_lines = []
    right_lines = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1)
            if slope < 0:
                left_lines.append(line)
            else:
                right_lines.append(line)

    # Calcular el promedio de las líneas izquierdas y las líneas derechas

    average_left_line = average_lines(left_lines)
    average_right_line = average_lines(right_lines)

    # Dibujar las líneas promedio en la imagen original
    if average_left_line is not None:
        x1, y1, x2, y2 = average_left_line[0]
        cv2.line(imagen, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if average_right_line is not None:
        x1, y1, x2, y2 = average_right_line[0]
        cv2.line(imagen, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # Calcular los puntos de intersección entre las líneas promedio extendidas y el borde superior de la imagen
    def get_intersection_point(line, y):
        x1, y1, x2, y2 = line[0]
        slope = (y2 - y1) / (x2 - x1)
        if slope == 0:
            return x1, y
        else:
            x = int(x1 + (y - y1) / slope)
            return x, y

    if average_left_line is not None:
        x1, y1, x2, y2 = average_left_line[0]
        extended_left_line = np.array([
            get_intersection_point(average_left_line, 0),
            get_intersection_point(average_left_line, height)
        ], dtype=np.int32)
        cv2.line(imagen, (extended_left_line[0][0], extended_left_line[0][1]),
                 (extended_left_line[1][0], extended_left_line[1][1]), (0, 0, 255), 2)

    if average_right_line is not None:
        x1, y1, x2, y2 = average_right_line[0]
        extended_right_line = np.array([
            get_intersection_point(average_right_line, 0),
            get_intersection_point(average_right_line, height)
        ], dtype=np.int32)
        cv2.line(imagen, (extended_right_line[0][0], extended_right_line[0][1]),
                 (extended_right_line[1][0], extended_right_line[1][1]), (0, 0, 255), 2)

    # Suponiendo que estás dentro de un bucle para procesar los frames...

    # Si se detectaron líneas tanto a la izquierda como a la derecha
    if len(left_lines) > 0 and len(right_lines) > 0:
        frames_consecutivos_sin_linea_izquierda = 0
        frames_consecutivos_sin_linea_derecha = 0
    # Si solo se detectaron líneas a la izquierda
    elif len(left_lines) > 0:
        frames_consecutivos_sin_linea_izquierda = 0
        frames_consecutivos_sin_linea_derecha = frames_consecutivos_sin_linea_derecha + 1
        print("SIN LINEA DERECHA", frames_consecutivos_sin_linea_derecha)
        if frames_consecutivos_sin_linea_derecha >= umbral:
            print("Girar a la derecha")
            # Aquí puedes activar la variable "doblar" o "girar" según sea necesario
    # Si solo se detectaron líneas a la derecha
    elif len(right_lines) > 0:
        frames_consecutivos_sin_linea_izquierda += 1
        frames_consecutivos_sin_linea_derecha = 0
        if frames_consecutivos_sin_linea_izquierda >= umbral:
            print("Girar a la izquierda")
            # Aquí puedes activar la variable "doblar" o "girar" según sea necesario
    # Si no se detectaron líneas en ninguno de los lados
    else:
        frames_consecutivos_sin_linea_izquierda += 1
        frames_consecutivos_sin_linea_derecha += 1
        # Podrías tomar alguna acción adicional si ambas líneas están ausentes en varios frames consecutivos

    # Calcular el punto medio entre las líneas promedio izquierda y derecha en la parte inferior de la imagen
    if average_left_line is not None and average_right_line is not None:
        x1_left, y1_left, x2_left, y2_left = average_left_line[0]
        x1_right, y1_right, x2_right, y2_right = average_right_line[0]

        # Calcular los puntos donde las líneas promedio izquierda y derecha intersectan el borde inferior de la imagen
        bottom_left_x = int(x1_left + (height - y1_left) * (x2_left - x1_left) / (y2_left - y1_left))
        bottom_right_x = int(x1_right + (height - y1_right) * (x2_right - x1_right) / (y2_right - y1_right))

        # Calcular el punto medio entre estos puntos
        midpoint_x = (bottom_left_x + bottom_right_x) // 2
        midpoint_y = height

        # Calcular la intersección de las líneas promedio izquierda y derecha
        slope_left = (y2_left - y1_left) / (x2_left - x1_left)
        slope_right = (y2_right - y1_right) / (x2_right - x1_right)
        intersection_x = int(
            (y1_right - y1_left + slope_left * x1_left - slope_right * x1_right) / (slope_left - slope_right))
        intersection_y = int(slope_left * (intersection_x - x1_left) + y1_left)

        # Dibujar un círculo en la intersección (solo para verificar)
        cv2.circle(imagen, (intersection_x, intersection_y), 5, (255, 0, 255), -1)

        # Dibujar la línea desde la intersección superior hasta el punto medio en la parte inferior
        cv2.line(imagen, (intersection_x, intersection_y), (midpoint_x, midpoint_y), (0, 165, 255), 2)

    # Calcular el punto inferior de la línea media que corta la parte inferior de la imagen
    bottom_midline_x = midpoint_x
    bottom_midline_y = height

    # Calcular el punto inferior del centro de la imagen
    bottom_center_x = width // 2
    bottom_center_y = height

    # Calcular la distancia entre el punto inferior del centro de la imagen y el punto inferior de la línea media
    distance_to_bottom_midline = bottom_midline_x - bottom_center_x

    print("Valor del error en píxeles:", distance_to_bottom_midline)

    # Dibujar un círculo en el punto inferior de la línea media
    cv2.circle(imagen, (midpoint_x, midpoint_y), 5, (0, 255, 255), -1)

    # Dibujar un círculo en el punto inferior del centro de la imagen
    cv2.circle(imagen, (bottom_center_x, bottom_center_y), 5, (0, 255, 0), -1)

    print(type(imagen))
    cv2.imshow("Líneas detectadas", imagen)
    # cv2.imshow('Monocromatico', imagen_canny)

    cv2.waitKey(0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    elif cv2.waitKey(1) & 0xFF == ord(' '):
        continue


class PIDController:
    def _init_(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, error, dt):
        proportional = error
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error
        control_signal = self.Kp * proportional + self.Ki * self.integral + self.Kd * derivative
        control_signal = max(min(control_signal, 20), -20)  # Limitar el control signal a +/- 20 grados
        return control_signal

    def control_signal(self, error, dt):
        pid_controller = PIDController(self.Kp, self.Ki, self.Kd)

        if abs(error) < 40:
            control_signal = -3
        else:
            control_signal = pid_controller.compute(error, dt)
        return control_signal


class LaneDetector:
    def __init__(self):
        self.valor_umbral = 190
        self.valor_kernel = 11
        self.valor_ROI = 0.5
        self.frames_consecutivos_sin_linea_izquierda = 0
        self.frames_consecutivos_sin_linea_derecha = 0
        self.umbral = 5

    # Funcion que da la cantidad de pixeles entre el punto medio de la imagen y el centro del carril detectado
    def get_error(self, imagen):
        height, width = imagen.shape[:2]

        # Definir la región de interés (ROI) como un cuarto de la imagen en la parte inferior
        x1 = 0
        y1 = int(self.valor_ROI * height)
        x2 = width
        y2 = height

        # Definir los vértices de la región de interés (ROI) como un rectángulo
        roi_vertices = np.array([[(x1, y1), (x2, y1), (x2, y2), (x1, y2)]], dtype=np.int32)
        mask = np.zeros_like(imagen)
        cv2.fillPoly(mask, roi_vertices, (255, 255, 255))
        masked_image = cv2.bitwise_and(imagen, mask)
        imagen_escala_gris = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
        _, imagen_blanco_y_negro = cv2.threshold(imagen_escala_gris, self.valor_umbral, 255, cv2.THRESH_BINARY)
        imagen_sin_ruido = cv2.medianBlur(imagen_blanco_y_negro, self.valor_kernel)
        imagen_canny = cv2.Canny(imagen_sin_ruido, 50, 150)
        lines = cv2.HoughLinesP(imagen_canny, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=150)

        left_lines = []
        right_lines = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                slope = (y2 - y1) / (x2 - x1)
                if slope < 0:
                    left_lines.append(line)
                else:
                    right_lines.append(line)

        # Calcular el promedio de las líneas izquierdas y las líneas derechas

        average_left_line = average_lines(left_lines)
        average_right_line = average_lines(right_lines)

        # Dibujar las líneas promedio en la imagen original
        if average_left_line is not None:
            x1, y1, x2, y2 = average_left_line[0]
            cv2.line(imagen, (x1, y1), (x2, y2), (255, 0, 0), 2)

        if average_right_line is not None:
            x1, y1, x2, y2 = average_right_line[0]
            cv2.line(imagen, (x1, y1), (x2, y2), (255, 0, 0), 2)

        if average_left_line is not None:
            x1, y1, x2, y2 = average_left_line[0]
            extended_left_line = np.array([
                self.get_intersection_point(average_left_line, 0),
                self.get_intersection_point(average_left_line, height)
            ], dtype=np.int32)
            cv2.line(imagen, (extended_left_line[0][0], extended_left_line[0][1]),
                     (extended_left_line[1][0], extended_left_line[1][1]), (0, 0, 255), 2)

        if average_right_line is not None:
            x1, y1, x2, y2 = average_right_line[0]
            extended_right_line = np.array([
                self.get_intersection_point(average_right_line, 0),
                self.get_intersection_point(average_right_line, height)
            ], dtype=np.int32)
            cv2.line(imagen, (extended_right_line[0][0], extended_right_line[0][1]),
                     (extended_right_line[1][0], extended_right_line[1][1]), (0, 0, 255), 2)

        # Suponiendo que estás dentro de un bucle para procesar los frames...

        # Si se detectaron líneas tanto a la izquierda como a la derecha
        if len(left_lines) > 0 and len(right_lines) > 0:
            self.frames_consecutivos_sin_linea_izquierda = 0
            self.frames_consecutivos_sin_linea_derecha = 0
        # Si solo se detectaron líneas a la izquierda
        elif len(left_lines) > 0:
            self.frames_consecutivos_sin_linea_izquierda = 0
            self.frames_consecutivos_sin_linea_derecha = self.frames_consecutivos_sin_linea_derecha + 1
            print("SIN LINEA DERECHA", self.frames_consecutivos_sin_linea_derecha)
            if self.frames_consecutivos_sin_linea_derecha >= self.umbral:
                print("Girar a la derecha")
                # Aquí puedes activar la variable "doblar" o "girar" según sea necesario
        # Si solo se detectaron líneas a la derecha
        elif len(right_lines) > 0:
            self.frames_consecutivos_sin_linea_izquierda = self.frames_consecutivos_sin_linea_izquierda + 1
            self.frames_consecutivos_sin_linea_derecha = 0
            if self.frames_consecutivos_sin_linea_izquierda >= self.umbral:
                print("Girar a la izquierda")
                # Aquí puedes activar la variable "doblar" o "girar" según sea necesario
        # Si no se detectaron líneas en ninguno de los lados
        else:
            self.frames_consecutivos_sin_linea_izquierda = self.frames_consecutivos_sin_linea_izquierda + 1
            self.frames_consecutivos_sin_linea_derecha = self.frames_consecutivos_sin_linea_derecha + 1
            # Podrías tomar alguna acción adicional si ambas líneas están ausentes en varios frames consecutivos

        # Calcular el punto medio entre las líneas promedio izquierda y derecha en la parte inferior de la imagen
        if average_left_line is not None and average_right_line is not None:
            x1_left, y1_left, x2_left, y2_left = average_left_line[0]
            x1_right, y1_right, x2_right, y2_right = average_right_line[0]

            # Calcular los puntos donde las líneas promedio izquierda y derecha intersectan el borde inferior de la imagen
            bottom_left_x = int(x1_left + (height - y1_left) * (x2_left - x1_left) / (y2_left - y1_left))
            bottom_right_x = int(x1_right + (height - y1_right) * (x2_right - x1_right) / (y2_right - y1_right))

            # Calcular el punto medio entre estos puntos
            midpoint_x = (bottom_left_x + bottom_right_x) // 2
            midpoint_y = height

            # Calcular la intersección de las líneas promedio izquierda y derecha
            slope_left = (y2_left - y1_left) / (x2_left - x1_left)
            slope_right = (y2_right - y1_right) / (x2_right - x1_right)
            intersection_x = int(
                (y1_right - y1_left + slope_left * x1_left - slope_right * x1_right) / (slope_left - slope_right))
            intersection_y = int(slope_left * (intersection_x - x1_left) + y1_left)

            # Dibujar un círculo en la intersección (solo para verificar)
            cv2.circle(imagen, (intersection_x, intersection_y), 5, (255, 0, 255), -1)

            # Dibujar la línea desde la intersección superior hasta el punto medio en la parte inferior
            cv2.line(imagen, (intersection_x, intersection_y), (midpoint_x, midpoint_y), (0, 165, 255), 2)

        # Calcular el punto inferior de la línea media que corta la parte inferior de la imagen
        bottom_midline_x = midpoint_x
        bottom_midline_y = height

        # Calcular el punto inferior del centro de la imagen
        bottom_center_x = width // 2
        bottom_center_y = height

        # Calcular la distancia entre el punto inferior del centro de la imagen y el punto inferior de la línea media
        distance_to_bottom_midline = bottom_midline_x - bottom_center_x
        return distance_to_bottom_midline

    # Calcular los puntos de intersección entre las líneas promedio extendidas y el borde superior de la imagen
    def get_intersection_point(self, line, y):
        x1, y1, x2, y2 = line[0]
        slope = (y2 - y1) / (x2 - x1)
        if slope == 0:
            return x1, y
        else:
            x = int(x1 + (y - y1) / slope)
            return x, y

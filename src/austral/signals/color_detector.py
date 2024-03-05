import cv2
import numpy as np

# Inicializar la cámara
cap = cv2.VideoCapture(0)


class ColorDetector:
    def __init__(self):
        pass

    def detecta_azul(self, frame):
        # Convertir el frame a espacio de color HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Definir el rango de color azul en HSV
        lower_blue = np.array([110, 50, 50])
        upper_blue = np.array([130, 255, 255])

        # Crear una máscara que solo contenga colores azules
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Verificar si hay azul en la máscara
        if cv2.countNonZero(mask) > 0:
            return True, mask
        else:
            return False, mask

    def detecta_rojo(self, frame):
        # Convertir el frame a espacio de color HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Rojo bajo (ajustando para capturar rojos más saturados y brillantes)
        lower_red1 = np.array([170, 150, 150])
        upper_red1 = np.array([180, 255, 255])
        # Rojo alto (también ajustado para la misma razón)
        lower_red2 = np.array([0, 150, 150])
        upper_red2 = np.array([10, 255, 255])

        # Crear una máscara que solo contenga colores rojos
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # Verificar si hay rojo en la máscara
        if cv2.countNonZero(mask_red) > 0:
            return True, mask_red
        else:
            return False, mask_red

    def detect_color(self, frame):
        detected_blue, _ = self.detecta_azul(frame)
        detected_red, _ = self.detecta_rojo(frame)
        if detected_blue:
            return "AZUL"
        if detected_red:
            return "ROJO"
        return "NO COLOR"

# while True:
#     # Leer el frame de la cámara
#     _, frame = cap.read()
#
#     # Detectar azul en el frame
#     azul_encontrado, blue_mask = detecta_azul(frame)
#     rojo_encontrado, red_mask = detecta_rojo(frame)
#
#     combined_mask = cv2.bitwise_or(blue_mask, red_mask)
#     detected_colors = cv2.bitwise_and(frame, frame, mask=combined_mask)
#
#     # Mostrar el frame original y el resultado
#     cv2.imshow('Original', frame)
#     cv2.imshow('Azul y Rojo Detectados', detected_colors)
#
#     # Imprimir en consola si se detectó azul
#     if azul_encontrado:
#         print("Azul detectado")
#
#     # Imprimir en consola si se detectó rojo
#     if rojo_encontrado:
#         print("Rojo detectado")
#
#     # Romper el bucle con la tecla 'q'
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # Liberar la cámara y cerrar todas las ventanas
# cap.release()
# cv2.destroyAllWindows()

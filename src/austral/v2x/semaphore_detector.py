import cv2
import numpy as np


class SemaphoreDetector:
    def detect(self, imagen):
        # Convertir la imagen de BGR a HSV
        hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

        # Definir rangos de color para el rojo y el verde
        rojo_bajo = np.array([0, 150, 150])
        rojo_alto = np.array([10, 255, 255])
        verde_bajo = np.array([50, 150, 150])
        verde_alto = np.array([80, 255, 255])

        # Definir la región de interés (ROI) en  la parte derecha de la imagen
        alto, ancho, _ = imagen.shape
        roi = imagen[:, ancho // 2:, :]

        roi_vertices = np.array([[(int(2 / 3 * ancho), 0), (ancho, 0), (ancho, alto), (int(2 / 3 * ancho), alto)]])
        mask = np.zeros_like(imagen)
        cv2.fillPoly(mask, roi_vertices, (255, 255, 255))
        imagen = cv2.bitwise_and(imagen, mask)

        # Crear máscaras para el rojo y el verde en la región de interés
        mascara_rojo = cv2.inRange(hsv, rojo_bajo, rojo_alto)
        mascara_verde = cv2.inRange(hsv, verde_bajo, verde_alto)

        # Encuentra los contornos de las máscaras de color
        contornos_rojos, _ = cv2.findContours(mascara_rojo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contornos_verdes, _ = cv2.findContours(mascara_verde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Dibuja los contornos en la imagen original
        cv2.drawContours(imagen, contornos_rojos, -1, (0, 0, 255), 2)
        cv2.drawContours(imagen, contornos_verdes, -1, (0, 255, 0), 2)

        # Contar píxeles rojos y verdes en la región de interés
        total_pixeles_rojos = cv2.countNonZero(mascara_rojo)
        total_pixeles_verdes = cv2.countNonZero(mascara_verde)

        # Determinar el estado del semáforo
        if total_pixeles_rojos > total_pixeles_verdes:
            estado = "RED"
        elif total_pixeles_verdes > total_pixeles_rojos:
            estado = "GREEN"
        else:
            estado = "NOTHING"

        return estado

import cv2
import torch
import time
import numpy as np

# Cargar el modelo
model = torch.hub.load('ultralytics/yolov5', 'custom', path='.\\yolov5\\runs\\train\\exp4\\weights\\best.pt', force_reload=True)

def capture_and_process_images(model):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara web.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: no se pudo capturar la imagen de la cámara web.")
                break
            # Procesar la imagen con el modelo
            results = model(frame)

            # Mostrar la imagen procesada
            cv2.imshow('Processed Image', cv2.cvtColor(np.squeeze(results.render()), cv2.COLOR_BGR2RGB))

            # Esperar 5 segundos (5000 milisegundos)
            if cv2.waitKey(1000) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
s
# Ejemplo de uso
capture_and_process_images(model)
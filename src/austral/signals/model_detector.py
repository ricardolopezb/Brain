import torch
import pathlib


class ModelDetector:
    pathlib.WindowsPath = pathlib.PosixPath
    def __init__(self):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path='./best.pt', force_reload=True)


    def detect(self, frame, lookupSignal):
        results = self.model(frame)
        if lookupSignal in str(results):
            print(f"Se encontró la señal '{lookupSignal}'.")
        else:
            print(f"No se encontró la señal '{lookupSignal}'.")

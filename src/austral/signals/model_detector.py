import torch
import pathlib


class ModelDetector:
    pathlib.WindowsPath = pathlib.PosixPath
    def __init__(self):
        self.model = torch.hub.load('src/austral/signals/ultralytics', 'custom', path='./best.pt', force_reload=True, trust_repo=True, source='local')


    def detect(self, frame, lookupSignal):
        results = self.model(frame)
        if lookupSignal in str(results):
            print(f"Se encontró la señal '{lookupSignal}'.")
        else:
            print(f"No se encontró la señal '{lookupSignal}'.")

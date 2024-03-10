import requests

from src.austral.configs import MODEL_API_URL


class DataSender:
    @staticmethod
    def send(endpoint, value):
        response = requests.post(f'{MODEL_API_URL}/{endpoint}', json=value)

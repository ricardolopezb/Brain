import requests


class DataSender:
    @staticmethod
    def send(endpoint, value):
        response = requests.post(f'http://192.168.0.102:5000/{endpoint}', json=value)

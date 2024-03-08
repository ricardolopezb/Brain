import requests


class DataSender:
    @staticmethod
    def send(self, endpoint, value):
        response = requests.post(f'http://192.168.0.101:5000/{endpoint}', data=value)

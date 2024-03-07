import requests


# This would be called in the threadCamera when encoding the frame into .jpg
class ModelRequestSender:
    def send(self, imdata):
        requests.put('http://192.168.0.101:5000/upload', data=imdata.tobytes())
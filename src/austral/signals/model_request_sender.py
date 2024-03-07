import requests


# This would be called in the threadCamera when encoding the frame into .jpg
class ModelRequestSender:
    def send(self, imdata, lookup_sign):
        print("SENDING REQUEST WITH SIGN: ", lookup_sign)
        requests.put(f'http://192.168.0.101:5000/upload/{lookup_sign}', data=imdata.tobytes())
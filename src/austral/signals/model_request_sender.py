import requests

from src.austral.configs import MODEL_API_URL


# This would be called in the threadCamera when encoding the frame into .jpg
class ModelRequestSender:
    def send(self, imdata, lookup_sign):
        response = requests.put(f'{MODEL_API_URL}/upload/{lookup_sign}', data=imdata.tobytes())
        if response.status_code == 200:
            json_response = response.json()
            return json_response
        else:
            print("Error:", response.status_code)
            return None
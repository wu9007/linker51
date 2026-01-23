import requests

class Communicator:
    def __init__(self, base_url):
        self.endpoint = f"{base_url}/vision/update"

    def send_coordinates(self, x, y):
        try:
            params = {'x': x, 'y': y}
            response = requests.get(self.endpoint, params=params, timeout=1)
            return response.status_code == 200
        except Exception:
            return False
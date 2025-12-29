import requests


class GoogleMapsClient:

    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, address):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.api_key
        }
        r = requests.get(url, params=params, timeout=10)
        res = r.json()
        if res.get("status") == "OK":
            loc = res["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
        return None, None

    def driving_distance(self, origin, dest):
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": f"{origin[0]},{origin[1]}",
            "destinations": f"{dest[0]},{dest[1]}",
            "mode": "driving",
            "key": self.api_key
        }
        r = requests.get(url, params=params, timeout=10)
        res = r.json()
        if res.get("status") == "OK":
            row = res["rows"][0]["elements"][0]
            if row.get("status") == "OK":
                return row["distance"]["value"]  # meters
        return None

import requests


class OSRMClient:
    """
    Example URL:
    https://router.project-osrm.org/route/v1/driving/106.700,10.776/106.800,10.780
    """

    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def driving_distance(self, origin, dest):
        lon1, lat1 = origin[1], origin[0]
        lon2, lat2 = dest[1], dest[0]

        url = f"{self.base_url}/driving/{lon1},{lat1};{lon2},{lat2}"
        params = {
            "overview": "false"
        }

        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if data.get("code") == "Ok":
                routes = data.get("routes")
                if routes:
                    return routes[0].get("distance")  # meters
        except Exception:
            return None
        return None

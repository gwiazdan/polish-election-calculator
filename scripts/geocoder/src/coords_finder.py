import requests
from shapely import wkt
from .config import URL


def normalize_teryt(teryt):
    """Normalize TERYT to 6-digit format."""
    try:
        teryt_int = int(float(teryt))
        return str(teryt_int).zfill(6)
    except (ValueError, TypeError):
        return None


def find_address(address, expected_teryt=None):
    """Query GUGiK API for address coordinates."""
    params = {"request": "GetAddress", "address": address}
    try:
        req = requests.get(URL, params=params, timeout=10)
        req.raise_for_status()
        data = req.json()

        if data.get("found objects", 0) > 0 and data.get("results"):
            if expected_teryt:
                expected_teryt_norm = normalize_teryt(expected_teryt)

                for _, result in data["results"].items():
                    result_teryt = result.get("teryt", "")
                    if normalize_teryt(result_teryt) == expected_teryt_norm:
                        return wkt.loads(result["geometry_wkt"])
            # Fallback - take first result
            result = data["results"]["1"]
            return wkt.loads(result["geometry_wkt"])
    except Exception:
        pass

    return None

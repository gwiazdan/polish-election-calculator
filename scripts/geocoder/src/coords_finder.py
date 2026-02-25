import json

import requests
from shapely import wkt
from .config import URL
import sys
from requests import Timeout, RequestException, ConnectionError
from requests.adapters import HTTPAdapter
import re

SESSION = requests.Session()
SESSION.mount("https://", HTTPAdapter(pool_connections=64, pool_maxsize=64))
SESSION.mount("http://", HTTPAdapter(pool_connections=64, pool_maxsize=64))

def normalize_teryt(teryt):
    """Normalize TERYT to 6-digit format."""
    try:
        teryt_int = int(float(teryt))
        teryt_str = str(teryt_int).zfill(6)
        if re.fullmatch(r"1465(0[2-9]|1[0-9])", teryt_str):
            return "146501"
        return teryt_str
    except (ValueError, TypeError):
        return None


def find_address(address, expected_teryt=None):
    """Query GUGiK API for address coordinates."""
    params = {"request": "GetAddress", "address": address}
    for attempt in range(3):
        try:
            req = SESSION.get(URL, params=params, timeout=10)
            req.raise_for_status()
            data = req.json()

            if not req.text.strip():  
                continue

            found_count =  data.get("found objects", 0)
            if isinstance(found_count, int) and found_count > 0 and data.get("results"):
                if expected_teryt:
                    for _, result in data["results"].items():
                        result_teryt = result.get("teryt", "")
                        if normalize_teryt(result_teryt) == expected_teryt:
                            return wkt.loads(result["geometry_wkt"])
                        
                result = data["results"]["1"]
                return wkt.loads(result["geometry_wkt"])
        except json.JSONDecodeError:
            return None
        except (ConnectionError, Timeout, RequestException):
            if attempt == 2:
                sys.exit(1)
        except TypeError:
            raise
    return None

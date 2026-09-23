import requests
from env_variables import getEnvVar

BASE_URL = getEnvVar("METABASE_URL")
API_KEY = getEnvVar("METABASE_API_KEY")

HEADERS = {"x-api-key" : API_KEY}



def api_get(path: str, **kwargs) -> dict:
    resp = requests.get(f"{BASE_URL}{path}", headers=HEADERS, **kwargs)
    if not resp.ok:
        print(f"GET {path} -> {resp.status_code}: {resp.text}")
    resp.raise_for_status()
    return resp.json()

def api_post(path: str, payload: dict) -> dict:
    resp = requests.post(f"{BASE_URL}{path}", headers=HEADERS, json=payload)
    if not resp.ok:
        print(f"POST {path} -> {resp.status_code}: {resp.text}")
    resp.raise_for_status()
    return resp.json()

def api_put(path: str, payload: dict) -> dict:
    resp = requests.put(f"{BASE_URL}{path}", headers=HEADERS, json=payload)
    if not resp.ok:
        print(f"PUT {path} -> {resp.status_code}: {resp.text}")
    resp.raise_for_status()
    return resp.json()
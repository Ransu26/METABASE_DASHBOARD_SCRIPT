import requests

url = "http://localhost:3000/api/card"
headers = {
    "Content-Type": "application/json",
    "x-api-Key": ""
}

payload = {
    "name": "TESTING_v2",
    "dataset_query": {
        "database": 1,
        "type": "native",
        "native": {
            "query": "SELECT SUM(Total * (1 - (Discount/100))) FROM Orders WHERE Discount IS NOT NULL"
        }
    },
    "display": "scalar",
    "visualization_settings": {}
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
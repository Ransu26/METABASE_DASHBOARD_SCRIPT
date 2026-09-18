import requests

url = "http://localhost:3000/api/card"
headers = {
    "Content-Type": "application/json",
    "x-api-Key": ""
}

payload = {
    "name": "TESTING_v3",
    "dataset_query": {
        "database": 1,
        "type": "native",
        "native": {
            "query": "SELECT date(CREATED_AT, 'weekday 0', '-6 days') AS week, COUNT(*) FROM Orders GROUP BY date(CREATED_AT, 'weekday 0', '-6 days') ORDER BY week;"        }
    },
    "display": "line",
    "visualization_settings": {
        "graph.x_axis.scale": "timeseries",
        "graph.metrics": ["COUNT"],
        "graph.dimensions": ["CREATED_AT"]
    }
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
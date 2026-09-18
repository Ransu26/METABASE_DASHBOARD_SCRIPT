import requests

url = "http://localhost:3000/api/card"
headers = {
    "Content-Type": "application/json",
    "x-api-Key": ""
}

payload = {
    "name": "TESTING_v1",
    "dataset_query": {
        "database": 1,
        "type": "native",
        "native": {
            "query": "SELECT Category, COUNT(*) FROM Products GROUP BY Category ORDER BY Category ASC;"
        }
    },
    "display": "bar",
    "visualization_settings": {
        "graph.x_axis.scale": "ordinal",
        "graph.dimensions": ["CATEGORY"],
        "graph.metrics": ["COUNT"]
    }
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
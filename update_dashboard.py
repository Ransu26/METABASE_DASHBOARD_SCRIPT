import requests

base_url = "http://localhost:3000"
headers = {
    "Content-Type": "application/json",
    "x-api-Key": ""
}
cards_payload = {
    "cards": [
        {"id": 1, "card_id": 50, "row": 0, "col": 0, "size_x": 24, "size_y": 6},
        {"id": 2, "card_id": 48, "row": 6, "col": 0, "size_x": 12, "size_y": 6},
        {"id": 3, "card_id": 59, "row": 6, "col": 13, "size_x": 12, "size_y": 6},
    ]
}
resp2 = requests.put(
    f"{base_url}/api/dashboard/7/cards",
    headers=headers,
    json=cards_payload,
)
print("Add cards status:", resp2.status_code)
print(resp2.json())
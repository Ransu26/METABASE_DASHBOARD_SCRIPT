import requests

url = "http://localhost:3000"
headers = {
    "Content-Type": "application/json",
    "x-api-Key": "X-key"
}

# CREATE A COLLECTION FOR THIS DASHBOARDS CARD

colRes = requests.post(url=f"{url}/api/collection", headers=headers, json={"name": "PROTOLARPER COLLECTIONS", "color": "#505050"})
collection = colRes.json()
colID = collection["id"]
print("Add cards status:", colRes.status_code)
print(colRes.json())


cards = ["Total Revenue", "Orders By Category", "Orders Over Time", "Account and Feedback"]
cards_id = []

def card_payload_func(name: str, query: str, display: str, visual_settings: dict | None = None) -> str:
    if visual_settings is None:
        visual_settings = {}
    payload = {
    "name": name,
    "collection_id": colID,
    "dataset_query": {
        "database": 1,
        "type": "native",
        "native": {
            "query": query
        }
    },
    "display": display,
    "visualization_settings": visual_settings
    }
    response = requests.post(url=f"{url}/api/card", headers=headers, json=payload)
    response.raise_for_status()
    card = response.json()
    card_id = card["id"]
    print("Add cards status:", response.status_code)
    print(response.json())
    return card_id
    

# CREATE CARDS
# CARD 1: TOTAL REVENUE
cards_id.append(card_payload_func(
        name= cards[0], 
        query="SELECT SUM(Total * (1 - (Discount/100))) FROM Orders WHERE Discount IS NOT NULL",
        display="scalar",
        visual_settings={}
    ))
# CARD 2: ORDERS BY CATEGORY
cards_id.append(card_payload_func(
        name= cards[1], 
        query="SELECT Category, COUNT(*) AS `Number of Orders` FROM Products GROUP BY Category ORDER BY Category ASC;",
        display="bar",
        visual_settings={
            "graph.x_axis.scale": "ordinal",
            "graph.dimensions": ["Category"],
            "graph.metrics": ["COUNT"]
        }
    ))
# CARD 3: ORDERS OVER TIME
cards_id.append(card_payload_func(
        name= cards[2], 
        query="SELECT date(CREATED_AT, 'weekday 0', '-6 days') AS week, COUNT(*) AS `Number of Orders` FROM Orders GROUP BY date(CREATED_AT, 'weekday 0', '-6 days') ORDER BY week;",
        display="line",
        visual_settings={
            "graph.x_axis.scale": "timeseries",
            "graph.metrics": ["COUNT"],
            "graph.dimensions": ["week"]
        }
    ))
# CARD 4: Accounts with feedback
cards_id.append(card_payload_func(
        name= cards[3], 
        query="SELECT acc.EMAIL AS `Email Address`, acc.FIRST_NAME AS `First Name`, acc.LAST_NAME AS `Last Name`, acc.PLAN AS `Subscribed Plan`, COALESCE(acc.SOURCE, 'N/A') AS Source, fb.RATING AS Rating FROM Accounts AS acc JOIN Feedback AS fb ON acc.EMAIL = fb.EMAIL LIMIT 20;",
        display="table",
        visual_settings={}
    ))

#CREATE COLLECTIONS FOR DASHBOARDS

dashboard_colRes = requests.post(url=f"{url}/api/collection", headers=headers, json={"name": "DASHBOARD COLLECTIONS", "color": "#F4F6F9"})
dashboard_col = dashboard_colRes.json()
dashboard_colID = dashboard_col["id"]
print("Add cards status:", dashboard_colRes.status_code)
print(dashboard_colRes.json())

# CREATE DASHBOARD
dash_payload = {"name": "PROTOLARPER", "collection_id" : dashboard_colID}
resp = requests.post(f"{url}/api/dashboard", headers=headers, json=dash_payload)
dashboard = resp.json()
dashboard_id = dashboard["id"]
print("Add cards status:", resp.status_code)
print(resp.json())
# ADD CARDS TO DASHBOARD

cards_to_add = []
row=0
col=0
sizeX = 24
for i in range(len(cards)):
    if i == 2:
        col+=13
    elif i == 3:
        row += 6
        col = 0
        sizeX = 24
    card = {
        "id": -(i + 1),
        "card_id": cards_id[i],
        "row": row,
        "col": col,
        "size_x": sizeX,
        "size_y": 6
    }
    cards_to_add.append(card)
    row=6
    sizeX = 12

cards_to_payload = {
    "cards": cards_to_add
}

resp2 = requests.put(
    f"{url}/api/dashboard/{dashboard_id}",
    headers=headers,
    json=cards_to_payload,
)

print("Add cards status:", resp2.status_code)
print(resp2.json())
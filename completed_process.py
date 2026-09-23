import requests
import uuid

url = "http://localhost:3000"
headers = {
    "Content-Type": "application/json",
    "x-api-Key": "api_key"
}

def search_Exist(name: str, model: str) -> list:
    response = requests.get(
    f"{url}/api/search",
    headers=headers,
    params={"q": name, "models": model})
    results = response.json().get("data", [])
    return results

def has_Match(name_to_search: str, model: str) -> dict | None:
    data = search_Exist(name_to_search, model)
    exact_match = next((item for item in data if item["name"].lower() == name_to_search.lower()), None)

    return exact_match


def card_payload_func(name: str, query: str, display: str, visual_settings: dict | None = None, template_tags: dict | None = None) -> str:
    if visual_settings is None:
        visual_settings = {}
    native = {
        "query": query
    }
    if template_tags:
        native["template-tags"] = template_tags

    card_id = ""
    payload = {
    "name": name,
    "collection_id": colID,
    "dataset_query": {
        "database": 1,
        "type": "native",
        "native": native
    },
    "display": display,
    "visualization_settings": visual_settings
    }
    card_match_result = has_Match(name, "card")
    if card_match_result:
        card_id = card_match_result["id"]
    else:
        response = requests.post(url=f"{url}/api/card", headers=headers, json=payload)
        response.raise_for_status()
        card = response.json()
        card_id = card["id"]
        print("Add cards status:", response.status_code)
        print(response.json())
    return card_id

def create_widget(name: str, type: str) -> int:
    match_result = has_Match(name, type)
    if match_result:
        return match_result["id"]
    else:
        colRes = requests.post(url=f"{url}/api/{type}", headers=headers, json={"name": name, "color": "#505050"})
        collection = colRes.json()
        print("Add cards status:", colRes.status_code)
        print(colRes.json())
        return collection["id"]

# CREATE A COLLECTION FOR THIS DASHBOARDS CARD

colID = create_widget("PROTOLARPER COLLECTIONS", "collection")

resp = requests.get(f"{url}/api/database/1/metadata", headers=headers)
resp.raise_for_status()
db_metadata = resp.json()

# assume DATABASE_ID found above, e.g. 2
orders_table_id = next(t["id"] for t in db_metadata["tables"] if t["name"] == "ORDERS")
products_table_id = next(t["id"] for t in db_metadata["tables"] if t["name"] == "PRODUCTS")
feedbacks_table_id = next(t["id"] for t in db_metadata["tables"] if t["name"] == "FEEDBACK")


orders_fields = {f["name"]: f["id"] for f in requests.get(f"{url}/api/table/{orders_table_id}/query_metadata", headers=headers).json()["fields"]}
products_fields = {f["name"]: f["id"] for f in requests.get(f"{url}/api/table/{products_table_id}/query_metadata", headers=headers).json()["fields"]}
feedback_fields = {f["name"]: f["id"] for f in requests.get(f"{url}/api/table/{feedbacks_table_id}/query_metadata", headers=headers).json()["fields"]}


created_at_field_id = orders_fields["CREATED_AT"]
category_field_id = products_fields["CATEGORY"]
date_received_field_id = feedback_fields["DATE_RECEIVED"]


cards = ["Total Revenue", "Orders By Category", "Orders Over Time", "Account and Feedback"]
cards_id = []
mappings = {}
    

# CREATE CARDS
# CARD 1: TOTAL REVENUE
card_1_id = card_payload_func(
        name= cards[0], 
        query="SELECT SUM(Total * (1 - (Orders.Discount/100))) FROM Orders JOIN Products ON Orders.PRODUCT_ID = Products.ID WHERE Orders.Discount IS NOT NULL [[AND {{created_at}}]][[ AND {{category}}]]",
        display="scalar",
        visual_settings={},
        template_tags={
            "created_at": {
                "id": str(uuid.uuid4()),
                "name": "created_at",
                "display-name": "Created At",
                "type": "dimension",
                "dimension": ["field", created_at_field_id, None],
                "widget-type": "date/all-options"
            },
            "category": {
                "id": str(uuid.uuid4()),
                "name": "category",
                "display-name": "Category",
                "type": "dimension",
                "dimension": ["field", category_field_id, None],
                "widget-type": "string/="
            }
        }
    )
cards_id.append(card_1_id)
# CARD 2: ORDERS BY CATEGORY
card_2_id = card_payload_func(
        name= cards[1], 
        query="SELECT Products.Category, COUNT(DISTINCT Orders.ID) AS `Number of Orders` FROM Products JOIN Orders ON Products.ID = Orders.PRODUCT_ID WHERE 1 = 1 [[AND {{created_at}}]] [[AND {{category}}]] GROUP BY Products.Category ORDER BY Products.Category ASC;",
        display="bar",
        visual_settings={
            "graph.x_axis.scale": "ordinal",
            "graph.dimensions": ["Category"],
            "graph.metrics": ["COUNT"]
        },
        template_tags={
            "created_at": {
                "id": str(uuid.uuid4()),
                "name": "created_at",
                "display-name": "Created At",
                "type": "dimension",
                "dimension": ["field", created_at_field_id, None],
                "widget-type": "date/all-options"
            },
            "category": {
                "id": str(uuid.uuid4()),
                "name": "category",
                "display-name": "Category",
                "type": "dimension",
                "dimension": ["field", category_field_id, None],
                "widget-type": "string/="
            }
        }
    )
cards_id.append(card_2_id)
# CARD 3: ORDERS OVER TIME
card_3_id = card_payload_func(
        name= cards[2], 
        query="SELECT date(Orders.CREATED_AT, 'weekday 0', '-6 days') AS week, COUNT(*) AS `Number of Orders` FROM Orders JOIN Products ON Products.ID = Orders.PRODUCT_ID WHERE 1 = 1 [[AND {{created_at}}]] [[AND {{category}}]] GROUP BY date(Orders.CREATED_AT, 'weekday 0', '-6 days') ORDER BY week;",
        display="line",
        visual_settings={
            "graph.x_axis.scale": "timeseries",
            "graph.metrics": ["COUNT"],
            "graph.dimensions": ["week"]
        },
        template_tags={
            "created_at": {
                "id": str(uuid.uuid4()),
                "name": "created_at",
                "display-name": "Created At",
                "type": "dimension",
                "dimension": ["field", created_at_field_id, None],
                "widget-type": "date/all-options"
            },
            "category": {
                "id": str(uuid.uuid4()),
                "name": "category",
                "display-name": "Category",
                "type": "dimension",
                "dimension": ["field", category_field_id, None],
                "widget-type": "string/="
            }
        }
    )
cards_id.append(card_3_id)
# CARD 4: Accounts with feedback
card_4_id = card_payload_func(
        name= cards[3], 
        query="""SELECT 
                    Accounts.EMAIL AS `Email Address`, 
                    Accounts.FIRST_NAME AS `First Name`, 
                    Accounts.LAST_NAME AS `Last Name`, 
                    Accounts.PLAN AS `Subscribed Plan`, 
                    COALESCE(Accounts.SOURCE, 'N/A') AS Source, 
                    Feedback.RATING AS Rating, 
                    Feedback.DATE_RECEIVED AS `Date Received` 
                FROM Accounts 
                JOIN Feedback ON Accounts.EMAIL = Feedback.EMAIL 
                WHERE 1 = 1 [[AND {{date_received}}]] 
                LIMIT 20;""",
        display="table",
        visual_settings={},
        template_tags={
            "date_received": {
                "id": str(uuid.uuid4()),
                "name": "date_received",
                "display-name": "Date Received",
                "type": "dimension",
                "dimension": ["field", date_received_field_id, None],
                "widget-type": "date/all-options"
            }
        }
    )
param_id = str(uuid.uuid4())
param_id2 = str(uuid.uuid4())
param_id3 = str(uuid.uuid4())

parameters = [
    {
        "id": param_id,
        "name": "Created At",
        "slug": "created_at",
        "type": "date/all-options",
        "sectionId": "date"
    },
    {
        "id": param_id2,
        "name": "Category",
        "slug": "category",
        "type": "string/=",
        "sectionId": "string"
    },
    {
        "id": param_id3,
        "name": "Date Received",
        "slug": "date_received",
        "type": "date/all-options",
        "sectionId": "date"
    }
]
mappings[card_1_id] = [
    {
        "parameter_id": param_id,
        "card_id": card_1_id,
        "target": ["dimension", ["template-tag", "created_at"]]
    },
    {
        "parameter_id": param_id2,
        "card_id": card_1_id,
        "target": ["dimension", ["template-tag", "category"]]
    }
]
mappings[card_2_id] = [
    {
        "parameter_id": param_id,
        "card_id": card_2_id,
        "target": ["dimension", ["template-tag", "created_at"]]
    },
    {
        "parameter_id": param_id2,
        "card_id": card_2_id,
        "target": ["dimension", ["template-tag", "category"]]
    }
]
mappings[card_3_id] = [
    {
        "parameter_id": param_id,
        "card_id": card_3_id,
        "target": ["dimension", ["template-tag", "created_at"]]
    },
    {
        "parameter_id": param_id2,
        "card_id": card_3_id,
        "target": ["dimension", ["template-tag", "category"]]
    }
]
mappings[card_4_id] = [
    {
        "parameter_id": param_id,
        "card_id": card_4_id,
        "target": ["dimension", ["template-tag", "date_received"]]
    }
]
cards_id.append(card_4_id)

#CREATE COLLECTIONS FOR DASHBOARDS
dashboard_colID = create_widget("DASHBOARD COLLECTIONS", "collection")

# CREATE DASHBOARD
dashboard_id = create_widget("PROTOLARPER", "dashboard")
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
    id = (i + 1) if has_Match("PROTOLARPER", "dashboard") else -(i + 1)
    card = {
        "id": id,
        "card_id": cards_id[i],
        "row": row,
        "col": col,
        "size_x": sizeX,
        "size_y": 6,
        "parameter_mappings": mappings.get(cards_id[i], [])

    }
    cards_to_add.append(card)
    row=6
    sizeX = 12

cards_to_payload = {
    "parameters": parameters,
    "dashcards": cards_to_add
}

resp2 = requests.put(
    f"{url}/api/dashboard/{dashboard_id}",
    headers=headers,
    json=cards_to_payload,
)

print("Add cards status:", resp2.status_code)
print(resp2.json())
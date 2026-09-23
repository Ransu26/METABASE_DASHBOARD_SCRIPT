import get_create_helpers as gch
import api_helpers as req
from env_variables import getEnvVar
from parameter_registry import ParameterRegistry, make_dimension_tag

DASHBOARD_NAME = "PROTOLARPER"
CARD_COLLECTION_NAME = "PROTOLARPER COLLECTIONS"
DASHBOARD_COLLECTION_NAME = "DASHBOARD COLLECTIONS"

db_id = int(getEnvVar("METABASE_DATABASE_ID"))

def main():
    card_collection_id = gch.get_create_collection(CARD_COLLECTION_NAME)
    dashboard_collection_id = gch.get_create_collection(DASHBOARD_COLLECTION_NAME)

    db_metadata = req.api_get(f"/api/database/{db_id}/metadata")

    order_table_id = gch.find_table_id(db_metadata, "ORDERS")
    product_table_id = gch.find_table_id(db_metadata, "PRODUCTS")
    feedback_table_id = gch.find_table_id(db_metadata, "FEEDBACK")

    order_fields = gch.get_fields_ids(order_table_id)
    product_fields = gch.get_fields_ids(product_table_id)
    feedback_fields = gch.get_fields_ids(feedback_table_id)

    created_at_field_id = order_fields["CREATED_AT"]
    category_field_id = product_fields["CATEGORY"]
    date_received_field_id = feedback_fields["DATE_RECEIVED"]

    registry = ParameterRegistry()

    created_at_param_id = registry.get_or_create("Created At", "created_at", "date/all-options", "date")
    category_param_id = registry.get_or_create("Category", "category", "string/=", "string")
    date_received_param_id = registry.get_or_create("Date Received", "date_received", "date/all-options", "date")

    card_defs = [
        {
            "name": "Total Revenue",
            "query": ("""
                SELECT
                    SUM(Total * (1 - (Orders.Discount/100))) 
                FROM Orders 
                JOIN Products ON Orders.PRODUCT_ID = Products.ID 
                WHERE Orders.Discount IS NOT NULL [[AND {{created_at}}]][[ AND {{category}}]]
            """),
            "display": "scalar",
            "visualization_settings": {},
            "template_tags": {
                "created_at": make_dimension_tag(
                    "created_at", 
                    "Created At", 
                    created_at_field_id, 
                    "date/all-options"),
                "category":  make_dimension_tag(
                    "category",
                    "Category",
                    category_field_id,
                    "string/=",
                )
            },
            "mappings": [
                {"parameter_id": created_at_param_id, "target": ["dimension", ["template-tag", "created_at"]]},
                {"parameter_id": category_param_id, "target": ["dimension", ["template-tag", "category"]]}
            ],
            "layout": {"row": 0, "col": 0, "size_x": 24, "size_y": 6}
        },
        {
            "name": "Orders By Category",
            "query": ("""
                SELECT 
                    Products.Category, 
                    COUNT(DISTINCT Orders.ID) AS `Number of Orders` 
                FROM Products 
                JOIN Orders ON Products.ID = Orders.PRODUCT_ID 
                WHERE 1 = 1 [[AND {{created_at}}]] [[AND {{category}}]] 
                GROUP BY Products.Category 
                ORDER BY Products.Category ASC;
            """),
            "display": "bar",
            "visualization_settings": {
                "graph.x_axis.scale": "ordinal",
                "graph.dimensions": ["Category"],
                "graph.metrics": ["COUNT"]
            },
            "template_tags": {
                "created_at": make_dimension_tag(
                    "created_at",
                    "Created At",
                    created_at_field_id,
                    "date/all-options"
                ),
                "category": make_dimension_tag(
                    "category",
                    "Category",
                    category_field_id,
                    "string/="
                )
            },
            "mappings": [
                {"parameter_id": created_at_param_id, "target": ["dimension", ["template-tag", "created_at"]]},
                {"parameter_id": category_param_id, "target": ["dimension", ["template-tag", "category"]]}
            ],
            "layout": {"row": 6, "col": 0, "size_x": 12, "size_y": 6}
        },
        {
            "name": "Orders Over Time",
            "query": ("""
                SELECT 
                    date(Orders.CREATED_AT, 'weekday 0', '-6 days') AS week, 
                    COUNT(*) AS `Number of Orders` 
                FROM Orders 
                JOIN Products ON Products.ID = Orders.PRODUCT_ID 
                WHERE 1 = 1 [[AND {{created_at}}]] [[AND {{category}}]] 
                GROUP BY date(Orders.CREATED_AT, 'weekday 0', '-6 days') 
                ORDER BY week;
            """),
            "display": "line",
            "visualization_settings": {
                "graph.x_axis.scale": "timeseries",
                "graph.metrics": ["COUNT"],
                "graph.dimensions": ["week"]
            },
            "template_tags": {
                "created_at": make_dimension_tag(
                    "created_at",
                    "Created At",
                    created_at_field_id,
                    "date/all-options"
                ),
                "category": make_dimension_tag(
                    "category",
                    "Category",
                    category_field_id,
                    "string/="
                )
            },
            "mappings": [
                {"parameter_id": created_at_param_id, "target": ["dimension", ["template-tag", "created_at"]]},
                {"parameter_id": category_param_id, "target": ["dimension", ["template-tag", "category"]]}
            ],
            "layout": {"row": 6, "col": 13, "size_x": 12, "size_y": 6}
        },
        {
            "name": "Account and Feedback",
            "query": ("""
                SELECT 
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
                LIMIT 20;
            """),
            "display": "table",
            "visualization_settings": {},
            "template_tags": {
                "date_received": make_dimension_tag(
                    "date_received",
                    "Date Received",
                    date_received_field_id,
                    "date/all-options"
                )
            },
            "mappings": [
                {"parameter_id": date_received_param_id, "target": ["dimension", ["template-tag", "date_received"]]}
            ],
            "layout": {"row": 12, "col": 0, "size_x": 24, "size_y": 6}
        }
    ]

    for card_def in card_defs:
        dateset_query = {
            "database": db_id,
            "type": "native",
            "native": {
                "query": card_def["query"],
                "template-tags": card_def["template_tags"],
            },
        }

        card_def["card_id"] = gch.create_card(
            name=card_def["name"],
            dataset_query=dateset_query,
            display=card_def["display"],
            visual_settings=card_def["visualization_settings"],
            collection_id=card_collection_id
        )
        print(f"Card '{card_def['name']}' ->  id {card_def['card_id']}")

    dashbord_id, dashboard_existed = gch.get_create_dashboard(DASHBOARD_NAME, dashboard_collection_id)
    print(f"Dashboard '{DASHBOARD_NAME}' -> id {dashbord_id} (existed: {dashboard_existed})")

    dashcards = []

    for i, card_def in enumerate(card_defs):
        layout = card_def["layout"]
        parameter_mappings = [
            {
                "parameter_id": m["parameter_id"],
                "card_id": card_def["card_id"],
                "target": m["target"]
            }
            for m in card_def["mappings"]
        ]
        dashcards.append({
            "id": -(i + 1),
            "card_id": card_def["card_id"],
            "row": layout["row"],
            "col": layout["col"],
            "size_x": layout["size_x"],
            "size_y": layout["size_y"],
            "parameter_mappings": parameter_mappings
        })

    payload = {
        "parameters": registry.parameters,
        "dashcards": dashcards
    }

    result = req.api_put(f"/api/dashboard/{dashbord_id}", payload)
    print("Dashboard updated:", result.get("id"), "-", len(result.get("dashcards", [])), "dashcards")

    # resp = req.api_get(f"/api/dashboard/30")
    # for dc in resp["dashcards"]:
    #     if dc["card_id"] == card_defs[0]["card_id"]:  # Total Revenue
    #         print(dc["parameter_mappings"])
    # for p in registry.parameters:
    #     print(p)
if __name__ == "__main__":
    print("inside 1")
    main()
    print("inside 2")
else:
    print("boomboy")
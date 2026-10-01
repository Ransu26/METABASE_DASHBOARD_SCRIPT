import get_create_helpers as gch
import api_helpers as req
from env_variables import getEnvVar
from parameter_registry import ParameterRegistry
from card_definitions import build_card_defs
from model_definitions import build_model_defs

DASHBOARD_NAME = "PROTOLARPER"
CARD_COLLECTION_NAME = "PROTOLARPER COLLECTIONS"
DASHBOARD_COLLECTION_NAME = "DASHBOARD COLLECTIONS"
MODEL_COLLECTION_NAME = "MODEL COLLECTIONS"

db_id = int(getEnvVar("METABASE_DATABASE_ID"))

def main():
    card_collection_id = gch.get_create_collection(CARD_COLLECTION_NAME)
    dashboard_collection_id = gch.get_create_collection(DASHBOARD_COLLECTION_NAME)
    model_collection_id = gch.get_create_collection(MODEL_COLLECTION_NAME)

    db_metadata = req.api_get(f"/api/database/{db_id}/metadata")

    order_table_id = gch.find_table_id(db_metadata, "ORDERS")
    product_table_id = gch.find_table_id(db_metadata, "PRODUCTS")
    feedback_table_id = gch.find_table_id(db_metadata, "FEEDBACK")

    order_fields = gch.get_fields_ids(order_table_id)
    product_fields = gch.get_fields_ids(product_table_id)
    feedback_fields = gch.get_fields_ids(feedback_table_id)

    field_ids = {
    "created_at": order_fields["CREATED_AT"],
    "category": product_fields["CATEGORY"],
    "date_received": feedback_fields["DATE_RECEIVED"]
    }

    registry = ParameterRegistry()

    param_ids = {
    "created_at": registry.get_or_create("Created At", "created_at", "date/all-options", "date"),
    "category": registry.get_or_create("Category", "category", "string/=", "string"),
    "date_received": registry.get_or_create("Date Received", "date_received", "date/all-options", "date")
    }

    model_defs = build_model_defs()
    models_ids = {}

    for model_def in model_defs:
        model_def["card_id"] = gch.create_card(
            name=model_def["name"],
            dataset_query = {
                "database": db_id,
                "type": "native",
                "native": {"query": model_def["query"]}
            },
            display=model_def["display"],
            card_type=model_def["type"],
            search_type=model_def["search_key"],
            visual_settings=model_def["visualization_settings"],
            collection_id=model_collection_id,
            result_metadata=None,
        )

        models_ids[model_def["key"]] = model_def["card_id"]
        print(f"Model '{model_def['name']}' -> id {model_def['card_id']}")


    card_defs = build_card_defs(field_ids=field_ids, param_ids=param_ids, model_id=models_ids)

    for card_def in card_defs:
        native = {
            "query": card_def["query"],
            "template-tags": card_def["template_tags"],
        }

        result_metadata = gch.run_native_query_for_metadata(native, db_id)

        card_def["card_id"] = gch.create_card(
            name=card_def["name"],
            dataset_query={
                "database": db_id,
                "type": "native",
                "native": native
            },
            card_type=card_def["type"],
            search_type=card_def["search_key"],
            display=card_def["display"],
            visual_settings=card_def["visualization_settings"],
            collection_id=card_collection_id,
            result_metadata=result_metadata
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
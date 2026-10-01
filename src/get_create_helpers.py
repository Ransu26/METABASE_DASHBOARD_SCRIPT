import api_helpers as req

def search_exists(name: str, model: str) -> dict:
    return req.api_get("/api/search", params={"q": name, "models": model}).get("data", [])

def has_exact_match(name: str, model: str) -> dict | None:
    return next(
        (item for item in search_exists(name, model) if item["name"].lower() == name.lower()), None
    )

def get_create_collection(name: str) -> int:
    match_result = has_exact_match(name, "collection")
    if match_result:
        return match_result["id"]
    created = req.api_post("/api/collection", {"name": name, "color": "#505050"})
    return created["id"]

def get_create_dashboard(name: str, collection_id: int) -> tuple[int, bool]:
    match_result = has_exact_match(name, "dashboard")
    if match_result:
        return match_result["id"], True
    created = req.api_post("/api/dashboard", {"name": name, "collection_id": collection_id})
    return created["id"], False

def create_card(
        name: str, 
        dataset_query: dict, 
        display: str, 
        card_type: str,
        search_type: str,
        visual_settings: dict, 
        collection_id: int,
        result_metadata: dict = None) -> int:
    match_result = has_exact_match(name, search_type)
    if match_result:
        return match_result["id"]
    payload = {
        "name": name,
        "collection_id": collection_id,
        "type": card_type,
        "dataset_query": dataset_query,
        "display": display,
        "visualization_settings": visual_settings,
        "result_metadata": result_metadata
    }
    created = req.api_post("/api/card", payload)
    return created["id"]

def find_table_id(db_metadata: dict, table_name: str) -> int:
    return next(
        (t["id"] for t in db_metadata["tables"] if t["name"] == table_name)
    )

def get_fields_ids(table_id: int) -> int:
    fields = req.api_get(f"/api/table/{table_id}/query_metadata")["fields"]
    return {f["name"]: f["id"] for f in fields}

def run_native_query_for_metadata(native: dict, database_id: int) -> list[dict]:
    """
    native: {"query": "...", "template-tags": {...}}  (template-tags optional)
    Runs the query ad-hoc so Metabase computes column metadata, to attach
    at card-creation time. Required for both models AND any question built
    on top of a model/native question - without it, Metabase can't resolve
    columns or connect dashboard parameters correctly.
    """
    payload = {
        "type": "native",
        "native": native,
        "database": database_id,
    }
    result = req.api_post("/api/dataset", payload)
    return result["data"]["results_metadata"]["columns"]



def build_model_defs() -> list[dict]:
    return [
        {
            "key": "orders_products",
            "name": "Orders + Products Model",
            "query": (
                "SELECT Orders.*, Products.Category "
                "FROM Orders JOIN Products ON Orders.PRODUCT_ID = Products.ID "
            ),
            "type": "model",
            "search_key": "dataset",
            "display": "table",
            "visualization_settings": {},
        },
        {
            "key": "accounts_feedback",
            "name": "Accounts + Feedback Model",
            "query": ("""
                SELECT
                    Accounts.*,
                    Feedback.*
                FROM Accounts
                JOIN Feedback ON Accounts.EMAIL = Feedback.EMAIL
            """),
            "type": "model",
            "search_key": "dataset",
            "display": "table",
            "visualization_settings": {}
        }
    ]
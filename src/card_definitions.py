from parameter_registry import make_dimension_tag, make_card_reference_tag

def build_card_defs(field_ids: dict, param_ids: dict, model_id: dict) -> list[dict]:

    orders_model_id = model_id["orders_products"]
    accounts_model_id = model_id["accounts_feedback"]

    orders_ref_tag_name, orders_ref_tag = make_card_reference_tag(orders_model_id)
    accounts_ref_tag_name, accounts_ref_tag = make_card_reference_tag(accounts_model_id)

    created_at_field_id = field_ids["created_at"]
    category_field_id = field_ids["category"]
    date_received_field_id = field_ids["date_received"]
 
    created_at_param_id = param_ids["created_at"]
    category_param_id = param_ids["category"]
    date_received_param_id = param_ids["date_received"]

    return [
        {
                    "name": "Total Revenue",
                    "type": "question",
                    "search_key": "card",
                    "query": (f"""
                        SELECT
                            SUM(Total * (1 - (Discount/100))) 
                        FROM  {{{{{orders_ref_tag_name}}}}}
                        WHERE Discount IS NOT NULL [[AND {{{{created_at}}}}]][[ AND {{{{category}}}}]]
                    """),
                    "display": "scalar",
                    "visualization_settings": {},
                    "template_tags": {
                        orders_ref_tag_name: orders_ref_tag, 
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
                    "type": "question",
                    "search_key": "card",
                    "query": (f"""
                        SELECT 
                            Category, 
                            COUNT(DISTINCT ID) AS `Number of Orders` 
                        FROM {{{{{orders_ref_tag_name}}}}}
                        WHERE 1 = 1 [[AND {{{{created_at}}}}]] [[AND {{{{category}}}}]] 
                        GROUP BY Category 
                        ORDER BY Category ASC;
                    """),
                    "display": "bar",
                    "visualization_settings": {
                        "graph.x_axis.scale": "ordinal",
                        "graph.dimensions": ["Category"],
                        "graph.metrics": ["COUNT"]
                    },
                    "template_tags": {
                        orders_ref_tag_name: orders_ref_tag, 
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
                    "type": "question",
                    "search_key": "card",
                    "query": (f"""
                        SELECT 
                            date(CREATED_AT, 'weekday 0', '-6 days') AS week, 
                            COUNT(*) AS `Number of Orders` 
                        FROM {{{{{orders_ref_tag_name}}}}}
                        WHERE 1 = 1 [[AND {{{{created_at}}}}]] [[AND {{{{category}}}}]] 
                        GROUP BY date(CREATED_AT, 'weekday 0', '-6 days') 
                        ORDER BY week;
                    """),
                    "display": "line",
                    "visualization_settings": {
                        "graph.x_axis.scale": "timeseries",
                        "graph.metrics": ["COUNT"],
                        "graph.dimensions": ["week"]
                    },
                    "template_tags": {
                        orders_ref_tag_name: orders_ref_tag, 
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
                    "type": "question",
                    "search_key": "card",
                    "query": (f"""
                        SELECT 
                            EMAIL AS `Email Address`, 
                            FIRST_NAME AS `First Name`, 
                            LAST_NAME AS `Last Name`, 
                            PLAN AS `Subscribed Plan`, 
                            COALESCE(SOURCE, 'N/A') AS Source, 
                            RATING AS Rating, 
                            DATE_RECEIVED AS `Date Received` 
                        FROM {{{{{accounts_ref_tag_name}}}}}
                        WHERE 1 = 1 [[AND {{{{date_received}}}}]] 
                        LIMIT 20;
                    """),
                    "display": "table",
                    "visualization_settings": {},
                    "template_tags": {
                        accounts_ref_tag_name: accounts_ref_tag, 
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
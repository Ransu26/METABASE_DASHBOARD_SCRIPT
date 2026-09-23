import pytest
import os
from src.env_variables import getEnvVar
import src.api_helpers as req

pytestmark = pytest.mark.skipif(
    not os.environ.get("METABASE_RUN_INTEGRATION_TEST"),
    reason="set METABASE_RUN_INTEGRATION_TEST=1 to run against a live metabase instance", 
)

DB_ID = int(getEnvVar("METABASE_DATABASE_ID"))

def run_native_query(sql: str) -> dict:
    payload = {
        "type": "native",
        "native": {"query": sql},
        "database": DB_ID
    }
    return req.api_post("/api/dataset", payload)

def get_rows(sql: str) -> list:
    result = run_native_query(sql)
    return result["data"]["rows"]

def get_cols(sql: str) -> list:
    result = run_native_query(sql)
    return [c["name"] for c in result["data"]["cols"]]


#TOTAL REVENUE
def test_total_revenue_query_runs_without_errors():
    rows = get_rows("""
        SELECT 
            SUM(Orders.Total * (1 - (Orders.Discount/100))) 
        FROM Orders 
        JOIN Products ON Orders.PRODUCT_ID = Products.ID 
        WHERE Orders.Discount IS NOT NULL
    """)
    assert len(rows) == 1
    assert rows[0][0] is not None

def test_total_revenue_is_non_negative():
    rows = get_rows("""
        SELECT 
            SUM(Total * (1 - (Orders.Discount/100))) 
        FROM Orders 
        JOIN Products ON Orders.PRODUCT_ID = Products.ID 
        WHERE Orders.Discount IS NOT NULL
    """)
    assert rows[0][0] >= 0

def discount_is_not_null_filter_no_drop_revenue():
    card_query_total = get_rows("""
        SELECT 
            SUM(Total * (1 - (Orders.Discount/100))) 
        FROM Orders 
        JOIN Products ON Orders.PRODUCT_ID = Products.ID 
        WHERE Orders.Discount IS NOT NULL        
    """)[0][0]

    coalesced_query = get_rows("""
        SELECT 
            SUM(Orders.Total * (1 - (COALESCED(Orders.Discount, 0)/100))) 
        FROM Orders 
        JOIN Products ON Orders.PRODUCT_ID = Products.ID 
    """)[0][0]

    null_discount_order_count = get_rows("""
        SELECT COUNT(*) FROM Orders WHERE Discount IS NULL
    """)[0][0]

    if null_discount_order_count > 0:
        assert card_query_total == coalesced_query, (
            f"{null_discount_order_count} orders have a NULL discount and are "
            f"being excluded by the card's WHERE clause. Card total: "
            f"{card_query_total}, total if NULL-discount orders were included "
            f"at full price: {coalesced_query}. If these should count as "
            f"'no discount applied', the card's query needs COALESCE instead "
            f"of a NOT NULL filter."
        )

def test_orders_by_category_columns():
    cols = get_cols("""
        SELECT Products.Category AS Category, COUNT(DISTINCT Orders.ID) AS "Number of Orders"
        FROM Products JOIN Orders ON Products.ID = Orders.PRODUCT_ID
        GROUP BY Products.Category
    """)
    assert "Category" in cols
    assert "Number of Orders" in cols
 
 
def test_orders_by_category_distinct_matches_ungrouped_total():
    """
    Sanity check: summing COUNT(DISTINCT Orders.ID) across all categories
    should equal the total distinct order count (i.e. the join to Products
    isn't fanning out and inflating counts, and every order has exactly one
    category).
    """
    grouped_rows = get_rows("""
        SELECT Products.Category, COUNT(DISTINCT Orders.ID)
        FROM Products JOIN Orders ON Products.ID = Orders.PRODUCT_ID
        GROUP BY Products.Category
    """)
    grouped_sum = sum(row[1] for row in grouped_rows)
 
    total_orders = get_rows("""
        SELECT COUNT(DISTINCT Orders.ID)
        FROM Products JOIN Orders ON Products.ID = Orders.PRODUCT_ID
    """)[0][0]
 
    assert grouped_sum == total_orders, (
        f"Sum of per-category counts ({grouped_sum}) does not match total "
        f"distinct order count ({total_orders}) - suggests a join fan-out "
        f"or an order matching multiple categories."
    )
 
 
# ---------------------------------------------------------------------------
# Card 3: Orders Over Time
# ---------------------------------------------------------------------------
 
def test_orders_over_time_date_function_runs():
    """
    The 'weekday 0'/'-6 days' modifiers are SQLite-specific date() syntax.
    This test's main purpose is to fail loudly and immediately if the
    connected database engine doesn't support this syntax, rather than
    letting it fail silently inside a dashboard card.
    """
    try:
        rows = get_rows("""
            SELECT date(Orders.CREATED_AT, 'weekday 0', '-6 days') AS week, COUNT(*)
            FROM Orders
            GROUP BY date(Orders.CREATED_AT, 'weekday 0', '-6 days')
            ORDER BY week
            LIMIT 5
        """)
    except Exception as e:
        pytest.fail(
            f"Orders Over Time query failed - likely a database-engine mismatch "
            f"with SQLite-specific date() modifiers. Confirm which engine "
            f"database id {DB_ID} actually uses. Original error: {e}"
        )
    assert len(rows) > 0
 
 
def test_orders_over_time_counts_sum_to_total():
    grouped_rows = get_rows("""
        SELECT date(Orders.CREATED_AT, 'weekday 0', '-6 days') AS week, COUNT(*)
        FROM Orders
        GROUP BY date(Orders.CREATED_AT, 'weekday 0', '-6 days')
    """)
    grouped_sum = sum(row[1] for row in grouped_rows)
    total = get_rows("SELECT COUNT(*) FROM Orders")[0][0]
    assert grouped_sum == total
 
 
# ---------------------------------------------------------------------------
# Card 4: Account and Feedback
# ---------------------------------------------------------------------------
 
def test_account_feedback_join_does_not_duplicate_rows():
    """
    If an account has multiple feedback rows, the join is expected to
    produce one output row per feedback entry (that's normal). But if an
    account with a SINGLE feedback row shows up more than once, that
    signals the join key isn't as unique as assumed.
    """
    rows = get_rows("""
        SELECT Accounts.EMAIL, Feedback.DATE_RECEIVED, COUNT(*)
        FROM Accounts JOIN Feedback ON Accounts.EMAIL = Feedback.EMAIL
        GROUP BY Accounts.EMAIL, Feedback.DATE_RECEIVED
        HAVING COUNT(*) > 1
    """)
    assert rows == [], (
        f"{len(rows)} (email, date_received) pairs appear more than once - "
        f"the EMAIL join key may not uniquely identify feedback entries, "
        f"which could inflate row counts on the dashboard card."
    )
 


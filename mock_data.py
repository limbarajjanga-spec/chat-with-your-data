import pandas as pd
import sqlite3

MOCK_SCHEMA = {
    "sales": {
        "description": "Monthly sales transactions by product and region",
        "columns": {
            "order_id": "INTEGER",
            "order_date": "DATE",
            "product_name": "TEXT",
            "category": "TEXT",
            "region": "TEXT",
            "sales_rep": "TEXT",
            "quantity": "INTEGER",
            "unit_price": "REAL",
            "revenue": "REAL",
            "discount": "REAL",
        },
    },
    "customers": {
        "description": "Customer master data with segments and demographics",
        "columns": {
            "customer_id": "INTEGER",
            "customer_name": "TEXT",
            "segment": "TEXT",
            "country": "TEXT",
            "city": "TEXT",
            "join_date": "DATE",
            "lifetime_value": "REAL",
        },
    },
    "products": {
        "description": "Product catalog with categories and cost info",
        "columns": {
            "product_id": "INTEGER",
            "product_name": "TEXT",
            "category": "TEXT",
            "sub_category": "TEXT",
            "cost": "REAL",
            "list_price": "REAL",
            "stock_quantity": "INTEGER",
        },
    },
}

def seed_database(conn):
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sales (
            order_id INTEGER PRIMARY KEY,
            order_date DATE,
            product_name TEXT,
            category TEXT,
            region TEXT,
            sales_rep TEXT,
            quantity INTEGER,
            unit_price REAL,
            revenue REAL,
            discount REAL
        );
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT,
            segment TEXT,
            country TEXT,
            city TEXT,
            join_date DATE,
            lifetime_value REAL
        );
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            sub_category TEXT,
            cost REAL,
            list_price REAL,
            stock_quantity INTEGER
        );
    """)

    import random, datetime
    random.seed(42)

    categories = {
        "Technology": ["Laptop Pro", "Wireless Mouse", "USB Hub", "Monitor 4K", "Keyboard Mech"],
        "Furniture": ["Standing Desk", "Ergonomic Chair", "Bookshelf", "Filing Cabinet", "Whiteboard"],
        "Office Supplies": ["Sticky Notes", "Ballpoint Pens", "Stapler", "Paper Ream", "Binder Set"],
    }
    regions = ["North", "South", "East", "West"]
    reps = ["Alice Kim", "Bob Patel", "Carlos Ruiz", "Diana Chen", "Ethan Brooks"]

    sales_rows = []
    for i in range(1, 501):
        cat = random.choice(list(categories.keys()))
        prod = random.choice(categories[cat])
        qty = random.randint(1, 20)
        price = round(random.uniform(10, 500), 2)
        disc = round(random.uniform(0, 0.25), 2)
        rev = round(qty * price * (1 - disc), 2)
        date = datetime.date(2024, random.randint(1, 12), random.randint(1, 28))
        sales_rows.append((i, date.isoformat(), prod, cat, random.choice(regions),
                           random.choice(reps), qty, price, rev, disc))
    cursor.executemany("INSERT OR IGNORE INTO sales VALUES (?,?,?,?,?,?,?,?,?,?)", sales_rows)

    segments = ["Enterprise", "SMB", "Startup", "Government"]
    countries = ["USA", "UK", "Germany", "India", "Canada"]
    cities = ["New York", "London", "Berlin", "Mumbai", "Toronto"]
    customer_rows = []
    for i in range(1, 101):
        join = datetime.date(2020 + random.randint(0, 3), random.randint(1, 12), random.randint(1, 28))
        customer_rows.append((i, f"Customer_{i:03d}", random.choice(segments),
                              random.choice(countries), random.choice(cities),
                              join.isoformat(), round(random.uniform(500, 50000), 2)))
    cursor.executemany("INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?,?,?)", customer_rows)

    product_rows = []
    pid = 1
    for cat, prods in categories.items():
        for p in prods:
            cost = round(random.uniform(5, 200), 2)
            price = round(cost * random.uniform(1.3, 2.5), 2)
            product_rows.append((pid, p, cat, cat + " Supplies", cost, price, random.randint(0, 500)))
            pid += 1
    cursor.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?,?,?)", product_rows)

    conn.commit()


def get_connection():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    seed_database(conn)
    return conn
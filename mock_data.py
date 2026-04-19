import pandas as pd
import sqlite3
import random

MOCK_SCHEMA = {
    "ev_market": {
        "description": "Electric vehicle sales, charging infrastructure, and battery metrics by region",
        "columns": {
            "record_id": "INTEGER",
            "region": "TEXT",
            "country": "TEXT",
            "manufacturer": "TEXT",
            "model": "TEXT",
            "segment": "TEXT",           # Sedan / SUV / Truck / Hatchback
            "units_sold": "INTEGER",
            "avg_range_km": "INTEGER",
            "battery_kwh": "REAL",
            "charge_time_min": "INTEGER", # 10-80% DC fast charge
            "msrp_usd": "REAL",
            "quarter": "TEXT",            # 2024-Q1 … 2025-Q2
            "charging_stations_nearby": "INTEGER",
            "govt_subsidy_usd": "REAL",
            "customer_rating": "REAL",    # 1.0 - 5.0
            "warranty_years": "INTEGER",
        },
    }
}


def seed_database(conn):
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS ev_market (
            record_id INTEGER PRIMARY KEY,
            region TEXT,
            country TEXT,
            manufacturer TEXT,
            model TEXT,
            segment TEXT,
            units_sold INTEGER,
            avg_range_km INTEGER,
            battery_kwh REAL,
            charge_time_min INTEGER,
            msrp_usd REAL,
            quarter TEXT,
            charging_stations_nearby INTEGER,
            govt_subsidy_usd REAL,
            customer_rating REAL,
            warranty_years INTEGER
        );
    """)

    rng = random.Random(42)

    # manufacturer -> [(model, segment, range_km, battery_kwh, charge_min, msrp, warranty)]
    ev_catalog = {
        "Tesla": [
            ("Model Y",    "SUV",      500, 77,  25, 47_990, 8),
            ("Model 3",    "Sedan",    570, 75,  22, 40_240, 8),
            ("Model S",    "Sedan",    650, 100, 20, 74_990, 8),
            ("Model X",    "SUV",      560, 100, 20, 79_990, 8),
            ("Cybertruck", "Truck",    480, 123, 30, 79_990, 8),
        ],
        "BYD": [
            ("Atto 3",  "SUV",    420, 60, 30, 35_000, 6),
            ("Han EV",  "Sedan",  550, 85, 28, 42_000, 6),
            ("Seal",    "Sedan",  510, 82, 26, 38_500, 6),
            ("Tang EV", "SUV",    400, 108, 35, 48_000, 6),
            ("Dolphin", "Hatchback", 340, 44, 40, 25_000, 6),
        ],
        "Hyundai": [
            ("Ioniq 6", "Sedan", 610, 77, 18, 38_615, 5),
            ("Ioniq 5", "SUV",   480, 72, 18, 41_450, 5),
            ("Kona EV", "SUV",   490, 65, 45, 33_550, 5),
        ],
        "Volkswagen": [
            ("ID.4",  "SUV",   520, 77, 28, 38_995, 5),
            ("ID.7",  "Sedan", 610, 91, 26, 54_995, 5),
            ("ID.3",  "Hatchback", 420, 58, 35, 28_500, 5),
        ],
        "Rivian": [
            ("R1T", "Truck", 483, 135, 35, 67_500, 5),
            ("R1S", "SUV",   450, 135, 35, 72_500, 5),
        ],
        "BMW": [
            ("iX3", "SUV",   460, 74, 32, 54_100, 5),
            ("i4",  "Sedan", 590, 83, 27, 56_400, 5),
            ("iX",  "SUV",   630, 111, 35, 87_100, 5),
        ],
        "Mercedes": [
            ("EQS", "Sedan", 770, 108, 31, 104_400, 4),
            ("EQB", "SUV",   419, 66,  32, 53_900, 4),
            ("EQE", "Sedan", 617, 90,  31, 74_900, 4),
        ],
        "GM / Chevrolet": [
            ("Silverado EV", "Truck", 640, 200, 40, 74_800, 3),
            ("Equinox EV",   "SUV",   483, 78,  37, 34_995, 3),
            ("Blazer EV",    "SUV",   515, 85,  35, 44_995, 3),
        ],
        "Stellantis": [
            ("Jeep Avenger",  "SUV",      400, 54, 30, 36_000, 3),
            ("Fiat 500e",     "Hatchback",320, 42, 35, 32_500, 3),
            ("Ram 1500 REV",  "Truck",    560, 168, 40, 58_000, 3),
        ],
        "Nio": [
            ("ET7",  "Sedan", 580, 100, 20, 69_000, 5),
            ("ES6",  "SUV",   450, 100, 20, 54_000, 5),
            ("EC7",  "SUV",   490, 100, 20, 58_000, 5),
        ],
    }

    regions_map = {
        "USA":         "North America",
        "Canada":      "North America",
        "Mexico":      "North America",
        "Germany":     "Europe",
        "Norway":      "Europe",
        "UK":          "Europe",
        "France":      "Europe",
        "Netherlands": "Europe",
        "China":       "Asia",
        "Japan":       "Asia",
        "South Korea": "Asia",
        "India":       "Asia",
        "Australia":   "Oceania",
        "Brazil":      "LATAM",
        "Chile":       "LATAM",
    }

    subsidy_map = {
        "USA": 7_500, "Canada": 5_000, "Germany": 4_500, "Norway": 0,
        "UK": 2_500, "France": 6_000, "Netherlands": 4_000, "China": 3_000,
        "Japan": 2_000, "South Korea": 2_500, "India": 1_500,
        "Australia": 0, "Brazil": 0, "Chile": 1_000, "Mexico": 0,
    }

    quarters = ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4", "2025-Q1", "2025-Q2"]

    rows = []
    rid = 1
    for make, cars in ev_catalog.items():
        for (model, segment, rng_km, kwh, charge, msrp, warranty) in cars:
            for country, region in regions_map.items():
                for q in quarters:
                    # scale demand: premium brands sell fewer units in LATAM/Oceania
                    base = 8_000 if region in ("North America", "Asia") else \
                           5_000 if region == "Europe" else 800
                    units = int(base * rng.uniform(0.3, 1.8))
                    rows.append((
                        rid, region, country, make, model, segment,
                        units,
                        rng_km + rng.randint(-25, 25),
                        kwh,
                        charge + rng.randint(-3, 6),
                        round(msrp + rng.randint(-3_000, 4_000), 2),
                        q,
                        rng.randint(5, 400),
                        subsidy_map.get(country, 0),
                        round(rng.uniform(3.2, 5.0), 1),
                        warranty,
                    ))
                    rid += 1

    cursor.executemany(
        "INSERT OR IGNORE INTO ev_market VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
    print(f"✅ Seeded ev_market — {len(rows)} rows")


def get_connection():
    """Return a seeded in-memory SQLite connection."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    seed_database(conn)
    return conn


def get_dataframe(conn=None) -> pd.DataFrame:
    """Return the full ev_market table as a pandas DataFrame."""
    own = conn is None
    if own:
        conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM ev_market", conn)
    if own:
        conn.close()
    return df


if __name__ == "__main__":
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM ev_market LIMIT 5", conn)
    print(df.to_string(index=False))

    print("\n── Units sold by manufacturer:")
    summary = pd.read_sql_query(
        "SELECT manufacturer, SUM(units_sold) total FROM ev_market GROUP BY manufacturer ORDER BY total DESC",
        conn,
    )
    print(summary.to_string(index=False))
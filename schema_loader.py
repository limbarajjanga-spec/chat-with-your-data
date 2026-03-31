from mock_data import MOCK_SCHEMA


def get_schema_context(mode="mock", conn=None) -> str:
    if mode == "mock":
        return _format_mock_schema(MOCK_SCHEMA)
    elif mode == "databricks" and conn is not None:
        return _fetch_databricks_schema(conn)
    return ""


def _format_mock_schema(schema: dict) -> str:
    lines = ["You have access to the following tables in a SQLite database (mock mode):\n"]
    for table, meta in schema.items():
        lines.append(f"Table: {table}")
        lines.append(f"  Description: {meta['description']}")
        lines.append("  Columns:")
        for col, dtype in meta["columns"].items():
            lines.append(f"    - {col} ({dtype})")
        lines.append("")
    return "\n".join(lines)


def _fetch_databricks_schema(conn) -> str:
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            ORDER BY table_name, ordinal_position
        """)
        rows = cursor.fetchall()
        tables = {}
        for table, col, dtype in rows:
            tables.setdefault(table, []).append((col, dtype))
        lines = ["You have access to the following tables in Databricks Delta Lake:\n"]
        for table, cols in tables.items():
            lines.append(f"Table: {table}")
            lines.append("  Columns:")
            for col, dtype in cols:
                lines.append(f"    - {col} ({dtype})")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"[Schema fetch error: {e}]"
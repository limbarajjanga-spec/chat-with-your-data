import pandas as pd


def run_query(sql: str, conn, mode="mock") -> pd.DataFrame:
    if mode == "mock":
        return pd.read_sql_query(sql, conn)
    elif mode == "databricks":
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=cols)


# ── Uncomment when switching to Databricks ────────────────────────────────────
# from databricks import sql as dbsql
#
# def get_databricks_connection(server_hostname, http_path, access_token):
#     return dbsql.connect(
#         server_hostname=server_hostname,
#         http_path=http_path,
#         access_token=access_token,
#     )
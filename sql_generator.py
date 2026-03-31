import re
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are an expert SQL analyst. Your job is to convert natural language questions into correct, executable SQL queries.

Rules:
1. Return ONLY the raw SQL query — no markdown, no explanation, no backticks.
2. Use only the tables and columns listed in the schema provided.
3. Use standard SQL syntax compatible with SQLite (mock mode) or Databricks SQL (production).
4. For aggregations, always include appropriate GROUP BY clauses.
5. Limit results to 500 rows unless the user asks for all data.
6. If a question is ambiguous, make a reasonable assumption and proceed.
7. Never use DELETE, UPDATE, DROP, INSERT or any DDL/DML — only SELECT.
"""

REFLECTION_PROMPT = """The SQL query you generated failed with this error:

ERROR: {error}

FAILED QUERY:
{sql}

Please fix the query. Return ONLY the corrected SQL — no explanation, no markdown."""


def extract_sql(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:sql)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def generate_sql(question: str, schema_context: str) -> str:
    messages = [
        {
            "role": "user",
            "content": f"{schema_context}\n\nQuestion: {question}",
        }
    ]
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return extract_sql(response.content[0].text)


def reflect_and_fix(sql: str, error: str, schema_context: str) -> str:
    messages = [
        {
            "role": "user",
            "content": (
                f"{schema_context}\n\n"
                + REFLECTION_PROMPT.format(error=error, sql=sql)
            ),
        }
    ]
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return extract_sql(response.content[0].text)


def generate_chart_config(question: str, columns: list, sample_rows: list) -> dict:
    prompt = f"""Given this question: "{question}"
And a result table with columns: {columns}
Sample rows (first 3): {sample_rows}

Respond ONLY with a JSON object (no markdown) with these keys:
- chart_type: one of "bar", "line", "scatter", "pie", "none"
- x: column name for x-axis (or labels)
- y: column name for y-axis (or values)
- title: short chart title

If the data is not suitable for a chart, use chart_type "none"."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    import json
    text = response.content[0].text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        return {"chart_type": "none"}
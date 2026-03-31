# 🔍 Chat With Your Data — Text2SQL Analytics

> Ask business questions in plain English. Get live SQL results with charts — powered by Claude Sonnet.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Sonnet-orange?style=flat-square)
![Deployed](https://img.shields.io/badge/Deployed-Railway-purple?style=flat-square)

---

## 🚀 Live Demo

🔗 [chat-with-your-data.up.railway.app](https://chat-with-your-data.up.railway.app)

---

## 📌 What It Does

Type a business question in plain English — Claude Sonnet converts it to SQL, runs it live against the database, and returns formatted results with an auto-generated chart.

**Example questions:**
- "Total revenue by product category"
- "Top 5 sales reps by revenue"
- "Monthly revenue trend in 2024"
- "Which region had the most orders?"
- "Products with stock quantity below 50"

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Natural Language → SQL** | Claude Sonnet converts plain English to executable SQL |
| **Schema-Aware Prompting** | Delta Lake table schemas injected dynamically into Claude's context window — accurate multi-table joins, no hallucination |
| **Error Reflection Loop** | If SQL fails, Claude automatically receives the error and self-corrects — no user intervention needed |
| **Auto Chart Generation** | Claude picks the best chart type (bar, line, scatter, pie) based on the question and result shape |
| **Query History** | All queries and results persist in the session |
| **CSV Export** | One-click download of any result set |

---

## 🏗️ Architecture
```
User Question
     │
     ▼
Schema Injector  ──►  Claude Sonnet (SQL Generation)
                              │
                              ▼
                       SQL Query
                              │
                         ┌────┴────┐
                         │ Execute │
                         └────┬────┘
                         Success?
                        ╱         ╲
                      Yes          No
                       │            │
                       │     Claude Sonnet
                       │    (Reflection Loop)
                       │            │
                       └─────┬──────┘
                             ▼
                    Results + Auto Chart
```

---

## 🛠️ Tech Stack

- **LLM**: Anthropic Claude Sonnet — SQL generation + error reflection
- **Frontend**: Streamlit — chat UI, results table, session history
- **Database**: SQLite (mock demo) → Databricks Delta Lake (production)
- **Charts**: Matplotlib
- **Deployment**: Railway

---

## 📁 Project Structure
```
chat-with-your-data/
├── app.py               # Streamlit UI — chat, results, charts
├── sql_generator.py     # Claude API — SQL generation + reflection loop
├── schema_loader.py     # Schema injector for Claude's context window
├── database.py          # Query executor (SQLite / Databricks)
├── mock_data.py         # In-memory SQLite seed data (500 rows)
├── requirements.txt
├── Procfile             # Railway deployment
└── .streamlit/
    └── config.toml
```

---

## ⚡ Run Locally
```bash
# 1. Clone the repo
git clone https://github.com/limbarajjanga-spec/chat-with-your-data.git
cd chat-with-your-data

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 4. Run
streamlit run app.py
```

Open `http://localhost:8501`

---

## 🔄 Switching to Databricks (Production)

1. Install connector: `pip install databricks-sql-connector`
2. Add env vars:
```
DATABRICKS_SERVER_HOSTNAME=your-workspace.azuredatabricks.net
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your_id
DATABRICKS_ACCESS_TOKEN=dapi...
```
3. Uncomment Databricks block in `database.py`
4. Set `mode="databricks"` in `app.py`

Everything else — SQL generation, reflection, charts — works identically.

---

## 👤 Author

**Limba Raj Janga**  
AI Engineer | Ex-ICICI Bank | IIT Kharagpur  
[LinkedIn](https://linkedin.com/in/your-profile) · [GitHub](https://github.com/limbarajjanga-spec)
```


from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from mock_data import get_connection, MOCK_SCHEMA
from schema_loader import get_schema_context
from database import run_query
from sql_generator import generate_sql, reflect_and_fix, generate_chart_config

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chat With Your Data",
    page_icon="🔍",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0e1117;
    color: #e0e0e0;
}
h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; }

.sql-block {
    background: #1a1f2e;
    border-left: 3px solid #4fc3f7;
    padding: 12px 16px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #80deea;
    border-radius: 4px;
    white-space: pre-wrap;
    margin: 8px 0 12px 0;
}
.badge-ok  { background:#1b4332; color:#52b788; padding:2px 10px; border-radius:20px; font-size:.75rem; font-family:'IBM Plex Mono',monospace; }
.badge-err { background:#3b1219; color:#f87171; padding:2px 10px; border-radius:20px; font-size:.75rem; font-family:'IBM Plex Mono',monospace; }

.stButton>button {
    background:#1e3a5f; color:#90caf9; border:1px solid #2a5298;
    border-radius:6px; font-family:'IBM Plex Mono',monospace; font-size:.8rem;
}
.stButton>button:hover { background:#2a5298; color:#fff; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "conn" not in st.session_state:
    st.session_state.conn = get_connection()
if "history" not in st.session_state:
    st.session_state.history = []
if "schema_context" not in st.session_state:
    st.session_state.schema_context = get_schema_context(mode="mock")


# ── Chart renderer ────────────────────────────────────────────────────────────
def render_chart(df: pd.DataFrame, cfg: dict):
    ctype = cfg.get("chart_type", "bar")
    x_col, y_col = cfg.get("x"), cfg.get("y")
    title = cfg.get("title", "")

    if not x_col or not y_col or x_col not in df.columns or y_col not in df.columns:
        return

    fig, ax = plt.subplots(figsize=(5, 3.4))
    fig.patch.set_facecolor("#1a1f2e")
    ax.set_facecolor("#1a1f2e")
    BLUE, TEXT = "#4fc3f7", "#cdd6f4"

    try:
        if ctype == "bar":
            ax.bar(df[x_col].astype(str), pd.to_numeric(df[y_col], errors="coerce"),
                   color=BLUE, edgecolor="#0e1117", linewidth=0.5)
            plt.xticks(rotation=35, ha="right")
        elif ctype == "line":
            ax.plot(df[x_col].astype(str), pd.to_numeric(df[y_col], errors="coerce"),
                    color=BLUE, lw=2, marker="o", ms=4)
            plt.xticks(rotation=35, ha="right")
        elif ctype == "scatter":
            ax.scatter(pd.to_numeric(df[x_col], errors="coerce"),
                       pd.to_numeric(df[y_col], errors="coerce"),
                       color=BLUE, alpha=0.7, edgecolors="none")
        elif ctype == "pie":
            n = len(df)
            colors = [plt.cm.Blues(0.3 + 0.6 * i / max(n - 1, 1)) for i in range(n)]
            ax.pie(pd.to_numeric(df[y_col], errors="coerce").fillna(0),
                   labels=df[x_col].astype(str), autopct="%1.0f%%",
                   colors=colors, textprops={"color": TEXT, "fontsize": 8})

        ax.set_title(title, color=TEXT, fontsize=10, pad=8)
        ax.tick_params(colors=TEXT, labelsize=8)
        for s in ax.spines.values():
            s.set_edgecolor("#2a2f3e")
        if ctype != "pie":
            ax.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda v, _: f"{v:,.0f}" if v >= 1000 else f"{v:.1f}")
            )
            ax.set_xlabel(x_col, color=TEXT, fontsize=8)
            ax.set_ylabel(y_col, color=TEXT, fontsize=8)

        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
    except Exception:
        pass
    finally:
        plt.close(fig)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Chat With Your Data")
    st.markdown("**Mode:** `Mock SQLite`")
    st.caption("Swap to Databricks connector when ready.")
    st.markdown("---")

    st.markdown("### 📋 Tables")
    for tbl, meta in MOCK_SCHEMA.items():
        with st.expander(f"`{tbl}`"):
            st.caption(meta["description"])
            for col, dtype in meta["columns"].items():
                st.markdown(f"- `{col}` · {dtype}")

    st.markdown("---")
    st.markdown("### 💡 Try asking")
    EXAMPLES = [
        "Total revenue by category",
        "Top 5 sales reps by revenue",
        "Monthly revenue trend in 2024",
        "Which region had the most orders?",
        "Average discount by category",
        "Products with stock below 50",
    ]
    for ex in EXAMPLES:
        if st.button(ex, key=f"ex_{ex}"):
            st.session_state.prefill = ex

    st.markdown("---")
    if st.button("🗑 Clear history"):
        st.session_state.history = []
        st.rerun()


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("# Chat With Your Data")
st.markdown(
    "Ask business questions in plain English — "
    "**Claude Sonnet** generates SQL → runs live → returns results + charts."
)
st.markdown("---")


# ── Show one history item ─────────────────────────────────────────────────────
def show_result(item: dict):
    with st.chat_message("user"):
        st.write(item["question"])
    with st.chat_message("assistant", avatar="🤖"):
        badge = "badge-err" if item.get("error") else "badge-ok"
        label = "❌ Error" if item.get("error") else "✅ Success"
        st.markdown(f'<span class="{badge}">{label}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="sql-block">{item["sql"]}</div>', unsafe_allow_html=True)

        if item.get("error"):
            st.error(item["error"])
        elif item.get("df") is not None and not item["df"].empty:
            df = item["df"]
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown(f"**{len(df)} rows**")
                st.dataframe(df, use_container_width=True, height=240)
                st.download_button("⬇ CSV", df.to_csv(index=False).encode(),
                                   "result.csv", "text/csv",
                                   key=f"dl_{id(item)}")
            with c2:
                cfg = item.get("chart_cfg", {})
                if cfg and cfg.get("chart_type") != "none":
                    render_chart(df, cfg)
        elif item.get("df") is not None:
            st.info("Query returned 0 rows.")


# Replay history
for item in st.session_state.history:
    show_result(item)


# ── New question ──────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill", "")
question = st.chat_input("Ask a question about your data…") or prefill

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Generating SQL with Claude…"):
            sql = generate_sql(question, st.session_state.schema_context)
        st.markdown(f'<div class="sql-block">{sql}</div>', unsafe_allow_html=True)

        df, error, chart_cfg = None, None, {}

        # Execute SQL — with one reflection pass on failure
        try:
            df = run_query(sql, st.session_state.conn, mode="mock")
            st.markdown('<span class="badge-ok">✅ Success</span>', unsafe_allow_html=True)
        except Exception as e:
            st.warning("Query failed — asking Claude to self-correct…")
            with st.spinner("Reflecting…"):
                sql = reflect_and_fix(sql, str(e), st.session_state.schema_context)
            st.markdown("**Corrected SQL:**")
            st.markdown(f'<div class="sql-block">{sql}</div>', unsafe_allow_html=True)
            try:
                df = run_query(sql, st.session_state.conn, mode="mock")
                st.markdown('<span class="badge-ok">✅ Fixed</span>', unsafe_allow_html=True)
            except Exception as e2:
                error = str(e2)
                st.markdown('<span class="badge-err">❌ Error</span>', unsafe_allow_html=True)
                st.error(error)

        # Display results + chart
        if df is not None and not df.empty:
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown(f"**{len(df)} rows**")
                st.dataframe(df, use_container_width=True, height=240)
                st.download_button("⬇ CSV", df.to_csv(index=False).encode(),
                                   "result.csv", "text/csv",
                                   key=f"dl_new_{len(st.session_state.history)}")
            with c2:
                with st.spinner("Choosing chart…"):
                    chart_cfg = generate_chart_config(
                        question, list(df.columns), df.head(3).values.tolist()
                    )
                if chart_cfg.get("chart_type") != "none":
                    render_chart(df, chart_cfg)
        elif df is not None:
            st.info("Query returned 0 rows.")

        # Save to history
        st.session_state.history.append(
            {"question": question, "sql": sql, "df": df,
             "chart_cfg": chart_cfg, "error": error}
        )

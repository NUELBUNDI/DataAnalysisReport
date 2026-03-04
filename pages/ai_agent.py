import streamlit as st
import pandas as pd
import numpy as np
import io
import contextlib
import traceback
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from openai import OpenAI

st.set_page_config(page_title="Data Agent", page_icon="📊", layout="wide")



def build_system_prompt(df):
    schema = {c: str(df[c].dtype) for c in df.columns}
    sample = df.head(3).to_dict(orient="records")
    schema_str = "\n".join(f"  - {col}: {dtype}" for col, dtype in schema.items())
    return f"""You are a data analysis assistant. You have a pandas DataFrame called `df`.

SCHEMA ({df.shape[0]:,} rows x {df.shape[1]} columns):
{schema_str}

SAMPLE (first 3 rows):
{json.dumps(sample, indent=2, default=str)}

INSTRUCTIONS:
- Write valid Python code to answer the user's question.
- Assign the final answer (string, number, or markdown table) to a variable named `result`.
- If a chart would help, create it with matplotlib/seaborn and assign the figure to `fig`. Otherwise do not define `fig`.
- Return ONLY raw Python code, no markdown fences, no explanations.
- Available: `df`, `pd`, `np`, `plt`, `sns`.
- Format numbers with commas, round floats to 2 decimal places.
"""

def run_agent(client, history, df, query, model):
    system = build_system_prompt(df)
    messages = [{"role": "system", "content": system}]
    for m in history[:-1]:
        if m["role"] in ("user", "assistant"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": query})

    resp = client.chat.completions.create(
        model=model, messages=messages, temperature=0, max_tokens=2000
    )
    code = resp.choices[0].message.content.strip()
    code = re.sub(r"^```(?:python)?\n?", "", code, flags=re.IGNORECASE)
    code = re.sub(r"\n?```$", "", code)

    local_vars = {"df": df, "pd": pd, "np": np, "plt": plt, "sns": sns, "result": None, "fig": None}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<agent>", "exec"), {}, local_vars)

    result = local_vars.get("result") or buf.getvalue() or "Done."
    return str(result), code, local_vars.get("fig")

# ── Sample data ───────────────────────────────────────────────────────────────

@st.cache_data
def make_sample():
    np.random.seed(42)
    n = 500
    categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports", "Beauty"]
    regions = ["North", "South", "East", "West", "Central"]
    dates = pd.date_range("2023-01-01", "2024-06-30", periods=n)
    df = pd.DataFrame({
        "order_id": [f"ORD-{i:04d}" for i in range(n)],
        "order_date": dates,
        "product_category": np.random.choice(categories, n),
        "product_name": [f"Product_{i % 80}" for i in range(n)],
        "quantity": np.random.randint(1, 20, n),
        "unit_price": np.round(np.random.uniform(5, 500, n), 2),
        "region": np.random.choice(regions, n),
        "customer_id": [f"CUST-{np.random.randint(1, 150):03d}" for _ in range(n)],
        "rating": np.round(np.random.uniform(1, 5, n), 1),
    })
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    return df

@st.cache_data
def load_csv(file):
    df = pd.read_csv(file)
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass
    return df

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    
    st.title("Settings")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"], index=0)
    show_code = st.toggle("Show generated code", value=False)

    st.divider()
    st.subheader("Data")
    source = st.radio("Source", ["Sample dataset", "Upload CSV"])
    uploaded = None
    if source == "Upload CSV":
        uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

    st.divider()
    if st.button("Clear chat history"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

# ── Load data ─────────────────────────────────────────────────────────────────

df = load_csv(uploaded) if uploaded else make_sample()

# ── Main ──────────────────────────────────────────────────────────────────────

st.title("Data Analysis Agent")
st.caption("Ask questions about your dataset in plain English.")

with st.expander("Dataset overview", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{df.shape[0]:,}")
    col2.metric("Columns", df.shape[1])
    col3.metric("Numeric columns", len(df.select_dtypes(include="number").columns))
    col4.metric("Missing values", f"{df.isnull().sum().sum():,}")
    st.dataframe(df.head(10), use_container_width=True)

st.divider()

st.caption("**Suggested questions**")
suggestions = [
    "Total revenue by category",
    "Sales trend over time",
    "Top 5 products by revenue",
    "Average rating per category",
    "Revenue by region",
]
cols = st.columns(len(suggestions))
for i, s in enumerate(suggestions):
    if cols[i].button(s, use_container_width=True):
        st.session_state["pending"] = s

st.divider()

# ── Chat ──────────────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("fig_bytes"):
            st.image(msg["fig_bytes"])
        if show_code and msg.get("code"):
            with st.expander("View generated code"):
                st.code(msg["code"], language="python")

pending = st.session_state.pop("pending", None)
user_input = st.chat_input("Ask anything about your data...") or pending

if user_input:
    if not api_key:
        st.warning("Please enter your OpenAI API key in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                client = OpenAI(api_key=api_key)
                answer, code, fig = run_agent(client, st.session_state.messages, df, user_input, model)

                fig_bytes = None
                if fig is not None:
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches="tight", dpi=140)
                    plt.close(fig)
                    fig_bytes = buf.getvalue()

                st.markdown(answer)
                if fig_bytes:
                    st.image(fig_bytes)
                if show_code:
                    with st.expander("View generated code"):
                        st.code(code, language="python")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "code": code,
                    "fig_bytes": fig_bytes,
                })

            except Exception as e:
                err = f"Something went wrong: {e}"
                st.error(err)
                with st.expander("Traceback"):
                    st.code(traceback.format_exc())
                st.session_state.messages.append({"role": "assistant", "content": err})
import streamlit      as st
import pandas         as pd
import numpy          as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import st_yled


from utils.data          import get_data,download_file,get_metrics
from utils.plots         import plot_region_distribution,plot_payment_distribution
from utils.aggrid_build  import render_aggrid
from components.comp     import kpi_badge_card

# --- Page Configuration ---
st.set_page_config(page_title="SalesAI Dashboard", layout="wide", initial_sidebar_state="expanded")

from pathlib import Path

def load_css():
    css_path = Path(r"assets\styles.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load once at top
load_css()

################# Load Sessions/ instantiate SessionState ##########################


    
##############################################################################

############# Get Data ######################

df_revenue              = get_data('data/amazon_sales_dataset.csv')
df_revenue['order_date']= pd.to_datetime(df_revenue['order_date']).dt.date

max_date = df_revenue['order_date'].max()
min_date = df_revenue['order_date'].min()

# Get 12 months range
last_1_months  = max_date  - timedelta(days=30)
last_3_months  = max_date  - timedelta(days=90)
last_6_months  = max_date  - timedelta(days=180)
last_12_months = max_date - timedelta(days=365)
last_24_months = max_date - timedelta(days=720)
last_36_months = max_date - timedelta(days=1080)



# --- PAGE 1: OVERVIEW ---
# Header
col1, col2, col3, col4 = st.columns([6, 2, 2, 2],vertical_alignment='bottom')
with col1:
    st.markdown("### 🏠 Sales Performance Dashboard")
    st.caption("Comprehensive overview of revenue, order volume, and product performance across regions and categories.")
with col2:
    time_range = st.selectbox("🗓️ Time Range",
             ["Last 3 Months", "Last 6 Months", "Last 12 Months", "Last 2 Years", "Last 3 Years"],
             index=0    ,
             format_func=lambda x: x.title(),
             placeholder="Select a time range")
with col3:
    product_category = st.selectbox(label="Product Category",
             options=df_revenue['product_category'].unique(),
             format_func=lambda x: x.title(),
             placeholder="Select a product category")

with col4:
    download_file(df_revenue,'Sales_Analytics.csv')


# Filter Data


if time_range=='Last 3 Months':
    df_filtered = df_revenue[
          (df_revenue['order_date'].between(last_3_months, max_date)) &
          (df_revenue['product_category']==product_category)
    ]
    differences = get_metrics(df_revenue, months=3)
elif time_range=='Last 6 Months':
    df_filtered = df_revenue[
          (df_revenue['order_date'].between(last_6_months, max_date)) &
          (df_revenue['product_category']==product_category)
    ]
    differences = get_metrics(df_revenue, months=6)
elif time_range=='Last 12 Months':
    df_filtered = df_revenue[
          (df_revenue['order_date'].between(last_12_months, max_date)) &
          (df_revenue['product_category']==product_category)
    ]

    differences = get_metrics(df_revenue, months=12)
elif time_range=='Last 2 Years':
    df_filtered = df_revenue[
          (df_revenue['order_date'].between(last_24_months, max_date)) &
          (df_revenue['product_category']==product_category)
    ]
    differences = get_metrics(df_revenue, months=24)
elif time_range=='Last 3 Years':
    df_filtered = df_revenue[
          (df_revenue['order_date'].between(last_36_months, max_date)) &
          (df_revenue['product_category']==product_category)
    ]
    differences = get_metrics(df_revenue, months=36)


st.markdown("<br>", unsafe_allow_html=True)

st_yled.init()

def format_percent(value):
    if value is None:
        return "N/A"
    return f"{(value*100):.2f}%"

def get_color(value):
    if value is None:
        return "grey"
    return "green" if value >= 0 else "red"

def get_bg_color(value):
    if value is None:
        return "#F6F6F6"
    return "#F6F6F6" if value >= 0 else "#E3BFB8"

kpi_config = [
    {
        "title": "Total Revenue",
        "key": "total_revenue",
        "format": lambda x: f"KES {x:,.2f}"
    },
    {
        "title": "Total Orders",
        "key": "total_orders",
        "format": lambda x: f"{x:,.0f}"
    },
    {
        "title": "Average Rating",
        "key": "average_rating",
        "format": lambda x: f"{x:.2f}"
    },
    {
        "title": "Quantity Sold",
        "key": "quantity_sold",
        "format": lambda x: f"{x:,.0f}"
    },
]

cols = st.columns(len(kpi_config))
for col, config in zip(cols, kpi_config):
    metric = differences[config["key"]]
    pct   = metric["percent_change"]

    with col:
        kpi_badge_card(
            title=config["title"],
            value=config["format"](metric["current"]),
            badge_text=format_percent(pct),
            border_color=get_color(pct),
            barge_color=get_color(pct), 
            background_color=get_bg_color(pct),
            key=f"kpi-{config['key']}"
        )



st.markdown("<br>", unsafe_allow_html=True)

# Middle Row Charts
col_chart1, col_chart2 = st.columns([6, 3],border=True,vertical_alignment='top')

with col_chart1:
    st.markdown("**Revenue Trend**")
    fig_rev = px.line(df_filtered.groupby('order_date').sum().reset_index(), x='order_date', y='total_revenue', line_shape='spline')
    fig_rev.update_traces(line_color='#3b82f6', fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)')
    fig_rev.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig_rev.update_yaxes(showgrid=True, gridcolor='#f0f0f0', tickprefix="$")
    st.plotly_chart(fig_rev, width='stretch')

with col_chart2:
    tab1, tab2 = st.tabs(["🎯Sales by Region", "💳Payment Methods"])
    
    with tab1:
        plot_region_distribution(
            df_filtered,
            column="customer_region",
            title="Customer Distribution by Region"
        )

    with tab2:
        plot_payment_distribution(
            df_filtered,
            column='payment_method',
            title='Payment Methods Distribution'
        )

# Bottom Row Charts

with st.container(height=400):
    st.markdown("**Recent Orders**")
    render_aggrid(df_revenue[['order_id','product_category','quantity_sold','customer_region','price','payment_method','rating','total_revenue']])




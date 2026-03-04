import streamlit       as st
import pandas          as pd
import numpy           as np
import plotly.graph_objects as go
import st_yled
from pathlib import Path
from datetime import datetime, timedelta

from utils.data          import get_data,download_file,get_metrics
from utils.plots         import plot_region_distribution,plot_payment_distribution
from utils.aggrid_build  import render_aggrid
from components.comp     import kpi_badge_card
from services.prophet_service import generate_forecast


def load_css():
    css_path = Path(r"assets\styles.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load once at top
load_css()

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


# Header
col1, col2, col3 = st.columns([6, 2, 2])

with col1:
    st.markdown("### 🧙🏽‍♂️ Forecast Session")
    st.caption("AI-driven revenue predictions for the upcoming quarters.")
with col2:
    scenario = st.selectbox("Scenario", ["Moderate (+5%)", "Aggressive (+10%)", "Conservative (+2%)"])
with col3:
    horizon_str = st.selectbox("Horizon", ["3 Months","6 Months", "12 Months", ])
    
df_daily, df_forecast, df_forecast_full = generate_forecast(df_revenue, horizon_str, scenario)

# Main Forecast Chart
st.caption("Historical performance vs. projected growth scenarios with confidence intervals.")

# KPIs
st_yled.init()

def get_color(value):
    return "green" if value >= 0 else "red"

def get_bg_color(value):
    return "#F6F6F6" if value >= 0 else "#E3BFB8"

projected_revenue   = df_forecast['Forecast'].sum() if len(df_forecast) > 0 else 0
avg_monthly         = projected_revenue / (len(df_forecast) / 30.0) if len(df_forecast) > 0 else 0
historical_monthly  = df_daily['Revenue'].sum() / (len(df_daily) / 30.0) if len(df_daily) > 0 else 0
expected_growth     = ((avg_monthly - historical_monthly) / historical_monthly) * 100 if historical_monthly > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    kpi_badge_card(
        title=f"Projected Rev. ({horizon_str})",
        value=f"${projected_revenue:,.0f}",
        badge_text="Forecast",
        border_color="grey",
        barge_color="grey",
        background_color="#F6F6F6",
        key="kpi-forecast-1"
    )

with kpi2:
    kpi_badge_card(
        title="Avg Monthly Run Rate",
        value=f"${avg_monthly:,.0f}",
        badge_text="Projected",
        border_color="grey",
        barge_color="grey",
        background_color="#F6F6F6",
        key="kpi-forecast-2"
    )

with kpi3:
    kpi_badge_card(
        title="Expected Growth",
        value=f"{expected_growth:+.1f}%",
        badge_text="vs hist",
        border_color=get_color(expected_growth),
        barge_color=get_color(expected_growth),
        background_color=get_bg_color(expected_growth),
        key="kpi-forecast-3"
    )

st.markdown("<br>", unsafe_allow_html=True)


with st.container(height=450):
    fig_fc = go.Figure()
    
    # Historical Line
    fig_fc.add_trace(go.Scatter(x=df_daily['Date'], y=df_daily['Revenue'], mode='lines+markers', 
                                name='Historical', line=dict(color='#3b82f6', width=2), marker=dict(size=4)))
    
    # Forecast Line (Dashed)
    fig_fc.add_trace(go.Scatter(x=df_forecast['Date'], y=df_forecast['Forecast'], mode='lines+markers', 
                                name='Forecast', line=dict(color='#6C5DD3', width=2, dash='dash'), marker=dict(size=4)))
    
    # Confidence Interval Shading
    fig_fc.add_trace(go.Scatter(x=df_forecast['Date'], y=df_forecast['UpperBound'], mode='lines', 
                                line=dict(width=0), showlegend=False, hoverinfo='skip'))
    fig_fc.add_trace(go.Scatter(x=df_forecast['Date'], y=df_forecast['LowerBound'], mode='lines', 
                                fill='tonexty', fillcolor='rgba(108, 93, 211, 0.1)', line=dict(width=0), 
                                name='Confidence Range', hoverinfo='skip'))
    
    fig_fc.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig_fc.update_yaxes(showgrid=True, gridcolor='#f0f0f0', tickprefix="$")
    st.plotly_chart(fig_fc, use_container_width=True)

# Bottom Row: Category Growth & AI Recommendation
col_cat, col_ai = st.columns([6, 4])


with col_cat:
    
    with st.container(height=300):
        st.markdown("**Category Growth Potential**")
        st.caption("Estimated growth by product category based on recent trends.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Calculate real category growth from df_revenue
        df_rev_dt = df_revenue.copy()
        df_rev_dt['order_date'] = pd.to_datetime(df_rev_dt['order_date'])
        max_d = df_rev_dt['order_date'].max()
        c_start = max_d - pd.DateOffset(months=6)
        p_start = c_start - pd.DateOffset(months=6)
        
        curr = df_rev_dt[(df_rev_dt['order_date'] > c_start) & (df_rev_dt['order_date'] <= max_d)].groupby('product_category')['total_revenue'].sum()
        prev = df_rev_dt[(df_rev_dt['order_date'] > p_start) & (df_rev_dt['order_date'] <= c_start)].groupby('product_category')['total_revenue'].sum()
        
        growth = ((curr - prev) / prev * 100).fillna(0)
        top_cats = curr.nlargest(4).index.tolist()
        
        colors = ["#ec4899", "#3b82f6", "#a855f7", "#f97316"]
        cats = []
        tot_rev = curr.sum()
        for i, cat in enumerate(top_cats):
            g_val = growth.get(cat, 0)
            rev_val = curr.get(cat, 0)
            prog = (rev_val / tot_rev) if tot_rev > 0 else 0
            prog = min(prog * 2, 1.0) # Scale it up slightly for visual effect
            cats.append((cat, prog, f"{g_val:+.1f}%", colors[i % len(colors)]))
        
        for name, prog, text, color in cats:
            c1, c2, c3 = st.columns([3, 6, 1])
            c1.write(name)
            with c2:
                # Using custom HTML for colored progress bars
                st.markdown(f"""
                <div style="background-color: #f0f0f0; border-radius: 5px; width: 100%; height: 10px; margin-top: 10px;">
                    <div style="background-color: {color}; width: {prog*100}%; height: 100%; border-radius: 5px;"></div>
                </div>
                """, unsafe_allow_html=True)
            c3.write(f"**{text}**")

with col_ai:
    with st.container(height=300):
        top_growth_cat = growth.idxmax() if not growth.empty else "Top"
        fastest_cat = top_cats[0] if top_cats else "Key"
        if top_growth_cat == fastest_cat and len(top_cats) > 1:
            fastest_cat = top_cats[1]
            
        st.markdown(f"""
        <div class="ai-card">
            <h4 style="margin-top:0;">💡 AI Recommendation</h4>
            <p style="color: #A0AEC0; font-size: 14px;">Based on the {scenario.split(' ')[0].lower()} growth scenario ({scenario.split(' ')[1]}), inventory levels for <strong>{top_growth_cat}</strong> and <strong>{fastest_cat}</strong> categories may fall short by next quarter.</p>
            <a href="#" class="ai-btn">View Inventory Report</a>
        </div>
        """, unsafe_allow_html=True)
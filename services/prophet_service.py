import pandas as pd
import streamlit as st
from prophet import Prophet

@st.cache_data
def generate_forecast(df_revenue, horizon_str, scenario):

    
    # Group by date for daily revenue
    df_daily = df_revenue.groupby('order_date')['total_revenue'].sum().reset_index()
    df_daily.columns = ['Date', 'Revenue']
    df_daily['Date'] = pd.to_datetime(df_daily['Date'])
    
    df_prophet = df_daily.rename(columns={'Date': 'ds', 'Revenue': 'y'})
    
    m = Prophet(daily_seasonality=False, yearly_seasonality=True, weekly_seasonality=True)
    m.fit(df_prophet)
    
    horizon_map = {"6 Months": 180, "12 Months": 365, "3 Months": 90}
    days = horizon_map.get(horizon_str, 180)
    
    future = m.make_future_dataframe(periods=days)
    forecast = m.predict(future)
    
    scenario_map = {"Moderate (+5%)": 1.05, "Aggressive (+10%)": 1.10, "Conservative (+2%)": 1.02}
    modifier = scenario_map.get(scenario, 1.05)
    
    forecast['yhat'] = forecast['yhat'] * modifier
    forecast['yhat_lower'] = forecast['yhat_lower'] * modifier
    forecast['yhat_upper'] = forecast['yhat_upper'] * modifier
    
    # format output
    df_forecast_full = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(
        columns={'ds': 'Date', 'yhat': 'Forecast', 'yhat_lower': 'LowerBound', 'yhat_upper': 'UpperBound'}
    )
    
    # Filter only future dates
    max_date = df_daily['Date'].max()
    df_future = df_forecast_full[df_forecast_full['Date'] > max_date].copy()
    
    return df_daily, df_future, df_forecast_full

import pandas as pd  
import numpy as np  
import streamlit as st

@st.cache_data
def get_data(file_path:str):

    df = pd.read_csv(file_path,parse_dates=['order_date'])
    return df



def get_metrics(data: pd.DataFrame, months: int):

    data['order_date'] = pd.to_datetime(data['order_date'])
    max_date = data['order_date'].max()

 
    current_start = max_date - pd.DateOffset(months=months)
    df_current = data[
        (data['order_date'] > current_start) &
        (data['order_date'] <= max_date)
    ]


    previous_end = current_start
    previous_start = previous_end - pd.DateOffset(months=months)

    df_previous = data[
        (data['order_date'] > previous_start) &
        (data['order_date'] <= previous_end)
    ]


    def calculate_metrics(df):
        return {
            "total_revenue": df['total_revenue'].mean(),
            "total_orders": df['order_id'].nunique(),
            "average_rating": df['rating'].mean(),
            "quantity_sold": df['quantity_sold'].sum()
        }

    current = calculate_metrics(df_current)
    previous = calculate_metrics(df_previous)


    differences = {}

    for key in current.keys():
        curr_val = current[key]
        prev_val = previous[key]

        abs_change = curr_val - prev_val

        if prev_val == 0 or pd.isna(prev_val):
            pct_change = None
        else:
            pct_change = (abs_change / prev_val) * 100

        differences[key] = {
            "current": curr_val,
            "previous": prev_val,
            "absolute_change": abs_change,
            "percent_change": pct_change
        }

    return differences
        











    pass


def download_file(df:pd.DataFrame,file_name:str):
    st.download_button(
        key='download-invoice-not-transmitted',
        label="📥 Export Data",
        data=df.to_csv(index=False),
        file_name=file_name,
        mime="text/csv",
        type="primary",
    )


    




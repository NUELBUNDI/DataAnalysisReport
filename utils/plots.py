import plotly.express as px
import streamlit as st

def plot_region_distribution(
    df,
    column,
    height=320,
    palette=None,
    title=None,
):
    """
    Creates a professional multi-color horizontal bar chart
    showing value counts of a categorical column, with text inside bars
    formatted with commas.
    """

    if palette is None:
        palette = [
            "#2563eb",  # blue
            "#16a34a",  # green
            "#f59e0b",  # amber
            "#ef4444",  # red
            "#7c3aed",  # violet
            "#0ea5e9",  # sky
            "#f97316",  # orange
        ]

    data = df[column].value_counts().reset_index()
    data.columns = ["Category", "Value"]
    data = data.sort_values("Value", ascending=True)

    # Format values with commas for text inside bars
    data["Value_text"] = data["Value"].apply(lambda x: f"{x:,}")

    fig = px.bar(
        data,
        x="Value",
        y="Category",
        orientation="h",
        text="Value_text",  # use formatted text
        color="Category",
        color_discrete_sequence=palette,
    )

    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=12, family="Inter, Arial, sans-serif"),
        marker=dict(opacity=0.9),
        hovertemplate="<b>%{y}</b><br>Count: %{x:,}<extra></extra>"  # formatted in hover too
    )

    fig.update_layout(
        height=height,
        showlegend=False,
        margin=dict(l=0, r=20, t=30 if title else 10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, Arial, sans-serif",
            size=13,
            color="#374151"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.05)",
            zeroline=False,
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=False,
            categoryorder="total ascending"
        )
    )

    if title:
        fig.update_layout(title=dict(text=title, x=0, xanchor="left"))

    st.plotly_chart(fig, use_container_width=True)



def plot_payment_distribution(
    df,
    column='payment_method',
    height=270,
    hole=0.4,
    palette=None,
    title=None,
):
    """
    Creates a professional donut chart for payment methods with percentages inside slices.
    """

    if palette is None:
        palette = [
            "#f97316",  # orange
            "#22c55e",  # green
            "#3b82f6",  # blue
            "#ef4444",  # red
            "#eab308",  # amber
        ]

    data = df[column].value_counts().reset_index()
    data.columns = ['Method', 'Value']

    fig = px.pie(
        data,
        values='Value',
        names='Method',
        hole=hole,
        color='Method',
        color_discrete_sequence=palette,
        labels={'Method':'Payment Method', 'Value':'Count'}
    )

    # Show percentage + value inside slices
    fig.update_traces(
        textinfo='percent+label',
        textposition='inside',
        insidetextorientation='radial',
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>'
    )

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=30 if title else 10, b=0),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, Arial, sans-serif', size=13, color='#374151')
    )

    if title:
        fig.update_layout(title=dict(text=title, x=0, xanchor='left'))

    st.plotly_chart(fig, use_container_width=True)
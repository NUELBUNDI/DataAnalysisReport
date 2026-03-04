import streamlit as st
import st_yled

def kpi_badge_card(
    title: str,
    value: str,
    badge_text: str = "New",
    badge_icon: str = ":material/star:",
    width: int = 300,
    background_color: str = "#F6F6F6",
    border_color: str = "grey",
    border_style: str = "solid",
    barge_color : str = "grey",
    border_width: int = 1,
    key: str = None
):
    """
    Reusable KPI Badge Card Component
    """

    st_yled.badge_card_one(
        badge_text=badge_text,
        badge_icon=badge_icon,
        title=title,
        text=value,
        width=width,
        title_font_size=18,
        text_font_size =18,
        text_font_weight="bold",
        background_color=background_color,
        border_color=border_color,
        border_style=border_style,
        border_width=border_width,
        badge_color= barge_color,
        key=key,
    )
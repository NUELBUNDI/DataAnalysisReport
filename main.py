import streamlit as st

# st.logo()
create_page = st.Page("pages/eda.py",      title="Dashboard", icon=":material/dashboard:")
delete_page = st.Page("pages/forecast.py", title="Forecast", icon=":material/add_chart:")
ai_page     = st.Page("pages/ai_agent.py", title="AI Agent", icon=":material/smart_toy:")

pg = st.navigation([create_page, delete_page, ai_page])

st.set_page_config(page_title="Data manager", page_icon=":material/edit:")

# --- Inject Custom CSS ---
st.markdown("""
    <style>
        /* Make sidebar use full height */
        section[data-testid="stSidebar"] {
            position: relative;
        }

        /* Footer container */
        .sidebar-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 16rem;  /* default sidebar width */
            padding: 10px;
            text-align: left;
            font-size: 14px;
        }

        /* Ensure content does not overlap footer */
        section[data-testid="stSidebar"] > div:first-child {
            padding-bottom: 80px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Footer HTML ---
st.sidebar.markdown("""
    <div class="sidebar-footer">
        © 2026 DatabuildAI<br> <a href="https://databuildai.com" target="_blank">Developed By DataBuildAI</a>
    </div>
""", unsafe_allow_html=True)

pg.run()
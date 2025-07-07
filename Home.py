import streamlit as st

st.set_page_config(
    page_title="Snowflake IaC Assistant",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #f0f2f6;
    }

    .home-container {
        max-width: 800px;
        margin: 0 auto;
        background-color: #ffffff;
        color: #000000;
        padding: 2.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    .stButton > button {
        width: 100%;
        min-height: 80px;
        background-color: #003366 !important;
        color: white !important;
        font-size: 1.1rem;
        font-weight: 600;
        border: none !important;
        border-radius: 10px;
        transition: background-color 0.3s ease, color 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #005599 !important;
        color: white !important;
    }

    .stButton > button:active {
        background-color: #001f3f !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("""
        <div class="home-container">
            <h1>Snowflake IaC Assistant</h1>
            <p>
                This tool helps you manage Snowflake users, roles, warehouses and grants.<br>
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    if st.button("Add New User"):
        st.switch_page("pages/1_Add_User.py")

    if st.button("Add Warehouse"):
        st.switch_page("pages/3_Add_Warehouse.py")

with col2:
    if st.button("Add Role"):
        st.switch_page("pages/2_Add_Role.py")

    if st.button("Add Grant"):
        st.switch_page("pages/4_Add_Grant.py")
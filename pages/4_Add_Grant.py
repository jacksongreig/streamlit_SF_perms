import streamlit as st
from ruamel.yaml import YAML
from io import StringIO

st.set_page_config(page_title="Add New Grant", layout="centered")

# ========== Styling ==========
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #f0f2f6;
    }

    .tool-container {
        max-width: 800px;
        margin: 0 auto;
        background-color: #ffffff;
        color: #000000;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }

    /* Form field labels */
    label, .stTextInput label, .stSelectbox label {
        color: #1a1a1a !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Checkbox label */
    .stCheckbox > label {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }

    /* Code block (YAML preview) */
    .stCodeBlock pre {
        background-color: #f4f4f4 !important;
        color: #333333 !important;
        font-size: 0.9rem;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Section headers */
    h1, h2, h3 {
        color: #003366 !important;
        font-weight: 700 !important;
    }

    .stMarkdown h2 {
        font-size: 1.25rem;
        color: #003366 !important;
        margin-top: 2rem;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        min-height: 60px;
        background-color: #003366 !important;
        color: white !important;
        font-size: 1.05rem;
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

yaml = YAML()

with st.container():
    st.header("Add New Snowflake Grant")

    col1, col2 = st.columns(2)
    with col1:
        role = st.text_input("Role to Grant", placeholder="e.g. ANALYST")
        privilege = st.text_input("Privilege", placeholder="e.g. SELECT")
    with col2:
        object_type = st.selectbox("Object Type", ["TABLE", "VIEW", "SCHEMA", "DATABASE", "WAREHOUSE"])
        object_name = st.text_input("Object Name", placeholder="e.g. MY_DB.MY_SCHEMA.MY_TABLE")

    grant_option = st.selectbox("With Grant Option", ["false", "true"])

    grant_yaml = {
        'grants': [
            {
                'role': role,
                'privilege': privilege,
                'on': {
                    'object_type': object_type,
                    'name': object_name
                },
                'with_grant_option': grant_option == "true"
            }
        ]
    }

    st.subheader("YAML Preview")
    yaml_stream = StringIO()
    yaml.dump(grant_yaml, yaml_stream)
    st.code(yaml_stream.getvalue(), language='yaml')

    if st.button("🚀 Submit & Raise Pull Request"):
        st.success("Stub: This would push to GitHub and raise a PR.")

    st.markdown("</div>", unsafe_allow_html=True)

import streamlit as st
from ruamel.yaml import YAML
from io import StringIO
from utils.github_integration import raise_github_pr

st.set_page_config(page_title="Add New User", layout="centered")

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

    h1, h2 {
        color: #003366 !important;
        font-weight: 700;
    }

    .stButton > button {
        width: 100%;
        min-height: 60px;
        background-color: #003366 !important;
        color: white !important;
        font-size: 1.05rem;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        transition: background-color 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #005599 !important;
    }

    .stCodeBlock pre {
        background-color: #f4f4f4 !important;
        color: #333 !important;
        font-size: 0.9rem;
        border-radius: 8px;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

yaml = YAML()

with st.container():
    st.header("Add New Snowflake User")

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", placeholder="e.g. JACKSON.TEST")
        default_role = st.text_input("Default Role", placeholder="e.g. PUBLIC")
    with col2:
        default_warehouse = st.text_input("Default Warehouse", placeholder="e.g. COMPUTE_WH")
        must_change_password = st.selectbox("Must Change Password on Login", ["true", "false"])

    disabled = st.selectbox("Disabled", ["false", "true"])
    comment = st.text_area("Comment", placeholder="Add a comment...")

    user_yaml = {
        'users': [
            {
                'name': username,
                'default_role': default_role,
                'default_warehouse': default_warehouse,
                'disabled': disabled == "true",
                'must_change_password': must_change_password == "true",
                'comment': comment
            }
        ]
    }

    st.subheader("YAML Preview")
    yaml_stream = StringIO()
    yaml.dump(user_yaml, yaml_stream)
    st.code(yaml_stream.getvalue(), language='yaml')

    if st.button("🚀 Submit & Raise Pull Request"):
        try:
            filename = f"users/{username.lower().replace('.', '_')}.yaml"
            pr_url = raise_github_pr(
                filename=filename,
                file_contents=yaml_stream.getvalue(),
                token=st.secrets["GITHUB_TOKEN"],
                repo_name=st.secrets["GITHUB_REPO"]
            )
            st.success(f"Pull Request created: [View PR]({pr_url})")
        except Exception as e:
            st.error(f"Failed to create PR: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
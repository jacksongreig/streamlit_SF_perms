import streamlit as st
from ruamel.yaml import YAML
from io import StringIO
from utils.github_integration import raise_github_pr

st.set_page_config(page_title="Add New Warehouse", layout="centered")

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
        border-radius: 10px;
    }

    .stCodeBlock pre {
        background-color: #f4f4f4 !important;
    }
    </style>
""", unsafe_allow_html=True)

yaml = YAML()

with st.container():
    st.header("Add New Snowflake Warehouse")

    wh_name = st.text_input("Warehouse Name", placeholder="e.g. DEV_WH")
    size = st.selectbox("Size", ["X-Small", "Small", "Medium", "Large", "X-Large"])
    auto_suspend = st.number_input("Auto Suspend (seconds)", min_value=0, value=600)
    auto_resume = st.selectbox("Auto Resume", ["true", "false"])
    comment = st.text_area("Comment", placeholder="Optional comment")

    warehouse_yaml = {
        'warehouses': [
            {
                'name': wh_name,
                'size': size,
                'auto_suspend': auto_suspend,
                'auto_resume': auto_resume == "true",
                'comment': comment
            }
        ]
    }

    st.subheader("YAML Preview")
    yaml_stream = StringIO()
    yaml.dump(warehouse_yaml, yaml_stream)
    st.code(yaml_stream.getvalue(), language='yaml')

    if st.button("🚀 Submit & Raise Pull Request"):
        try:
            filename = f"warehouses/{wh_name.lower()}.yaml"
            pr_url = raise_github_pr(
                filename=filename,
                file_contents=yaml_stream.getvalue(),
                token=st.secrets["GITHUB_TOKEN"],
                repo_name=st.secrets["GITHUB_REPO"]
            )
            st.success(f"✅ Pull Request created: [View PR]({pr_url})")
        except Exception as e:
            st.error(f"❌ Failed to create PR: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

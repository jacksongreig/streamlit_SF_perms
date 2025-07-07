import streamlit as st
from ruamel.yaml import YAML
from io import StringIO
from utils.github_integration import raise_github_pr

st.set_page_config(page_title="Add New Role", layout="centered")

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
    st.header("Add New Snowflake Role")

    role_name = st.text_input("Role Name", placeholder="e.g. ANALYST")
    comment = st.text_area("Comment", placeholder="Optional comment")

    role_yaml = {
        'roles': [
            {
                'name': role_name,
                'comment': comment
            }
        ]
    }

    st.subheader("YAML Preview")
    yaml_stream = StringIO()
    yaml.dump(role_yaml, yaml_stream)
    st.code(yaml_stream.getvalue(), language='yaml')

    if st.button("🚀 Submit & Raise Pull Request"):
        try:
            filename = f"roles/{role_name.lower()}.yaml"
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

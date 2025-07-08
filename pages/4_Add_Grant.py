import streamlit as st
from ruamel.yaml import YAML
from io import StringIO
from utils.github_integration import raise_github_pr
from utils.shared_css import inject_shared_css

st.set_page_config(
    page_title="Add Grant",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed"
)

inject_shared_css()
yaml = YAML()

with st.container():
    st.markdown('<h1 style="text-align: center;">Add Grant</h1>', unsafe_allow_html=True)

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

    if st.button("Submit & Raise PR"):
        try:
            filename = f"grants/{role.lower()}_{privilege.lower()}.yaml"
            pr_url = raise_github_pr(
                filename=filename,
                file_contents=yaml_stream.getvalue(),
                token=st.secrets["GITHUB_TOKEN"],
                repo_name=st.secrets["GITHUB_REPO"]
            )
            st.success(f"PR created: [View PR]({pr_url})")
        except Exception as e:
            st.error(f"Failed to create PR: {e}")

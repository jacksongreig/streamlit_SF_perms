import streamlit as st
from ruamel.yaml import YAML
from io import StringIO
from utils.shared_css import inject_shared_css
# from utils.github_integration import raise_github_pr

st.set_page_config(
    page_title="Grants",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed"
)

inject_shared_css()
yaml = YAML()

# Session state to store multiple grants
if "grants_list" not in st.session_state:
    st.session_state["grants_list"] = []

with st.container():
    st.markdown('<h1 style="text-align: center;">Grants</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        role = st.text_input("Role to Grant", placeholder="e.g. ANALYST")
        privilege = st.text_input("Privilege", placeholder="e.g. SELECT")
    with col2:
        object_type = st.selectbox("Object Type", ["TABLE", "VIEW", "SCHEMA", "DATABASE", "WAREHOUSE"])
        object_name = st .text_input("Object Name", placeholder="e.g. MY_DB.MY_SCHEMA.MY_TABLE")

    grant_option = st.selectbox("Include 'WITH GRANT OPTION'?", ["false", "true"])

    add_button_disabled = not all([role, privilege, object_name])

    if st.button("Add to Grants List", disabled=add_button_disabled):
        st.session_state["grants_list"].append({
            'role': role,
            'privilege': privilege,
            'on': {
                'object_type': object_type,
                'name': object_name
            },
            'with_grant_option': grant_option == "true"
        })
        st.success("Grant added!")

    # YAML Preview
    if st.session_state["grants_list"]:
        st.markdown("---")
        st.markdown('<h3 style="text-align: center;">Grants YAML Preview</h3>', unsafe_allow_html=True)

        grant_yaml = {
            'grants': st.session_state["grants_list"]
        }

        yaml_stream = StringIO()
        yaml.dump(grant_yaml, yaml_stream)
        st.code(yaml_stream.getvalue(), language='yaml')

        if st.button("Submit & Raise PR"):
            try:
                safe_filename = f"{role}_{privilege}".lower().replace(" ", "_")
                filename = f"grants/{safe_filename}.yaml"
                pr_url = raise_github_pr(
                    filename=filename,
                    file_contents=yaml_stream.getvalue(),
                    token=st.secrets["GITHUB_TOKEN"],
                    repo_name=st.secrets["GITHUB_REPO"]
                )
                st.success(f"PR created: [View PR]({pr_url})")
                st.session_state["grants_list"] = []  # Clear list after PR
            except Exception as e:
                st.error(f"Failed to create PR: {e}")

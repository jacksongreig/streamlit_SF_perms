import streamlit as st
from ruamel.yaml import YAML
from io import StringIO
from utils.github_integration import raise_github_pr
from utils.shared_css import inject_shared_css

st.set_page_config(
    page_title="Add Role",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed"
)

inject_shared_css()
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False
yaml.allow_unicode = True

with st.container():
    st.markdown('<h1 style="text-align: center;">Add Role</h1>', unsafe_allow_html=True)

    role_name = st.text_input("*Role Name", placeholder="e.g. ANALYST")
    comment = st.text_area("Comment (optional)", placeholder="Describe the role or leave blank")
    owner = st.selectbox("*Owner", options=["SECURITYADMIN", "ACCOUNTADMIN"])

    # Validate and clean
    role_name_clean = role_name.strip()
    comment_clean = comment.strip()

    # Build role dict
    role_data = {
        "name": role_name_clean,
        "owner": owner
    }
    if comment_clean:
        role_data["comment"] = comment_clean

    # Final YAML
    role_yaml = {"roles": [role_data]}

    st.subheader("YAML Preview")
    yaml_stream = StringIO()
    yaml.dump(role_yaml, yaml_stream)
    st.code(yaml_stream.getvalue(), language='yaml')

    if st.button("Submit & Raise PR"):
        if not role_name_clean:
            st.error("Role Name is required.")
        elif not owner:
            st.error("Owner is required.")
        else:
            try:
                filename = f"roles/{role_name_clean.lower().replace(' ', '_').replace('.', '_')}.yaml"
                pr_url = raise_github_pr(
                    filename=filename,
                    file_contents=yaml_stream.getvalue(),
                    token=st.secrets["GITHUB_TOKEN"],
                    repo_name=st.secrets["GITHUB_REPO"]
                )
                st.success(f"PR created: [View PR]({pr_url})")
            except Exception as e:
                st.error(f"Failed to create PR: {e}")

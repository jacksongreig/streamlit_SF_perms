import streamlit as st
from ruamel.yaml import YAML
from io import StringIO
from utils.github_integration import raise_github_pr
from utils.shared_css import inject_shared_css

st.set_page_config(
    page_title="Create New User",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed"
)

inject_shared_css()
yaml = YAML()

with st.container():
    st.markdown('<h1 style="text-align: center;">Create New User</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("*Name:", placeholder="e.g. TEST_PRACTIV")
        default_namespace = st.text_input("Default Namespace (optional)", placeholder="e.g. DEFAULT NAMESPACE")
        default_role = st.text_input("*Default Role", placeholder="e.g. DEFAULT_ROLE")
        default_secondary_roles = st.text_input("Default Secondary Roles (optional)", placeholder="e.g. SECONDARY ROLE")
        default_warehouse = st.text_input("*Default Warehouse", placeholder="e.g. WAREHOUSE")
        display_name = st.text_input("*Display Name", placeholder="e.g. DISPLAY NAME")
        email = st.text_input("*Email", placeholder="e.g. jackson.greig@practiv.com")
        disabled = st.checkbox("Disabled User")

    with col2:
        first_name = st.text_input("*First Name", placeholder="e.g. FIRST NAME")
        last_name = st.text_input("*Last Name", placeholder="e.g. LAST NAME")
        middle_name = st.text_input("Middle Name (optional)", placeholder="e.g. MIDDLE NAME")
        network_policy = st.text_input("Network Policy (optional)", placeholder="e.g. INTERNAL_POLICY")
        owner = st.text_input("*Owner", value="ACCOUNTADMIN")
        user_type = st.selectbox("*User Type", ["PERSON", "SERVICE"])
        password = st.text_input("*Password", type="password", placeholder="e.g. &47#*4#4473#@#")
        must_change_password = st.checkbox("Change Password on First Login", value=True)

    rsa_public_key = st.text_input("RSA Public Key (optional)", placeholder="PASTE PUBLIC KEY HERE")
    comment = st.text_area("Comment (optional)")

    if not display_name.strip() and first_name.strip() and last_name.strip():
        display_name = f"{first_name.strip()} {last_name.strip()}"

    user_data = {
        'name': name,
        'comment': comment.strip() or None,
        'default_namespace': default_namespace.strip() or None,
        'default_role': default_role,
        'default_secondary_roles': default_secondary_roles.strip() or None,
        'default_warehouse': default_warehouse,
        'disabled': disabled,
        'display_name': display_name.strip(),
        'email': email.strip(),
        'first_name': first_name.strip(),
        'last_name': last_name.strip(),
        'login_name': name.strip(),
        'middle_name': middle_name.strip() or None,
        'must_change_password': bool(must_change_password),
        'network_policy': network_policy.strip() or None,
        'owner': owner.strip(),
        'rsa_public_key': rsa_public_key.strip() or None,
        'type': user_type,
        'password': password.strip()
    }

    user_data_cleaned = {k: v for k, v in user_data.items() if v is not None}

    user_yaml = {
        'users': [user_data_cleaned]
    }

    st.subheader("YAML Preview")
    yaml_stream = StringIO()
    yaml.dump(user_yaml, yaml_stream)
    st.code(yaml_stream.getvalue(), language="yaml")

    if st.button("Submit & Raise PR"):
        if not name.strip():
            st.error("Name is required.")
        elif not password.strip():
            st.error("Password is required.")
        elif not default_role.strip() or not default_warehouse.strip():
            st.error("Default role and warehouse are required.")
        else:
            try:
                filename = f"users/{name.lower().replace('.', '_')}.yaml"
                pr_url = raise_github_pr(
                    filename=filename,
                    file_contents=yaml_stream.getvalue(),
                    token=st.secrets["GITHUB_TOKEN"],
                    repo_name=st.secrets["GITHUB_REPO"]
                )
                st.success(f"PR created: [View PR]({pr_url})")
            except Exception as e:
                st.error(f"Failed to create PR: {e}")
import streamlit as st
from snowflake.snowpark.context import get_active_session
from ruamel.yaml import YAML
from io import StringIO
from utils.shared_css import inject_shared_css
from utils.github import raise_github_pr

# ------------------------ Page Setup ------------------------

st.set_page_config(page_title="Users", layout="centered", initial_sidebar_state="collapsed")
inject_shared_css()

session = get_active_session()
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False

if "user_mode" not in st.session_state:
    st.session_state.user_mode = "create"

# ------------------------ Title & Mode Switch ------------------------

st.markdown('<h1 style="text-align: center;">Users</h1>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("Create New User"):
        st.session_state.user_mode = "create"
with col2:
    if st.button("Edit Existing User"):
        st.session_state.user_mode = "edit"

st.markdown("---")
st.markdown(f"<h3 style='text-align: center;'>{'Create New User' if st.session_state.user_mode == 'create' else 'Edit Existing User'}</h3>", unsafe_allow_html=True)

# ------------------------ Load Existing Users ------------------------

@st.cache_data
def get_existing_users():
    df = session.sql("""
        SELECT name 
        FROM SNOWFLAKE.ACCOUNT_USAGE.USERS 
        WHERE deleted_on IS NULL AND name != 'SNOWFLAKE'
        ORDER BY name
    """).to_pandas()
    return df["NAME"].tolist()

def get_user_details(user_name: str):
    df = session.sql(f"""
        SELECT 
            NAME, EMAIL, DISABLED, DISPLAY_NAME, DEFAULT_ROLE, 
            DEFAULT_WAREHOUSE, OWNER, COMMENT
        FROM SNOWFLAKE.ACCOUNT_USAGE.USERS
        WHERE NAME = '{user_name}'
        LIMIT 1
    """).to_pandas()
    if df.empty:
        return {}
    row = df.iloc[0]
    return {
        "name": row["NAME"],
        "email": row["EMAIL"],
        "disabled": row["DISABLED"] == "YES",
        "display_name": row["DISPLAY_NAME"],
        "default_role": row["DEFAULT_ROLE"],
        "default_warehouse": row["DEFAULT_WAREHOUSE"],
        "owner": row["OWNER"],
        "comment": row["COMMENT"]
    }

user_info = {}
selected_user = None
if st.session_state.user_mode == "edit":
    user_list = get_existing_users()
    selected_user = st.selectbox("Select a user to edit", user_list)
    if selected_user:
        user_info = get_user_details(selected_user)

# ------------------------ Form Layout ------------------------

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("*Name", value=user_info.get("name", ""))
    default_namespace = st.text_input("Default Namespace (optional)")
    default_role = st.text_input("*Default Role", value=user_info.get("default_role", ""))
    default_secondary_roles = st.text_input("Default Secondary Roles (optional)")
    default_warehouse = st.text_input("*Default Warehouse", value=user_info.get("default_warehouse", ""))
    display_name_input = st.text_input("*Display Name", value=user_info.get("display_name", ""))
    email = st.text_input("*Email", value=user_info.get("email", ""))
    disabled = st.checkbox("Disabled User", value=user_info.get("disabled", False))

with col2:
    user_type = st.selectbox("*User Type", ["PERSON", "SERVICE"])
    is_service = user_type == "SERVICE"

    first_name = st.text_input("*First Name", value="", disabled=is_service)
    last_name = st.text_input("*Last Name", value="", disabled=is_service)
    middle_name = st.text_input("Middle Name (optional)", disabled=is_service)
    network_policy = st.text_input("Network Policy (optional)")
    owner = st.text_input("*Owner", value=user_info.get("owner", "ACCOUNTADMIN"))
    password = st.text_input("*Password", type="password", value="", disabled=is_service)
    must_change_password = st.checkbox("Change Password on First Login", value=not is_service, disabled=is_service)

rsa_public_key = st.text_input("RSA Public Key (optional)")
comment = st.text_area("Comment (optional)")

# ------------------------ YAML Construction ------------------------

display_name = display_name_input.strip()
if not display_name and first_name.strip() and last_name.strip():
    display_name = f"{first_name.strip()} {last_name.strip()}"

user_data = {
    "name": name.strip(),
    "comment": comment.strip() or None,
    "default_namespace": default_namespace.strip() or None,
    "default_role": default_role.strip(),
    "default_secondary_roles": default_secondary_roles.strip() or None,
    "default_warehouse": default_warehouse.strip(),
    "disabled": disabled,
    "display_name": display_name.strip(),
    "email": email.strip(),
    "network_policy": network_policy.strip() or None,
    "owner": owner.strip(),
    "rsa_public_key": rsa_public_key.strip() or None,
    "type": user_type,
    "login_name": name.strip(),
}

if user_type == "PERSON":
    user_data["first_name"] = first_name.strip()
    user_data["last_name"] = last_name.strip()
    user_data["middle_name"] = middle_name.strip() or None
    user_data["must_change_password"] = must_change_password
    if password.strip():
        user_data["password"] = password.strip()

user_data_cleaned = {k: v for k, v in user_data.items() if v is not None}

# ------------------------ YAML Preview ------------------------

st.markdown("---")
yaml_stream = StringIO()
yaml.dump({"users": [user_data_cleaned]}, yaml_stream)

st.markdown('<h3 style="text-align: center;">User YAML Preview</h3>', unsafe_allow_html=True)
st.code(yaml_stream.getvalue(), language="yaml")

# ------------------------ GitHub PR Submission ------------------------

@st.cache_resource
def fetch_github_secrets():
    # TEMP fallback for dev until SYSTEM$GET_SECRET works
    import os
    import json
    return json.dumps({
        "username": os.getenv("GITHUB_PAT", "<your-token-here>"),
        "password": os.getenv("GITHUB_REPO", "jacksongreig/streamlit_SF_perms")
    })


def submit_to_github(yaml_string):
    import json
    secret_obj = json.loads(fetch_github_secrets())
    github_token = secret_obj["username"]
    github_repo = secret_obj["password"]

    pr_url = raise_github_pr(
        filename="users.yaml",
        file_contents=yaml_string,
        token=github_token,
        repo_name=github_repo
    )
    return pr_url

# ------------------------ Action Buttons ------------------------

if st.session_state.user_mode == "create":
    if st.button("Submit & Raise PR", use_container_width=True):
        if not name.strip():
            st.error("Name is required.")
        elif not default_role.strip() or not default_warehouse.strip():
            st.error("Default role and warehouse are required.")
        elif user_type == "PERSON" and not password.strip():
            st.error("Password is required for PERSON users.")
        else:
            try:
                pr_url = submit_to_github(yaml_stream.getvalue())
                st.success(f"PR created: [View PR]({pr_url})")
            except Exception as e:
                st.error(f"Failed to raise PR: {e}")
else:
    col_submit, col_delete = st.columns(2)

    with col_submit:
        if st.button("Update User & Raise PR", use_container_width=True):
            try:
                pr_url = submit_to_github(yaml_stream.getvalue())
                st.success(f"PR updated: [View PR]({pr_url})")
            except Exception as e:
                st.error(f"Failed to raise PR: {e}")

    with col_delete:
        if selected_user and st.button("Delete User & Raise PR", use_container_width=True):
            try:
                delete_stream = StringIO()
                yaml.dump({"users": [{"name": selected_user, "action": "delete"}]}, delete_stream)
                pr_url = submit_to_github(delete_stream.getvalue())
                st.success(f"Delete PR created: [View PR]({pr_url})")
            except Exception as e:
                st.error(f"Failed to raise delete PR: {e}")

# ------------------------ Footer ------------------------

st.markdown("---", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; color: grey; font-size: 0.85rem; padding: 1rem 0;'>
        © 2025 Created by Practiv
    </div>
""", unsafe_allow_html=True)

st.image("logo_practiv.png", use_container_width=True)
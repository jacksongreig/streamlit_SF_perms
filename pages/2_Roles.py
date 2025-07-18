import streamlit as st
from snowflake.snowpark.context import get_active_session
from ruamel.yaml import YAML
from io import StringIO
# from utils.github_integration import raise_github_pr
from utils.shared_css import inject_shared_css

# ── App Setup ─────────────────────────────────────────
st.set_page_config(page_title="Roles", layout="centered", initial_sidebar_state="collapsed")
inject_shared_css()
session = get_active_session()

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False
yaml.allow_unicode = True

# ── Page State ────────────────────────────────────────
if "role_mode" not in st.session_state:
    st.session_state.role_mode = "create"

# ── Header ────────────────────────────────────────────
st.markdown('<h1 style="text-align: center;">Roles</h1>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Mode Toggle ───────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if st.button("Create New Role"):
        st.session_state.role_mode = "create"
with col2:
    if st.button("Edit Existing Role"):
        st.session_state.role_mode = "edit"

st.markdown("---")
st.markdown(
    f"<h3 style='text-align: center;'>{'Create New Role' if st.session_state.role_mode == 'create' else 'Edit Current Role'}</h3>",
    unsafe_allow_html=True
)

# ── Helpers ───────────────────────────────────────────
@st.cache_data
def get_existing_roles():
    df = session.sql("SELECT DISTINCT name FROM SNOWFLAKE.ACCOUNT_USAGE.ROLES ORDER BY name").to_pandas()
    return df["NAME"].tolist()

def get_role_details(role_name: str):
    df = session.sql(f"""
        SELECT name, owner, comment
        FROM SNOWFLAKE.ACCOUNT_USAGE.ROLES
        WHERE name = '{role_name}'
        LIMIT 1
    """).to_pandas()
    if df.empty:
        return {}
    row = df.iloc[0]
    return {
        "name": row["NAME"],
        "owner": row["OWNER"],
        "comment": row["COMMENT"]
    }

# ── Form Fields ───────────────────────────────────────
role_info = {}
if st.session_state.role_mode == "edit":
    roles = get_existing_roles()
    selected_role = st.selectbox("Select a role to edit", roles)
    if selected_role:
        role_info = get_role_details(selected_role)

role_name = st.text_input("*Role Name", value=role_info.get("name", ""), placeholder="e.g. ANALYST")
comment = st.text_area("Comment (optional)", value=role_info.get("comment", ""), placeholder="Describe the role or leave blank")
owner_options = ["SECURITYADMIN", "ACCOUNTADMIN"]
owner_default = 0 if role_info.get("owner", "ACCOUNTADMIN") == "SECURITYADMIN" else 1
owner = st.selectbox("*Owner", options=owner_options, index=owner_default)

role_name_clean = role_name.strip()
comment_clean = comment.strip()

# ── YAML Generation ───────────────────────────────────
role_data = {
    "name": role_name_clean,
    "owner": owner
}
if comment_clean:
    role_data["comment"] = comment_clean

role_yaml = {"roles": [role_data]}
yaml_stream = StringIO()
yaml.dump(role_yaml, yaml_stream)

# ── YAML Preview ──────────────────────────────────────
st.markdown("---")
st.markdown('<h3 style="text-align: center;">YAML Preview</h3>', unsafe_allow_html=True)
st.code(yaml_stream.getvalue(), language="yaml")

# ── Submit / Delete Buttons ───────────────────────────
submit_label = "Submit & Raise PR" if st.session_state.role_mode == "create" else "Update & Raise PR"
col_submit, col_delete = st.columns(2)

with col_submit:
    if st.button(submit_label):
        if not role_name_clean:
            st.error("Role Name is required.")
        elif not owner:
            st.error("Owner is required.")
        else:
            try:
                filename = f"roles/{role_name_clean.lower().replace(' ', '_').replace('.', '_')}.yaml"
                # pr_url = raise_github_pr(...)
                st.success("PR logic ready — YAML generated successfully.")
            except Exception as e:
                st.error(f"Failed to Raise PR: {e}")

with col_delete:
    if st.session_state.role_mode == "edit" and role_info:
        if st.button("Delete Role", type="secondary"):
            if role_name_clean.upper() in ["ACCOUNTADMIN", "SECURITYADMIN", "SYSADMIN"]:
                st.error("You cannot delete a system-critical role.")
            else:
                st.warning(f'Confirm deletion of role: `{role_name_clean}`')
                confirm = st.radio("Are you sure?", ["No", "Yes"], horizontal=True, index=0)
                if confirm == "Yes":
                    delete_yaml = {
                        "roles": [
                            {
                                "name": role_name_clean,
                                "action": "delete"
                            }
                        ]
                    }
                    delete_stream = StringIO()
                    yaml.dump(delete_yaml, delete_stream)
                    try:
                        filename = f"roles/delete/{role_name_clean.lower().replace(' ', '_')}.yaml"
                        # pr_url = raise_github_pr(...)
                        st.success("Delete PR logic ready — YAML generated successfully.")
                        st.code(delete_stream.getvalue(), language="yaml")
                    except Exception as e:
                        st.error(f"Failed to raise delete PR: {e}")

# ── Footer ────────────────────────────────────────────
st.markdown("---", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; color: grey; font-size: 0.85rem; padding: 1rem 0;'>
        © 2025 Created by Practiv
    </div>
""", unsafe_allow_html=True)

st.image("logo_practiv.png", use_container_width=True)
import streamlit as st
from snowflake.snowpark.context import get_active_session
from ruamel.yaml import YAML
from io import StringIO
# from utils.github_integration import raise_github_pr
from utils.shared_css import inject_shared_css

st.set_page_config(page_title="Warehouses", layout="centered", initial_sidebar_state="collapsed")

inject_shared_css()
session = get_active_session()
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False
yaml.allow_unicode = True

if "warehouse_mode" not in st.session_state:
    st.session_state.warehouse_mode = "create"

st.markdown('<h1 style="text-align: center;">Warehouses</h1>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("Create New Warehouse"):
        st.session_state.warehouse_mode = "create"
with col2:
    if st.button("Edit Existing Warehouse"):
        st.session_state.warehouse_mode = "edit"

st.markdown("---")

st.markdown(f"<h3 style='text-align: center;'>{'Create New Warehouse' if st.session_state.warehouse_mode == 'create' else 'Edit Current Warehouse'}</h3>", unsafe_allow_html=True)

@st.cache_data
def get_existing_warehouses():
    df = session.sql("SELECT name FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES ORDER BY name").to_pandas()
    return df["NAME"].tolist()

def get_warehouse_details(wh_name: str):
    df = session.sql(f"""
        SELECT name, warehouse_size, warehouse_type, scaling_policy, auto_suspend,
               auto_resume, enable_query_acceleration, query_acceleration_max_scale_factor,
               min_cluster_count, max_cluster_count, max_concurrency_level,
               statement_timeout_in_seconds, statement_queued_timeout_in_seconds,
               resource_monitor, owner, comment
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES
        WHERE name = '{wh_name}'
        LIMIT 1
    """).to_pandas()
    if df.empty:
        return {}
    row = df.iloc[0]
    return {col.lower(): row[col] for col in df.columns}

wh_info = {}
if st.session_state.warehouse_mode == "edit":
    wh_list = get_existing_warehouses()
    selected_wh = st.selectbox("Select a warehouse to edit", wh_list)
    if selected_wh:
        wh_info = get_warehouse_details(selected_wh)

col1, col2 = st.columns(2)
with col1:
    wh_name = st.text_input("*Warehouse Name", value=wh_info.get("name", ""), placeholder="e.g. DEV_WH")
    warehouse_size = st.selectbox("Warehouse Size", ["XSMALL", "SMALL", "MEDIUM", "LARGE", "XLARGE"],
                                  index=["XSMALL", "SMALL", "MEDIUM", "LARGE", "XLARGE"].index(wh_info.get("warehouse_size", "XSMALL")))
    warehouse_type = st.selectbox("Warehouse Type", ["STANDARD", "SNOWPARK-OPTIMIZED"],
                                  index=["STANDARD", "SNOWPARK-OPTIMIZED"].index(wh_info.get("warehouse_type", "STANDARD")))
    scaling_policy = st.selectbox("Scaling Policy", ["STANDARD", "ECONOMY"],
                                  index=["STANDARD", "ECONOMY"].index(wh_info.get("scaling_policy", "STANDARD")))
    auto_suspend = st.number_input("Auto Suspend (seconds)", min_value=0, value=int(wh_info.get("auto_suspend", 60)))
    auto_resume = st.selectbox("Auto Resume", ["true", "false"], index=0 if wh_info.get("auto_resume", True) else 1) == "true"
    enable_query_acceleration = st.selectbox("Enable Query Acceleration", ["false", "true"],
                                             index=1 if wh_info.get("enable_query_acceleration", False) else 0) == "true"

with col2:
    query_accel_factor = st.number_input("Query Acceleration Max Scale Factor", min_value=0,
                                         value=int(wh_info.get("query_acceleration_max_scale_factor", 8)))
    min_cluster_count = st.number_input("Min Cluster Count", min_value=1, value=int(wh_info.get("min_cluster_count", 1)))
    max_cluster_count = st.number_input("Max Cluster Count", min_value=1, value=int(wh_info.get("max_cluster_count", 1)))
    max_concurrency_level = st.number_input("Max Concurrency Level", min_value=1, value=int(wh_info.get("max_concurrency_level", 8)))
    stmt_timeout = st.number_input("Statement Timeout (seconds)", min_value=0, value=int(wh_info.get("statement_timeout_in_seconds", 172800)))
    stmt_queue_timeout = st.number_input("Statement Queued Timeout (seconds)", min_value=0, value=int(wh_info.get("statement_queued_timeout_in_seconds", 0)))
    resource_monitor = st.text_input("Resource Monitor (optional)", value=wh_info.get("resource_monitor", ""))
    owner = st.text_input("*Owner", value=wh_info.get("owner", "ACCOUNTADMIN"))

comment = st.text_area("Comment (optional)", value=wh_info.get("comment", ""))

warehouse_data = {
    "name": wh_name.strip(),
    "warehouse_size": warehouse_size,
    "warehouse_type": warehouse_type,
    "scaling_policy": scaling_policy,
    "auto_suspend": auto_suspend,
    "auto_resume": auto_resume,
    "enable_query_acceleration": enable_query_acceleration,
    "query_acceleration_max_scale_factor": query_accel_factor,
    "min_cluster_count": min_cluster_count,
    "max_cluster_count": max_cluster_count,
    "max_concurrency_level": max_concurrency_level,
    "statement_timeout_in_seconds": stmt_timeout,
    "statement_queued_timeout_in_seconds": stmt_queue_timeout,
    "owner": owner.strip(),
    "comment": comment.strip() or None,
    "resource_monitor": resource_monitor.strip() or None
}

warehouse_yaml = {"warehouses": [warehouse_data]}
yaml_stream = StringIO()
yaml.dump(warehouse_yaml, yaml_stream)

st.markdown("---")

st.markdown('<h3 style="text-align: center;">User YAML Preview</h1>', unsafe_allow_html=True)

st.code(yaml_stream.getvalue(), language='yaml')

submit_label = "Submit & Create PR" if st.session_state.warehouse_mode == "create" else "Update & Raise PR"
col_submit, col_delete = st.columns([2, 1])

if st.button(submit_label):
    if not wh_name.strip():
        st.error("Warehouse Name is required.")
    elif not owner.strip():
        st.error("Owner is required.")
    else:
        try:
            filename = f"warehouses/{wh_name.lower().replace(' ', '_').replace('.', '_')}.yaml"
            # pr_url = raise_github_pr(
            #     filename=filename,
            #     file_contents=yaml_stream.getvalue(),
            #     token=st.secrets["GITHUB_TOKEN"],
            #     repo_name=st.secrets["GITHUB_REPO"]
            # )
            # st.success(f"PR created: [View PR]({pr_url})")
            st.success("PR logic ready — YAML generated successfully.")
        except Exception as e:
            st.error(f"Failed to create PR: {e}")

if st.session_state.warehouse_mode == "edit" and wh_info:
    with col_delete:
        if st.button("Delete Warehouse", type="secondary"):
            st.warning(f'Confirm deletion of warehouse: `{wh_name}`')
            confirm = st.radio("Are you sure?", ["No", "Yes"], horizontal=True, index=0)
            if confirm == "Yes":
                delete_yaml = {
                    "warehouses": [
                        {
                            "name": wh_name.strip(),
                            "action": "delete"
                        }
                    ]
                }
                delete_stream = StringIO()
                yaml.dump(delete_yaml, delete_stream)

                try:
                    filename = f"warehouses/delete/{wh_name.lower().replace(' ', '_')}.yaml"
                    # pr_url = raise_github_pr(
                    #     filename=filename,
                    #     file_contents=delete_stream.getvalue(),
                    #     token=st.secrets["GITHUB_TOKEN"],
                    #     repo_name=st.secrets["GITHUB_REPO"]
                    # )
                    # st.success(f"Delete PR created: [View PR]({pr_url})")
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
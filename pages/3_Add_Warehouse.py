import streamlit as st
from ruamel.yaml import YAML
from io import StringIO
from utils.github_integration import raise_github_pr
from utils.shared_css import inject_shared_css

st.set_page_config(
    page_title="Add Warehouse",
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
    st.markdown('<h1 style="text-align: center;">Add Warehouse</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        wh_name = st.text_input("*Warehouse Name", placeholder="e.g. DEV_WH")
        warehouse_size = st.selectbox("Warehouse Size", ["XSMALL", "SMALL", "MEDIUM", "LARGE", "XLARGE"])
        warehouse_type = st.selectbox("Warehouse Type", ["STANDARD", "SNOWPARK-OPTIMIZED"])
        scaling_policy = st.selectbox("Scaling Policy", ["STANDARD", "ECONOMY"])
        auto_suspend = st.number_input("Auto Suspend (seconds)", min_value=0, value=60)
        auto_resume = st.selectbox("Auto Resume", ["true", "false"]) == "true"
        enable_query_acceleration = st.selectbox("Enable Query Acceleration", ["false", "true"]) == "true"

    with col2:
        query_accel_factor = st.number_input("Query Acceleration Max Scale Factor", min_value=0, value=8)
        min_cluster_count = st.number_input("Min Cluster Count", min_value=1, value=1)
        max_cluster_count = st.number_input("Max Cluster Count", min_value=1, value=1)
        max_concurrency_level = st.number_input("Max Concurrency Level", min_value=1, value=8)
        stmt_timeout = st.number_input("Statement Timeout (seconds)", min_value=0, value=172800)
        stmt_queue_timeout = st.number_input("Statement Queued Timeout (seconds)", min_value=0, value=0)
        resource_monitor = st.text_input("Resource Monitor (optional)", placeholder="Leave blank if none")
        owner = st.text_input("*Owner", value="ACCOUNTADMIN")

    comment = st.text_area("Comment (optional)", placeholder="e.g. Analytics & dev workloads")

    # Build YAML
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

    st.subheader("YAML Preview")
    yaml_stream = StringIO()
    yaml.dump(warehouse_yaml, yaml_stream)
    st.code(yaml_stream.getvalue(), language='yaml')

    if st.button("Submit & Raise PR"):
        if not wh_name.strip():
            st.error("Warehouse Name is required.")
        elif not owner.strip():
            st.error("Owner is required.")
        else:
            try:
                filename = f"warehouses/{wh_name.lower().replace(' ', '_').replace('.', '_')}.yaml"
                pr_url = raise_github_pr(
                    filename=filename,
                    file_contents=yaml_stream.getvalue(),
                    token=st.secrets["GITHUB_TOKEN"],
                    repo_name=st.secrets["GITHUB_REPO"]
                )
                st.success(f"PR created: [View PR]({pr_url})")
            except Exception as e:
                st.error(f"Failed to create PR: {e}")

import streamlit as st
from ruamel.yaml import YAML
from io import StringIO
from github import Github
from datetime import datetime

# ========== Page Setup ==========
st.set_page_config(page_title="Add New User", layout="centered")

# ========== Styling ==========
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
    label, .stTextInput label, .stSelectbox label {
        color: #1a1a1a !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    .stButton > button {
        width: 100%;
        min-height: 60px;
        background-color: #003366 !important;
        color: white !important;
        font-size: 1.05rem;
        font-weight: 600;
        border: none !important;
        border-radius: 10px;
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #005599 !important;
        color: white !important;
    }
    .stButton > button:active {
        background-color: #001f3f !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ========== YAML Builder ==========
st.header("Add New Snowflake User")

username = st.text_input("Username", placeholder="e.g. jack.greig").strip()
default_role = st.text_input("Default Role", placeholder="e.g. ANALYST").strip().upper()
default_warehouse = st.text_input("Default Warehouse", placeholder="e.g. COMPUTE_WH").strip().upper()
disabled = st.checkbox("User is disabled")

# Optional settings
must_change_password = st.checkbox("User must change password on next login", value=True)
comment = st.text_input("Comment (optional)")

# ========== Build YAML ==========
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

user_yaml = {
    "users": [
        {
            "name": username,
            "default_role": default_role,
            "default_warehouse": default_warehouse,
            "disabled": disabled,
            "must_change_password": must_change_password,
        }
    ]
}
if comment:
    user_yaml["users"][0]["comment"] = comment

# ========== Preview ==========
st.subheader("🧾 YAML Preview")
yaml_stream = StringIO()
yaml.dump(user_yaml, yaml_stream)
st.code(yaml_stream.getvalue(), language='yaml')

# ========== GitHub PR Function ==========
def raise_github_pr(filename, file_contents):
    token = st.secrets["GITHUB_TOKEN"]
    repo_name = st.secrets["GITHUB_REPO"]

    g = Github(token)
    repo = g.get_repo(repo_name)

    base_branch = repo.default_branch
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    branch_name = f"feature/{filename.replace('/', '_').replace('.yaml','')}_{timestamp}"

    base = repo.get_branch(base_branch)
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base.commit.sha)

    repo.create_file(
        path=filename,
        message=f"add: {filename}",
        content=file_contents,
        branch=branch_name
    )

    pr = repo.create_pull(
        title=f"feat: add {filename}",
        body="Auto-generated from the Snowflake IaC Assistant.",
        head=branch_name,
        base=base_branch
    )

    return pr.html_url

# ========== Submit ==========
if st.button("🚀 Submit & Raise Pull Request"):
    if not username or not default_role or not default_warehouse:
        st.error("Please fill in all required fields.")
    else:
        filename = f"users/{username.replace('.', '_').lower()}.yaml"
        try:
            pr_url = raise_github_pr(filename, yaml_stream.getvalue())
            st.success(f"✅ Pull Request created: [View PR]({pr_url})")
        except Exception as e:
            st.error(f"❌ Failed to create PR: {e}")
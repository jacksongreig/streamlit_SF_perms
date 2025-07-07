
import os
import glob
from ruamel.yaml import YAML
import snowflake.connector # type: ignore

# === Load YAML files ===
yaml = YAML()
yaml_files = glob.glob("users/*.yaml")

if not yaml_files:
    print("No YAML files found in /users folder.")
    exit(0)

# === Connect to Snowflake ===
conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    role=os.environ["SNOWFLAKE_ROLE"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    database=os.environ["SNOWFLAKE_DATABASE"],
    schema=os.environ["SNOWFLAKE_SCHEMA"]
)

cs = conn.cursor()

# === Apply users ===
for filepath in yaml_files:
    print(f"🔍 Processing {filepath}")
    with open(filepath, "r") as f:
        content = yaml.load(f)

    users = content.get("users", [])
    for user in users:
        name = user["name"]
        role = user["default_role"]
        wh = user["default_warehouse"]
        disabled = user.get("disabled", False)
        change_pwd = user.get("must_change_password", True)
        comment = user.get("comment", "")

        print(f"➡️ Creating or replacing user '{name}'...")

        stmt = f"""
        CREATE OR REPLACE USER {name}
            DEFAULT_ROLE = {role}
            DEFAULT_WAREHOUSE = {wh}
            MUST_CHANGE_PASSWORD = {'TRUE' if change_pwd else 'FALSE'}
            DISABLED = {'TRUE' if disabled else 'FALSE'}
            COMMENT = '{comment}'
        """

        try:
            cs.execute(stmt)
            print(f"User '{name}' applied successfully.")
        except Exception as e:
            print(f"Error applying user '{name}': {e}")

cs.close()
conn.close()
print("🏁 Done.")

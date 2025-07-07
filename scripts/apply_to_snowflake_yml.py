import os
import subprocess
from ruamel.yaml import YAML
import snowflake.connector

# === Get Changed YAML Files from Last Commit ===
changed_files = subprocess.check_output(["git", "diff", "--name-only", "HEAD~1", "HEAD"]).decode("utf-8").splitlines()
yaml_files = [f for f in changed_files if f.endswith(".yaml")]

if not yaml_files:
    print("🚫 No YAML files changed in the last commit.")
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
yaml = YAML()

# === Apply each file ===
for filepath in yaml_files:
    print(f"🔍 Processing {filepath}")
    with open(filepath, "r") as f:
        content = yaml.load(f)

    # === Apply Users ===
    if "users" in content:
        for user in content["users"]:
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
                print(f"✅ User '{name}' applied successfully.")
            except Exception as e:
                print(f"❌ Error applying user '{name}': {e}")

    # === Apply Warehouses ===
    elif "warehouses" in content:
        for wh in content["warehouses"]:
            name = wh["name"]
            size = wh.get("size", "X-Small")
            suspend = wh.get("auto_suspend", 600)
            resume = wh.get("auto_resume", True)
            comment = wh.get("comment", "")

            print(f"➡️ Creating or replacing warehouse '{name}'...")
            stmt = f"""
            CREATE OR REPLACE WAREHOUSE {name}
                WAREHOUSE_SIZE = '{size}'
                AUTO_SUSPEND = {suspend}
                AUTO_RESUME = {'TRUE' if resume else 'FALSE'}
                COMMENT = '{comment}'
            """
            try:
                cs.execute(stmt)
                print(f"✅ Warehouse '{name}' applied successfully.")
            except Exception as e:
                print(f"❌ Error applying warehouse '{name}': {e}")

    # === Apply Roles ===
    elif "roles" in content:
        for role in content["roles"]:
            name = role["name"]
            comment = role.get("comment", "")

            print(f"➡️ Creating or replacing role '{name}'...")
            stmt = f"""
            CREATE OR REPLACE ROLE {name}
                COMMENT = '{comment}'
            """
            try:
                cs.execute(stmt)
                print(f"✅ Role '{name}' applied successfully.")
            except Exception as e:
                print(f"❌ Error applying role '{name}': {e}")

    # === Apply Grants ===
    elif "grants" in content:
        for grant in content["grants"]:
            role = grant["role"]
            priv = grant["privilege"]
            obj_type = grant["on"]["object_type"]
            obj_name = grant["on"]["name"]
            grant_opt = grant.get("with_grant_option", False)

            print(f"➡️ Granting {priv} on {obj_type} {obj_name} to role '{role}'...")
            stmt = f"""
            GRANT {priv} ON {obj_type} {obj_name} TO ROLE {role}
            {" WITH GRANT OPTION" if grant_opt else ""}
            """
            try:
                cs.execute(stmt)
                print(f"✅ Grant applied successfully.")
            except Exception as e:
                print(f"❌ Error applying grant: {e}")

cs.close()
conn.close()
print("🏁 All done.")
import os
import subprocess
from ruamel.yaml import YAML
import snowflake.connector

yaml = YAML()

# === Get changed YAML files (safe for GitHub Actions) ===
def get_changed_yaml_files():
    try:
        # Try to get last 2 commits
        result = subprocess.run(
            ["git", "log", "--format=%H", "-n", "2"],
            check=True,
            stdout=subprocess.PIPE,
            text=True
        )
        commits = result.stdout.strip().split("\n")
        if len(commits) < 2:
            raise Exception("Not enough commits to diff.")
        head, previous = commits[0], commits[1]
        diff_output = subprocess.check_output(["git", "diff", "--name-only", previous, head])
        changed = [f for f in diff_output.decode("utf-8").splitlines() if f.endswith(".yaml")]
        return changed
    except Exception as e:
        print(f"⚠️ Could not determine diff: {e}")
        print("🔁 Falling back to all YAML files in repo.")
        fallback = []
        for root, _, files in os.walk("."):
            for f in files:
                if f.endswith(".yaml"):
                    fallback.append(os.path.join(root, f))
        return fallback

# === Connect to Snowflake ===
def connect_to_snowflake():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"]
    )

# === Apply YAML Logic ===
def apply_yaml_file(filepath, cursor):
    print(f"🔍 Processing {filepath}")
    with open(filepath, "r") as f:
        content = yaml.load(f)

    if filepath.startswith("users/") and "users" in content:
        for user in content["users"]:
            name = user["name"]
            role = user["default_role"]
            wh = user["default_warehouse"]
            disabled = user.get("disabled", False)
            change_pwd = user.get("must_change_password", True)
            comment = user.get("comment", "")

            stmt = f"""
            CREATE OR REPLACE USER {name}
                DEFAULT_ROLE = {role}
                DEFAULT_WAREHOUSE = {wh}
                MUST_CHANGE_PASSWORD = {'TRUE' if change_pwd else 'FALSE'}
                DISABLED = {'TRUE' if disabled else 'FALSE'}
                COMMENT = '{comment}'
            """
            try:
                print(f"➡️ Creating or replacing user '{name}'...")
                cursor.execute(stmt)
                print(f"✅ User '{name}' applied successfully.")
            except Exception as e:
                print(f"❌ Error applying user '{name}': {e}")

    elif filepath.startswith("warehouses/") and "warehouses" in content:
        for wh in content["warehouses"]:
            name = wh["name"]
            size = wh.get("size", "X-Small")
            comment = wh.get("comment", "")
            stmt = f"""
            CREATE OR REPLACE WAREHOUSE {name}
                WAREHOUSE_SIZE = '{size}'
                AUTO_SUSPEND = 60
                AUTO_RESUME = TRUE
                COMMENT = '{comment}'
            """
            try:
                print(f"➡️ Creating or replacing warehouse '{name}'...")
                cursor.execute(stmt)
                print(f"✅ Warehouse '{name}' applied successfully.")
            except Exception as e:
                print(f"❌ Error applying warehouse '{name}': {e}")

    elif filepath.startswith("grants/") and "grants" in content:
        for grant in content["grants"]:
            role = grant["role"]
            privilege = grant["privilege"]
            object_type = grant["on"]["object_type"]
            name = grant["on"]["name"]
            with_option = "WITH GRANT OPTION" if grant.get("with_grant_option", False) else ""

            stmt = f"GRANT {privilege} ON {object_type} {name} TO ROLE {role} {with_option}"
            try:
                print(f"➡️ Granting {privilege} on {object_type} {name} to role {role}...")
                cursor.execute(stmt)
                print(f"✅ Grant applied successfully.")
            except Exception as e:
                print(f"❌ Error applying grant: {e}")

    else:
        print(f"⚠️ Unsupported or malformed YAML file: {filepath}")

# === Main ===
def main():
    yaml_files = get_changed_yaml_files()
    if not yaml_files:
        print("🚫 No YAML files to apply.")
        return

    conn = connect_to_snowflake()
    cs = conn.cursor()

    for file in yaml_files:
        apply_yaml_file(file, cs)

    cs.close()
    conn.close()
    print("🏁 Done.")

if __name__ == "__main__":
    main()

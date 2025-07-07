import os
import snowflake.connector
import yaml
import glob

# Connect to Snowflake
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

# Load YAML files
for filepath in glob.glob("users/*.yaml"):
    with open(filepath) as f:
        data = yaml.safe_load(f)
        for user in data.get("users", []):
            name = user["name"]
            role = user["default_role"]
            wh = user["default_warehouse"]
            print(f"Creating user: {name}")

            cs.execute(f"CREATE USER IF NOT EXISTS {name} DEFAULT_ROLE = {role} DEFAULT_WAREHOUSE = {wh}")

cs.close()
conn.close()
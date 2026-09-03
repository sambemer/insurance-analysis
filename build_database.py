import sqlite3
import pandas as pd

conn = sqlite3.connect("insurance.db")

customers = pd.read_csv("customers.csv")
auto = pd.read_csv("auto_policies.csv")
home = pd.read_csv("home_policies.csv")

customers.to_sql("customers", conn, if_exists="replace", index=False)
auto.to_sql("auto_policies", conn, if_exists="replace", index=False)
home.to_sql("home_policies", conn, if_exists="replace", index=False)

# Helpful indexes for join performance
cur = conn.cursor()
cur.execute("CREATE INDEX IF NOT EXISTS idx_auto_customer ON auto_policies(customer_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_home_customer ON home_policies(customer_id);")
conn.commit()
conn.close()

print("insurance.db built with tables: customers, auto_policies, home_policies")

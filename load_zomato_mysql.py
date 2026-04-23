import pandas as pd
import mysql.connector
from mysql.connector import Error
import math

# ─────────────────────────────────────────
#  CONFIG — add your password
# ─────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "Anshul@2106",   # ← replace this
}
DB_NAME    = "zomato_delhi"
TABLE_NAME = "restaurants"
INPUT_FILE = "zomato_delhi_clean.csv"

# ─────────────────────────────────────────
#  CONNECT
# ─────────────────────────────────────────
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Connected to MySQL!\n")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")
    print(f"Database '{DB_NAME}' ready.\n")
except Error as e:
    print(f"[!] Connection failed: {e}")
    exit()

# ─────────────────────────────────────────
#  LOAD CSV
# ─────────────────────────────────────────
df = pd.read_csv(INPUT_FILE)
df = df.where(pd.notnull(df), None)
print(f"Loaded {len(df)} rows from {INPUT_FILE}")
print(f"Columns: {list(df.columns)}\n")

# ─────────────────────────────────────────
#  CREATE TABLE
# ─────────────────────────────────────────
cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
cursor.execute(f"""
CREATE TABLE {TABLE_NAME} (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(300),
    locality        VARCHAR(200),
    cuisines        TEXT,
    rating          FLOAT,
    price_for_two   FLOAT,
    votes           FLOAT,
    city            VARCHAR(100),
    source          VARCHAR(50),
    price_band      VARCHAR(50),
    primary_cuisine VARCHAR(100)
)
""")
print(f"Table '{TABLE_NAME}' created.\n")

# ─────────────────────────────────────────
#  INSERT
# ─────────────────────────────────────────
def clean_val(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    return v

cols = list(df.columns)
placeholders = ", ".join(["%s"] * len(cols))
col_names = ", ".join(cols)
insert_sql = f"INSERT INTO {TABLE_NAME} ({col_names}) VALUES ({placeholders})"

rows = [tuple(clean_val(v) for v in row) for row in df.itertuples(index=False, name=None)]
cursor.executemany(insert_sql, rows)
conn.commit()
print(f"Inserted {cursor.rowcount} rows.\n")

# ─────────────────────────────────────────
#  VERIFY
# ─────────────────────────────────────────
cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
print(f"Verified: {cursor.fetchone()[0]} rows in MySQL\n")

cursor.execute(f"""
    SELECT locality, COUNT(*) as count
    FROM {TABLE_NAME}
    GROUP BY locality
    ORDER BY count DESC
    LIMIT 5
""")
print("Top 5 localities:")
for row in cursor.fetchall():
    print(f"  {row[0]:<30} {row[1]}")

cursor.close()
conn.close()
print(f"\nDone! Open MySQL Workbench → zomato_delhi → restaurants")

import pandas as pd
import sqlite3

# Load the CSV
df = pd.read_csv("sales data analysis.csv", encoding="latin1")

# Save to SQLite database
conn = sqlite3.connect("sales.db")
df.to_sql("sales", conn, if_exists="replace", index=False)

print("✅ sales.db created successfully.")

cursor = conn.cursor()
cursor.execute("PRAGMA table_info(sales)")
for col in cursor.fetchall():
    print(col)
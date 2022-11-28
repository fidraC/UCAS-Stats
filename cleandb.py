### Clean up the database

# Imports
import sqlite3
from sys import argv

if len(argv) != 2:
    print("Usage: python cleandb.py [database]")
    exit(1)

# Connect to the database
conn = sqlite3.connect(argv[1])
c = conn.cursor()

data = c.execute("SELECT id, entry_requirements, fees, average_salary, employment_rate, name FROM courses").fetchall()

conn.close()

valid_data = []
for row in data:
    # ID
    id = row[0]
    # Entry Requirements
    try:
        entry = int(row[1])
    except ValueError:
        continue
    # Fees
    try:
        fees = int(row[2]) 
    except ValueError:
        continue
    # Average Salary
    try:
        salary = int(row[3].replace("k", "000"))
    except ValueError:
        continue
    # Employment Rate
    try:
        employment = int(row[4])
    except ValueError:
        continue
    valid_data.append({'id': id, 'entry': entry, 'fees': fees, 'salary': salary, 'employment': employment, 'name': row[5]})

# Insert the data into a new database
conn = sqlite3.connect(argv[1].replace(".db", "_clean.db"))
c = conn.cursor()

c.execute("CREATE TABLE courses (id INTEGER PRIMARY KEY, entry_requirements INTEGER, fees INTEGER, average_salary INTEGER, employment_rate INTEGER, name TEXT)")
for row in valid_data:
    c.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?)", (row['id'], row['entry'], row['fees'], row['salary'], row['employment'], row['name']))

conn.commit()
conn.close()

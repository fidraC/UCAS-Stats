# Clean the data for bivariate analysis
import sqlite3
from sys import argv

if len(argv) < 4:
    print("Usage: python clean_bivariate.py <database> <field1> <field2>")
    exit(1)

# Connect to the database
conn = sqlite3.connect(argv[1])
c = conn.cursor()

data = c.execute('SELECT ' + argv[2] + ', ' + argv[3] + ', id, name FROM courses').fetchall()

conn.close()
del conn, c

valid_data = []
for row in data:
    try:
        field1 = int(row[0].replace('k', '000'))
    except ValueError:
        continue
    try:
        field2 = int(row[1].replace('k', '000'))
    except ValueError:
        continue
    valid_data.append({'field1': field1, 'field2': field2, 'id': row[2], 'name': row[3]})

del data

# Insert the data into a new database
conn = sqlite3.connect(argv[1].replace('.db', '_cleaned_bivariate.db'))
c = conn.cursor()

c.execute('CREATE TABLE courses (id INTEGER PRIMARY KEY, ' + argv[2] + ' INTEGER, ' + argv[3] + ' INTEGER, name TEXT, original_id INTEGER)')
for row in valid_data:
    c.execute('INSERT INTO courses VALUES (?, ?, ?, ?, ?)', (None, row['field1'], row['field2'], row['name'], row['id']))

conn.commit()
conn.close()

del conn, c, valid_data

### Calculates statistical values for a given dataset

from sys import argv
import sqlite3
import matplotlib.pyplot as plt
import json

def median(values):
    values.sort()
    if len(values) % 2 == 0:
        return (values[len(values) // 2] + values[len(values) // 2 - 1]) / 2
    else:
        return values[len(values) // 2]
    # Explain what the code above does
    # 1. Sort the values
    # 2. If the length of the list is even, return the average of the two middle values
    # 3. If the length of the list is odd, return the middle value

def quartile(values, q):
    values.sort()
    if q == 1:
        return median(values[:len(values) // 2])
    elif q == 3:
        return median(values[len(values) // 2:]) 
    else:
        raise ValueError('Quartile must be 1 or 3')
    # Explain what the code above does
    # 1. Sort the values
    # 2. If q is 1, return the median of the first half of the list
    # 3. If q is 3, return the median of the second half of the list
    # 4. If q is neither 1 nor 3, raise a ValueError

def get_stats(db, table, field):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    data = c.execute('SELECT ' + field + ' FROM ' + table).fetchall()
    conn.close()
    del conn
    del c
    # Construct a list of values from the data
    values = []
    for row in data:
        values.append(row[0])
    # Deallocate the data
    del data
    minimum = min(values)
    maximum = max(values)
    q1 = quartile(values, 1)
    q3 = quartile(values, 3)
    iqr = q3 - q1
    med = median(values)
    range_val = maximum - minimum
    return {'min': minimum, 'q1': q1, 'med': med, 'q3': q3, 'max': maximum, 'iqr': iqr, 'range': range_val}

def box_plot(min, q1, med, q3, max, field):
    # Create a horizontal box plot
    plt.boxplot([min, q1, med, q3, max], vert=False)
    # Add labels
    plt.ylabel(field, fontdict={'fontsize': 14})
    plt.show()

if __name__ == '__main__':
    if len(argv) != 4:
        print('Usage: get_stats.py <database> <table> <field>')
        exit(1)
    stats = get_stats(argv[1], argv[2], argv[3])
    print(json.dumps(stats, indent=2))
    box_plot(stats['min'], stats['q1'], stats['med'], stats['q3'], stats['max'], argv[3])

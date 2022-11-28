import sqlite3
from sys import argv
import matplotlib.pyplot as plt
import json

def median(values):
    values.sort()
    if len(values) % 2 == 0:
        return (values[len(values) // 2] + values[len(values) // 2 - 1]) / 2
    else:
        return values[len(values) // 2]

def quartile(values, q):
    values.sort()
    if len(values) == 1:
        return values[0]
    if q == 1:
        return median(values[:len(values) // 2])
    elif q == 3:
        return median(values[len(values) // 2:]) 
    else:
        raise ValueError('Quartile must be 1 or 3')

def get_stats(dict_array, field):
    # Construct a list of values from the data
    values = []
    for row in dict_array:
        values.append(row[field])
    minimum = min(values)
    q1 = quartile(values, 1)
    med = median(values)
    q3 = quartile(values, 3)
    maximum = max(values)
    return {'min': minimum, 'q1': q1, 'med': med, 'q3': q3, 'max': maximum}

if __name__ == '__main__':
    if len(argv) != 3:
        print('Usage: python make_stat_graph.py <database> <field>')
        exit(1)
    field_arg = argv[2]
    conn = sqlite3.connect(argv[1])
    c = conn.cursor()
    data = c.execute('SELECT id, entry_requirements, fees, average_salary, employment_rate FROM courses').fetchall()
    conn.close()
    del conn
    del c
    # Construct an array of values from the data
    values = []
    for row in data:
        values.append({'id': row[0], 'entry_requirements': row[1], 'fees': row[2], 'average_salary': row[3], 'employment_rate': row[4]})
    # Deallocate the data
    del data
    # Classify the data by unique entry requirements
    sorted_values = []
    for value in values:
        if len(sorted_values) == 0:
            sorted_values.append([value])
        else:
            for i in range(len(sorted_values)):
                if sorted_values[i][0]['entry_requirements'] == value['entry_requirements']:
                    sorted_values[i].append(value)
                    break
                elif i == len(sorted_values) - 1:
                    sorted_values.append([value])
    del values
    # Construct points for a line graph for each entry requirement
    stats = []

    for requirement in sorted_values:
        # Construct a list of coordinates for the line graph
        fees_coordinates = []
        employment_rate_coordinates = []
        average_salary_coordinates = []
        # Get the min, q1, med, q3, and max for each field
        fees_coordinates.append(get_stats(requirement, 'fees'))
        employment_rate_coordinates.append(get_stats(requirement, 'employment_rate'))
        average_salary_coordinates.append(get_stats(requirement, 'average_salary'))
        # Append the coordinates to the stats array
        stats.append({'entry_requirements': requirement[0]['entry_requirements'], 'fees': fees_coordinates, 'employment_rate': employment_rate_coordinates, 'average_salary': average_salary_coordinates})
    
    del sorted_values

    ### Display the line graph (only one field is displayed at a time)
    # Construct the points for the line graph
    # There are 5 lines in the graph for each field
    # The lines are the min, q1, med, q3, and max
    # The x-axis is the entry requirements
    # The y-axis is the value of the field
    min_line_coordinates = []
    q1_line_coordinates = []
    med_line_coordinates = []
    q3_line_coordinates = []
    max_line_coordinates = []
    # Sort the stats by entry requirements
    stats.sort(key=lambda x: x['entry_requirements'])
    for entries in stats:
        x = entries['entry_requirements']
        min_line_coordinates.append((x, entries[field_arg][0]['min']))
        q1_line_coordinates.append((x, entries[field_arg][0]['q1']))
        med_line_coordinates.append((x, entries[field_arg][0]['med']))
        q3_line_coordinates.append((x, entries[field_arg][0]['q3']))
        max_line_coordinates.append((x, entries[field_arg][0]['max']))
    # Plot the points
    plt.plot(*zip(*min_line_coordinates), label='min')
    plt.plot(*zip(*q1_line_coordinates), label='q1')
     # Make the median line thicker
    plt.plot(*zip(*med_line_coordinates), label='med', linewidth=5)
    plt.plot(*zip(*q3_line_coordinates), label='q3')
    plt.plot(*zip(*max_line_coordinates), label='max')
    # Add a legend
    plt.legend()
    # Add a title
    plt.title('Statistics for ' + field_arg)
    # Add labels to the axes
    plt.xlabel('Entry Requirements')
    plt.ylabel(field_arg)
    # Display the graph
    plt.show()

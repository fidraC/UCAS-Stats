import sqlite3
import sys
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) < 5:
    print("Usage: python bivariate_graph.py <database> <table> <x-axis> <y-axis>")
    sys.exit(1)

db = sys.argv[1]
table = sys.argv[2]
x_axis = sys.argv[3]
y_axis = sys.argv[4]

conn = sqlite3.connect(db)
c = conn.cursor()
data = c.execute("SELECT %s, %s FROM %s" % (x_axis, y_axis, table)).fetchall()
conn.close()

x = [d[0] for d in data]
y = [d[1] for d in data]

del data, c, conn

# Create scatter plot in another window
plt.scatter(x, y)
plt.xlabel(x_axis)
plt.ylabel(y_axis)
# Show plot and continue without waiting
plt.show(block=False)

# Clear plot
plt.clf()

# Remove outliers outside of % quartile
q1 = np.percentile(x, 3)
q3 = np.percentile(x, 97)
iqr = q3 - q1
lower_bound = q1 - (1.5 * iqr)
upper_bound = q3 + (1.5 * iqr)
outliers = []
for i in range(len(x)):
    if x[i] < lower_bound or x[i] > upper_bound:
        y[i] = None
        x[i] = None
        outliers.append(i)
print(len(outliers))

# Remove None values
x = [d for d in x if d is not None]
y = [d for d in y if d is not None]

# Remove outliers outside of % quartile
q1 = np.percentile(y, 3)
q3 = np.percentile(y, 97)
iqr = q3 - q1
lower_bound = q1 - (1.5 * iqr)
upper_bound = q3 + (1.5 * iqr)
outliers = []
for i in range(len(y)):
    if y[i] < lower_bound or y[i] > upper_bound:
        y[i] = None
        x[i] = None
        outliers.append(i)
print(len(outliers))

# Remove None values
x = [d for d in x if d is not None]
y = [d for d in y if d is not None]


# Plot again
plt.scatter(x, y)
plt.xlabel(x_axis)
plt.ylabel(y_axis)

# Find line of best fit
m, b = np.polyfit(x, y, 1)
plt.plot(x, m*np.array(x) + b, color='red')
# Label line of best fit with mx + b
plt.text(0.05, 0.95, "y = %.4fx + %.2f" % (m, b), transform=plt.gca().transAxes, fontsize=14, verticalalignment='top')

plt.show()

# Calculate pearson correlation coefficient
from scipy import stats
print(stats.pearsonr(x, y))
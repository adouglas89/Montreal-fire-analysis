import json
import numpy as np
import matplotlib.pyplot as plt

with open("monthly_fire_counts_verdun_all_time.json", "r") as file:
    data = json.load(file)
print(data)

data.sort()
def format_month(month_num):
    """Convert numeric month back to yyyy/mm format"""
    year = month_num // 12
    month = month_num % 12
    if month == 0:
        year -= 1
        month = 12
    return f"{year}/{month:02d}"
new_data = []
for entry in data:
    new_format_month = format_month(entry[0])
    new_data.append([new_format_month,entry[1]])

monthly_array = np.array(new_data)


# ---------------------------------------------------------
# Step 10: Prepare data for Matplotlib
# ---------------------------------------------------------

months = []
number_of_fires = []

for row in monthly_array:
    months.append(row[0])
    number_of_fires.append(int(row[1]))
print("done6")

# ---------------------------------------------------------
# Step 11: Make the line graph
# ---------------------------------------------------------

plt.plot(months, number_of_fires)

plt.title("Number of Valid Fires per Month in Verdun")
plt.xlabel("Month")
plt.ylabel("Number of Valid Fires")

plt.xticks(rotation=45)

plt.show()
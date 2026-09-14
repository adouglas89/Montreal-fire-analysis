import csv
import numpy as np
import matplotlib.pyplot as plt


# Name of the CSV file
filename = "donneesouvertes-interventions-sim_2015_2022.csv"


# ---------------------------------------------------------
# Step 1: Convert the CSV file into a list of lists
# ---------------------------------------------------------

spreadsheet = []

file = open(filename, "r", encoding="utf-8-sig")
reader = csv.reader(file)

for row in reader:
    spreadsheet.append(row)

file.close()


# ---------------------------------------------------------
# Step 2: Get the column headers
# ---------------------------------------------------------

headers = spreadsheet[0]


# Find the column numbers we need
date_column = headers.index("CREATION_DATE_TIME")
description_column = headers.index("DESCRIPTION_GROUPE")
incident_type_column = headers.index("INCIDENT_TYPE_DESC")
arrond_column = headers.index("NOM_ARROND")


# ---------------------------------------------------------
# Step 3: Keep only rows where DESCRIPTION_GROUPE is INCENDIE
# ---------------------------------------------------------

incendie_rows = []

for i in range(1, len(spreadsheet)):
    row = spreadsheet[i]

    if row[description_column] == "INCENDIE":
        incendie_rows.append(row)

print("done1")
print(len(incendie_rows))
# ---------------------------------------------------------
# Step 4: Remove rows with "sans feu" in INCIDENT_TYPE_DESC
# ---------------------------------------------------------

valid_fire_rows = []

for row in incendie_rows:# we don't seem to need this one.  If it says INCENDIE its a fire.
    incident_type = row[incident_type_column]

    if "sans feu" not in incident_type.lower():
        valid_fire_rows.append(row)
print("done2")
print(len(valid_fire_rows))
# ---------------------------------------------------------
# Step 5: Keep only the date and NOM_ARROND columns
# ---------------------------------------------------------

date_and_arrond_rows = []

for row in valid_fire_rows:
    date = row[date_column]
    arrond = row[arrond_column]

    new_row = [date, arrond]
    date_and_arrond_rows.append(new_row)
print("done3")

# ---------------------------------------------------------
# Step 6: Keep only rows from Verdun
# ---------------------------------------------------------

verdun_rows = []

for row in date_and_arrond_rows:
    arrond = row[1]

    if arrond == "Verdun":
        verdun_rows.append(row)

print("total fires in verdun:")
print(len(verdun_rows))

# ---------------------------------------------------------
# Step 7: Count how many fires happened in each month
# ---------------------------------------------------------

# ---------------------------------------------------------
# Count Verdun fires by month
# ---------------------------------------------------------

monthly_counts = []

for row in verdun_rows:
    date = row[0]
    month = date[0:7]

    found_month = False

    for month_row in monthly_counts:
        if month_row[0] == month:
            month_row[1] = month_row[1] + 1
            found_month = True
            break

    if found_month == False:
        monthly_counts.append([month, 1])

#print(monthly_counts)
# ---------------------------------------------------------
# Add missing months with zero fires
# ---------------------------------------------------------

monthly_counts.sort()

complete_monthly_counts = []

print("done5")
# ---------------------------------------------------------
# Step 8: Sort the monthly counts by month
# ---------------------------------------------------------

monthly_counts.sort()
# Original data - example (you can replace this with your actual data)
original_data = monthly_counts

# Step 1: Find the first and last months chronologically
def parse_month(month_str):
    """Convert yyyy/mm to a comparable value (year*12 + month)"""
    year, month = month_str.split('/')
    return int(year) * 12 + int(month)

def format_month(month_num):
    """Convert numeric month back to yyyy/mm format"""
    year = month_num // 12
    month = month_num % 12
    if month == 0:
        year -= 1
        month = 12
    return f"{year}/{month:02d}"

# Get the first and last months from the original data
first_month_num = parse_month(original_data[0][0])
last_month_num = parse_month(original_data[0][0])

for item in original_data:
    month_num = parse_month(item[0])
    if month_num < first_month_num:
        first_month_num = month_num
    if month_num > last_month_num:
        last_month_num = month_num

# Step 2: Create a complete list with all months and zeros
complete_data = []
current_month = first_month_num
while current_month <= last_month_num:
    month_str = format_month(current_month)
    complete_data.append([month_str, 0])
    current_month += 1

# Step 3: Combine the two lists
# Create a dictionary for quick lookup of original values
original_dict = {}
for item in original_data:
    original_dict[item[0]] = item[1]

# Update the complete data with values from the original
for item in complete_data:
    month = item[0]
    if month in original_dict:
        item[1] = original_dict[month]



# ---------------------------------------------------------
# Step 9: Convert the list of lists into a NumPy array
# ---------------------------------------------------------
complete_data.sort()
monthly_array = np.array(complete_data)


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
import csv
import numpy as np
import matplotlib.pyplot as plt


# Name of the CSV file
filename = "donneesouvertes-interventions-sim2020.csv"


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
# ---------------------------------------------------------
# Step 4: Remove rows with "sans feu" in INCIDENT_TYPE_DESC
# ---------------------------------------------------------

valid_fire_rows = []

for row in incendie_rows:
    incident_type = row[incident_type_column]

    if "sans feu" not in incident_type.lower():
        valid_fire_rows.append(row)
print("done2")

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

print("done3")
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


# ---------------------------------------------------------
# Add missing months with zero fires
# ---------------------------------------------------------

monthly_counts.sort()

complete_monthly_counts = []

if len(monthly_counts) > 0:

    first_month = monthly_counts[0][0]
    last_month = monthly_counts[len(monthly_counts) - 1][0]

    first_year = int(first_month[0:4])
    first_month_number = int(first_month[5:7])

    last_year = int(last_month[0:4])
    last_month_number = int(last_month[5:7])

    current_year = first_year
    current_month_number = first_month_number

    while current_year < last_year or (current_year == last_year and current_month_number <= last_month_number):

        if current_month_number < 10:
            current_month_text = str(current_year) + "-0" + str(current_month_number)
        else:
            current_month_text = str(current_year) + "-" + str(current_month_number)

        count_for_this_month = 0

        for month_row in monthly_counts:
            if month_row[0] == current_month_text:
                count_for_this_month = month_row[1]

        complete_monthly_counts.append([current_month_text, count_for_this_month])

        current_month_number = current_month_number + 1

        if current_month_number == 13:
            current_month_number = 1
            current_year = current_year + 1
print("done5")
# ---------------------------------------------------------
# Step 8: Sort the monthly counts by month
# ---------------------------------------------------------

monthly_counts.sort()


# ---------------------------------------------------------
# Step 9: Convert the list of lists into a NumPy array
# ---------------------------------------------------------

monthly_array = np.array(complete_monthly_counts)


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
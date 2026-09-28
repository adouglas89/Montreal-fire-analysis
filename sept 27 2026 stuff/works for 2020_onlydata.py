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

def parse_month(month_str):
    """Convert yyyy/mm to a comparable value (year*12 + month)"""
    year, month = month_str.split('-')
    return int(year) * 12 + int(month)

def format_month(month_num):
    """Convert numeric month back to yyyy/mm format"""
    year = month_num // 12
    month = month_num % 12
    if month == 0:
        year -= 1
        month = 12
    return f"{year}/{month:02d}"

# ---------------------------------------------------------
# Step 7: Count how many fires happened in each month
# ---------------------------------------------------------
verdun_rows.sort()
monthly_counts = []
print(verdun_rows)
start_month = verdun_rows[0][0][0:7]
end_month = verdun_rows[-1][0][0:7]
x =  parse_month(start_month)
while x <= parse_month(end_month):
    monthly_counts.append([x,0])
    x += 1
for row in verdun_rows:
    date = row[0]
    month = date[0:7]
    integer_month = parse_month(month)
    index_for_month = integer_month - parse_month(start_month)
    monthly_counts[index_for_month][1] +=1
#print(monthly_counts)
#sys.exit()        
                   
    

print("done5")


# ---------------------------------------------------------
# Step 9: Convert the list of lists into a NumPy array
# ---------------------------------------------------------

import json
import importlib
set1 = importlib.import_module("works for oneiwth nodate_onlydata")
set2 = importlib.import_module("for2005-2014filev2_onlydata")
set3 = importlib.import_module("works for 2015-2022v2_onlydata")
set4 = importlib.import_module("works for 2020_onlydata")

final_set = set1.monthly_counts+set2.monthly_counts+set3.monthly_counts+set4.monthly_counts

with open("monthly_fire_counts_verdun_all_time.json", "w") as file:
    json.dump(final_set, file)
print("file exported")
import sys
from pathlib import Path
import pandas as pd

# The 2005-2014 file uses older names; rename them to the names used from 2015 on.
# Other old names (neighbourhoods, cities, incident types) are listed in mappings/ but not applied.
OLD_GROUP_NAMES = {
    "Incendies de bâtiments": "INCENDIE",
    "Autres incendies": "AUTREFEU",
    "Sans incendie": "SANS FEU",
    "Premier répondant": "1-REPOND",
    "Fausses alertes/annulations": "FAU-ALER",
}

OLD_NEIGHBOURHOOD_NAMES = {
    "Verdun / Ïle-des-Soeurs": "Verdun",  # used 2005-2007
}

data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
files = sorted(data_dir.glob("*.csv"))
merged = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

# Keep the day only; the files use different date formats
merged["CREATION_DATE_TIME"] = pd.to_datetime(merged["CREATION_DATE_TIME"], format="mixed").dt.date
merged["INCIDENT_TYPE_DESC"] = merged["INCIDENT_TYPE_DESC"].str.strip()

# Use the same names across all years
merged["DESCRIPTION_GROUPE"] = merged["DESCRIPTION_GROUPE"].replace(OLD_GROUP_NAMES)
merged["NOM_ARROND"] = merged["NOM_ARROND"].replace(OLD_NEIGHBOURHOOD_NAMES)

# The files overlap for 2020-2022; the overlapping rows differ only by slightly adjusted coordinates
coords = ["MTM8_X", "MTM8_Y", "LONGITUDE", "LATITUDE"]
merged = merged.drop_duplicates(subset=merged.columns.difference(coords))

Path("processed_data").mkdir(exist_ok=True)
merged.to_csv("processed_data/merged.csv", index=False)
print(f"Merged {len(files)} files -> processed_data/merged.csv ({len(merged)} rows)")

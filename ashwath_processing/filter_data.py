import pandas as pd

INPUT_PATH = "processed_data/merged.csv"
OUTPUT_PATH = "processed_data/filtered.csv"

# Groups to keep (DESCRIPTION_GROUPE)
GROUPS = ["INCENDIE", "AUTREFEU"]

# Optional: for a group, keep only these descriptions (INCIDENT_TYPE_DESC).
# Groups not listed here keep all their descriptions.
DESCRIPTIONS = {
    "AUTREFEU": ["Feu de cheminée *"],
}

df = pd.read_csv(INPUT_PATH)

keep = pd.Series(False, index=df.index)
for group in GROUPS:
    in_group = df["DESCRIPTION_GROUPE"] == group
    if group in DESCRIPTIONS:
        in_group &= df["INCIDENT_TYPE_DESC"].isin(DESCRIPTIONS[group])
    keep |= in_group

filtered = df[keep]
filtered.to_csv(OUTPUT_PATH, index=False)
print(f"Kept {len(filtered)} of {len(df)} rows -> {OUTPUT_PATH}")
print(filtered.groupby(["DESCRIPTION_GROUPE", "INCIDENT_TYPE_DESC"]).size().to_string())

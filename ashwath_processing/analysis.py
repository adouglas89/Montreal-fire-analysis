from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

INPUT_PATH = "processed_data/filtered.csv"

# Neighbourhood to plot. Must match one of these exactly (accents included):
#   Ahuntsic-Cartierville
#   Anjou
#   Côte-des-Neiges-Notre-Dame-de-Grâce
#   Indéterminé                  (not assigned to a neighbourhood)
#   L'Île-Bizard-Sainte-Geneviève
#   Lachine
#   LaSalle
#   Le Plateau-Mont-Royal
#   Le Sud-Ouest
#   Mercier-Hochelaga-Maisonneuve
#   Montréal-Nord
#   Outremont
#   Pierrefonds-Roxboro
#   Rivière-des-Prairies-Pointe-aux-Trembles
#   Rosemont-La Petite-Patrie
#   Saint-Laurent
#   Saint-Léonard
#   Verdun
#   Ville-Marie
#   Villeray-Saint-Michel-Parc-Extension
NEIGHBOURHOOD = "Verdun"

# Range of years to plot (both years included)
START_YEAR = 2005
END_YEAR = 2025

# ---------------------------------------------------------------------------
# Count fires per year
# ---------------------------------------------------------------------------

fires = pd.read_csv(INPUT_PATH, parse_dates=["CREATION_DATE_TIME"])
fires = fires[fires["NOM_ARROND"] == NEIGHBOURHOOD]

years = range(START_YEAR, END_YEAR + 1)
fire_year = fires["CREATION_DATE_TIME"].dt.year
fires_per_year = fire_year.value_counts().reindex(years, fill_value=0)  # group by year, fill missing years with 0

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

BACKGROUND = "#fcfcfb"
LINE = "#2a78d6"
TITLE_TEXT = "#0b0b0b"
LABEL_TEXT = "#52514e"
GRID = "#e5e4e0"
AXIS = "#c3c2b7"

fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=BACKGROUND)
ax.set_facecolor(BACKGROUND)

# Line with a dot for each year
ax.plot(years, fires_per_year.values, color=LINE, linewidth=2, marker="o", markersize=5)

# Write the count just above each dot
for year, count in fires_per_year.items():
    ax.annotate(count, (year, count), textcoords="offset points", xytext=(0, 8),
                ha="center", color=LABEL_TEXT, fontsize=9)

ax.set_title(f"Fires per year in {NEIGHBOURHOOD}, {START_YEAR}–{END_YEAR}", loc="left", color=TITLE_TEXT)
ax.set_xticks(list(years))
ax.tick_params(axis="x", rotation=45)  # angled so long year ranges don't overlap
ax.set_ylim(0, fires_per_year.max() * 1.15)  # start at 0, leave room for the labels

# Light horizontal grid, no box around the chart
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.tick_params(colors=LABEL_TEXT, length=0)
for side in ["top", "right", "left"]:
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(AXIS)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

Path("plots").mkdir(exist_ok=True)
output_path = f"plots/fires_{NEIGHBOURHOOD}_{START_YEAR}-{END_YEAR}.png"
fig.savefig(output_path, dpi=150, bbox_inches="tight")

print(fires_per_year.to_string())
print(f"Saved {output_path}")

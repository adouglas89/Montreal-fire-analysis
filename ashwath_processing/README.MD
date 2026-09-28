# Fires per year by neighbourhood

These scripts merge the SIM intervention files (2005–2026) into one dataset, keep only fires, and plot the number of fires per year in a chosen neighbourhood.

Requires Python with `pandas` and `matplotlib`. Run all commands from this folder.

## Step 1: Download the data

Download all the SIM intervention CSV files (2005–2026) and save them in a `data/` folder.

## Step 2: Merge the files

```bash
python merge.py data/
```

This combines every CSV in `data/` and saves the result to `processed_data/merged.csv`. Along the way it:

- **Makes dates consistent.** The files use different date formats; all dates are converted to the same format (day only, no time).
- **Makes names consistent.** The 2005–2014 file uses older group names (e.g. "Incendies de bâtiments"), which are renamed to the codes used from 2015 on (e.g. "INCENDIE"). Neighbourhood names also changed over time; for now only Verdun is fixed ("Verdun / Ïle-des-Soeurs" → "Verdun"), but other neighbourhoods can be added to `OLD_NEIGHBOURHOOD_NAMES` the same way.
- **Removes duplicates.** The files overlap for 2020–2022.

## Step 3: Keep only fires

```bash
python filter_data.py
```

This keeps all building fires (`INCENDIE`) and, from other fires (`AUTREFEU`), only chimney fires. The result is saved to `processed_data/filtered.csv`, and a count per incident type is printed.

To change which incidents are kept, edit `GROUPS` and `DESCRIPTIONS` at the top of the script.

## Step 4: Plot fires per year

```bash
python analysis.py
```

This plots the number of fires per year for one neighbourhood and saves it to `plots/fires_<neighbourhood>_<start>-<end>.png`.

To choose the neighbourhood and years, edit these settings at the top of the script:

- `NEIGHBOURHOOD`: must match a name exactly, accents included (the full list is in the script)
- `START_YEAR` and `END_YEAR`: both years are included

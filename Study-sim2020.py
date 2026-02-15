#!/usr/bin/env python3
"""
Building fires over time and by arrondissement (Strictly speaking, we probably would like 
to normalize these by either population of the arronsissments or by their areas to allow more apples-to-apples comparisons).

Input:
- filtered_interventions.csv (ie. the result of running Filter-sim2020.py. But any other SIM CSV with similar columns
should also work fine.)

Comparison focus:
- Raw-count comparisons between multiple arrondissements:
  1) Monthly counts, selected arrondissements on the same plot
  2) Heatmap: arrondissement × month (counts)
  3) Seasonality: average count by month-of-year (counts), selected arrondissements
  4) Ranking bar charts: total counts by arrondissement and avg per month

Arrondissement selection:
- Set ARRONDS_TO_COMPARE to specific NOM_ARROND strings, OR
- Leave it empty to auto-pick top TOP_N_ARRONDS by total fires. 
By default, I've set N = 20 to include all the arrondissements. Verdun normally hangs out at around 16-17, depending
on the inclusion parameters. So if you want to see Verdun show up via this approach, N needs to be fairly large.

Inclusion criteria: Since we're interested in studying building/apartment fires in particular and the SIM data 
doesn't explicitly give this to us, there's some question about what incidents to include or not. To facilitate exploration
of this, I've set things up so that there are two sets of inclusion which I've called `STRICT_ALLOW' and `BROAD_ALLOW'.
They each filter events based on the INCIDENT_TYPE_DESC column of the corresponding entry, and the same analysis is 
performed for both inclusion criteria. So you can run the analysis with different inclusion criteria in parallel to see
what difference they make. Right now, I haven't included the 
various alarm levels: Feu / 2e Alerte, Feu / 3e Alerte, Feu / 4e Alerte, Feu / 5e Alerte
though arguably these should be included as well.  

Outputs saved to ./plots_building_fires_raw/
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------
# Configuration
# ---------------------------

DEFAULT_INPUT_CSV = "filtered_interventions.csv"
OUT_DIR = Path("plots_building_fires_raw")

TOP_N_ARRONDS = 20  # used if ARRONDS_TO_COMPARE is empty

# Optional: choose specific arrondissements to compare (exact NOM_ARROND strings).
# Leave empty to auto-select top TOP_N_ARRONDS.
ARRONDS_TO_COMPARE: List[str] = []

# Strict definition: structural/building fires only
STRICT_ALLOW = {"Feu de bâtiment"}

# Broad definition: building-related fire incidents (edit as needed)
BROAD_ALLOW = {
    "Feu de bâtiment",
    "Feu de cuisson",
    "Feu de cuisinière",
    "Feu de cheminée *",
    "Feu de nature électrique",
    "Aliments surchauffés",
}


# ---------------------------
# Helpers
# ---------------------------

def ensure_out_dir() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def pick_timestamp_column(df: pd.DataFrame) -> str:
    if "CREATION_DATE_TIME_PARSED" in df.columns:
        return "CREATION_DATE_TIME_PARSED"
    if "CREATION_DATE_TIME" in df.columns:
        return "CREATION_DATE_TIME"
    raise KeyError("Missing timestamp column. Expected CREATION_DATE_TIME_PARSED or CREATION_DATE_TIME.")


def parse_timestamp(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_datetime(df[col], errors="coerce")


def safe_series(df: pd.DataFrame, col: str, default: str = "") -> pd.Series:
    if col not in df.columns:
        return pd.Series([default] * len(df), index=df.index)
    return df[col].fillna(default).astype(str)


def month_index(ts: pd.Series) -> pd.PeriodIndex:
    return ts.dt.to_period("M")


def savefig(filename: str) -> None:
    plt.tight_layout()
    plt.savefig(OUT_DIR / filename, dpi=200)
    plt.close()


def classify_building_fires(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    itype = safe_series(df, "INCIDENT_TYPE_DESC")
    df["building_fire_strict"] = itype.isin(STRICT_ALLOW)
    df["building_fire_broad"] = itype.isin(BROAD_ALLOW)
    return df


def select_arronds(df_fire: pd.DataFrame) -> List[str]:
    if "NOM_ARROND" not in df_fire.columns or df_fire.empty:
        return []
    arr = df_fire["NOM_ARROND"].fillna("(missing)").astype(str)

    if ARRONDS_TO_COMPARE:
        return [a for a in ARRONDS_TO_COMPARE if (arr == a).any()]

    return arr.value_counts().head(TOP_N_ARRONDS).index.tolist()


def build_monthly_pivot(df_fire: pd.DataFrame, arronds: List[str]) -> pd.DataFrame:
    """
    index = month (PeriodIndex), columns = arrondissement, values = raw monthly counts
    """
    if df_fire.empty or "NOM_ARROND" not in df_fire.columns or not arronds:
        return pd.DataFrame()

    df = df_fire.copy()
    df["NOM_ARROND"] = df["NOM_ARROND"].fillna("(missing)").astype(str)
    df = df[df["NOM_ARROND"].isin(arronds)]
    if df.empty:
        return pd.DataFrame()

    pivot = pd.crosstab(month_index(df["ts"]), df["NOM_ARROND"]).sort_index()

    # Ensure all arronds present as columns (even if 0 in some months)
    for a in arronds:
        if a not in pivot.columns:
            pivot[a] = 0
    return pivot[arronds]


# ---------------------------
# Plots (raw counts)
# ---------------------------

def plot_overall_monthly(df_fire: pd.DataFrame, label: str, filename: str) -> None:
    monthly = month_index(df_fire["ts"]).value_counts().sort_index()
    if monthly.empty:
        return
    x = monthly.index.to_timestamp()

    plt.figure(figsize=(12, 5))
    plt.plot(x, monthly.values, linewidth=2)
    plt.title(f"{label}: Total Count per Month (Overall)")
    plt.xlabel("Month")
    plt.ylabel("Count")
    savefig(filename)


def plot_compare_monthly_lines(pivot: pd.DataFrame, label: str, filename: str) -> None:
    if pivot.empty:
        return
    x = pivot.index.to_timestamp()

    plt.figure(figsize=(13, 6))
    for col in pivot.columns:
        plt.plot(x, pivot[col].values, linewidth=1.8)
    plt.title(f"{label}: Monthly Counts by Arrondissement (Raw)")
    plt.xlabel("Month")
    plt.ylabel("Count")
    plt.legend(pivot.columns, fontsize=8, ncol=2)
    savefig(filename)


def plot_heatmap_arrond_by_month(pivot: pd.DataFrame, label: str, filename: str) -> None:
    if pivot.empty:
        return

    months = pivot.index.astype(str).tolist()
    step = 2 if len(months) <= 36 else 3
    xticks = np.arange(0, len(months), step)

    plt.figure(figsize=(14, 6))
    plt.imshow(pivot.T.values, aspect="auto")
    plt.title(f"{label}: Heatmap (Arrondissement × Month) (Raw counts)")
    plt.xlabel("Month")
    plt.ylabel("Arrondissement")
    plt.xticks(xticks, [months[i] for i in xticks], rotation=45, ha="right")
    plt.yticks(np.arange(len(pivot.columns)), pivot.columns.tolist())
    plt.colorbar(label="Count")
    savefig(filename)


def plot_seasonality_month_of_year(df_fire: pd.DataFrame, arronds: List[str], label: str, filename: str) -> None:
    """
    Raw-count seasonality: average # of fires in each calendar month (Jan..Dec),
    averaged across years in the dataset, for selected arrondissements.
    """
    if df_fire.empty or "NOM_ARROND" not in df_fire.columns or not arronds:
        return

    df = df_fire.copy()
    df["NOM_ARROND"] = df["NOM_ARROND"].fillna("(missing)").astype(str)
    df = df[df["NOM_ARROND"].isin(arronds)]
    if df.empty:
        return

    # Explicit columns avoid ts reset_index collision
    df["year"] = df["ts"].dt.year
    df["month"] = df["ts"].dt.month

    counts = (
        df.groupby(["NOM_ARROND", "year", "month"])
          .size()
          .reset_index(name="count")
    )

    seasonal = (
        counts.groupby(["NOM_ARROND", "month"])["count"]
              .mean()
              .unstack(fill_value=0)
              .reindex(columns=range(1, 13), fill_value=0)
              .reindex(index=arronds)
    )

    plt.figure(figsize=(13, 6))
    for arr in seasonal.index:
        plt.plot(range(1, 13), seasonal.loc[arr].values, linewidth=1.8)
    plt.title(f"{label}: Seasonality (Avg raw monthly count by month-of-year)")
    plt.xlabel("Month of year")
    plt.ylabel("Average count (raw)")
    plt.xticks(range(1, 13))
    plt.legend(seasonal.index, fontsize=8, ncol=2)
    savefig(filename)


def plot_rank_total_by_arrond(df_fire: pd.DataFrame, label: str, filename: str, topk: int = 20) -> None:
    if df_fire.empty or "NOM_ARROND" not in df_fire.columns:
        return

    arr = df_fire["NOM_ARROND"].fillna("(missing)").astype(str)
    totals = arr.value_counts().head(topk)

    plt.figure(figsize=(12, 7))
    plt.barh(totals.index[::-1], totals.values[::-1])
    plt.title(f"{label}: Total Count by Arrondissement (Top {topk})")
    plt.xlabel("Total count (raw)")
    plt.ylabel("Arrondissement")
    savefig(filename)


def run_bundle(df_fire: pd.DataFrame, label: str, prefix: str) -> None:
    if df_fire.empty:
        print(f"{label}: no matching rows; skipping.")
        return

    arronds = select_arronds(df_fire)
    if not arronds:
        print(f"{label}: no arrondissement information available; skipping arrondissement comparisons.")
        return

    pivot = build_monthly_pivot(df_fire, arronds)

    plot_overall_monthly(df_fire, label, f"{prefix}_01_overall_monthly.png")
    plot_rank_total_by_arrond(df_fire, label, f"{prefix}_02_rank_total_by_arrond.png")
    plot_compare_monthly_lines(pivot, label, f"{prefix}_03_compare_monthly_lines_raw.png")
    plot_heatmap_arrond_by_month(pivot, label, f"{prefix}_04_heatmap_arrond_by_month_raw.png")
    plot_seasonality_month_of_year(df_fire, arronds, label, f"{prefix}_05_seasonality_month_of_year_raw.png")

    print(f"{label}: comparing arrondissements: {arronds}")


# ---------------------------
# Main
# ---------------------------

def main(argv: List[str]) -> int:
    ensure_out_dir()

    input_path = Path(argv[1]) if len(argv) >= 2 else Path(DEFAULT_INPUT_CSV)
    if not input_path.exists():
        print(f"ERROR: Input CSV not found: {input_path}")
        return 2

    df = pd.read_csv(input_path)

    ts_col = pick_timestamp_column(df)
    df = df.copy()
    df["ts"] = parse_timestamp(df, ts_col)
    df = df[df["ts"].notna()].copy()

    if df.empty:
        print("No rows with a parseable timestamp. Nothing to plot.")
        return 0

    df = classify_building_fires(df)

    strict_n = int(df["building_fire_strict"].sum())
    broad_n = int(df["building_fire_broad"].sum())

    print(f"Rows in input (timestamp parsed): {len(df):,}")
    print(f"STRICT building fires (Feu de bâtiment): {strict_n:,}")
    print(f"BROAD building-related fires: {broad_n:,}")

    if "INCIDENT_TYPE_DESC" in df.columns:
        if strict_n:
            print("\nTop INCIDENT_TYPE_DESC among STRICT matches:")
            print(safe_series(df[df["building_fire_strict"]], "INCIDENT_TYPE_DESC").value_counts().head(15).to_string())
        if broad_n:
            print("\nTop INCIDENT_TYPE_DESC among BROAD matches:")
            print(safe_series(df[df["building_fire_broad"]], "INCIDENT_TYPE_DESC").value_counts().head(15).to_string())

    df_strict = df[df["building_fire_strict"]].copy()
    df_broad = df[df["building_fire_broad"]].copy()

    run_bundle(df_strict, "STRICT (Feu de bâtiment)", "strict")
    run_bundle(df_broad, "BROAD (building-related)", "broad")

    print(f"\nDone. Plots saved to: {OUT_DIR.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
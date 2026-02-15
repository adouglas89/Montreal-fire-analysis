#!/usr/bin/env python3
"""
Filter SIM intervention records by date range (inclusive) and optional categorical filters.

Inputs (from the user):
- DateRange: [StartDate, EndDate] as date-only strings "YYYY-MM-DD"
- IncidentTypes: list of INCIDENT_TYPE_DESC values (optional; can be empty)
- GroupDescriptions: list of DESCRIPTION_GROUPE values (optional; can be empty)
- Arronds: list of NOM_ARROND values (optional; can be empty)

Behavior:
- Reads "donneesouvertes-interventions-sim2020.csv" into a DataFrame
- Parses CREATION_DATE_TIME robustly (supports full timestamps and date-only strings)
- Filters rows where CREATION_DATE_TIME date is within [StartDate, EndDate]
- Applies optional filters only when the corresponding list is non-empty
- Produces a filtered DataFrame and prints a short summary
"""

from __future__ import annotations

import sys
from datetime import datetime, date
from typing import List, Tuple

import pandas as pd


CSV_PATH = "donneesouvertes-interventions-sim2020.csv"


def parse_date_yyyy_mm_dd(s: str) -> date:
    """Parse a date-only string formatted as YYYY-MM-DD into a datetime.date."""
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Invalid date '{s}'. Expected format YYYY-MM-DD.") from e


def get_user_list(prompt: str) -> List[str]:
    """
    Read a comma-separated list from stdin.
    Returns a list of trimmed, non-empty strings.
    Empty input => empty list.
    """
    raw = input(prompt).strip()
    if not raw:
        return []
    # Split on commas, trim whitespace, drop empties
    return [item.strip() for item in raw.split(",") if item.strip()]


def get_user_inputs() -> Tuple[Tuple[date, date], List[str], List[str], List[str]]:
    """
    Collect user inputs:
      - DateRange: two date strings
      - IncidentTypes, GroupDescriptions, Arronds: optional comma-separated lists
    """
    print("Enter DateRange (two dates, YYYY-MM-DD).")
    start_str = input("  StartDate (YYYY-MM-DD): ").strip()
    end_str = input("  EndDate   (YYYY-MM-DD): ").strip()

    start_date = parse_date_yyyy_mm_dd(start_str)
    end_date = parse_date_yyyy_mm_dd(end_str)

    # Ensure StartDate <= EndDate
    if start_date > end_date:
        raise ValueError(f"StartDate {start_date} is after EndDate {end_date}.")

    print("\nOptional filters (comma-separated). Press Enter for an empty list.")
    incident_types = get_user_list("  IncidentTypes (INCIDENT_TYPE_DESC): ")
    group_descs = get_user_list("  GroupDescriptions (DESCRIPTION_GROUPE): ")
    arronds = get_user_list("  Arronds (NOM_ARROND): ")

    return (start_date, end_date), incident_types, group_descs, arronds


def load_data(csv_path: str) -> pd.DataFrame:
    """
    Read the CSV into a DataFrame.
    Keep columns as-is; parse dates in a later, controlled step.
    """
    return pd.read_csv(csv_path)


def parse_creation_datetime(df: pd.DataFrame) -> pd.Series:
    """
    Parse CREATION_DATE_TIME as datetimes.
    """
    return pd.to_datetime(df["CREATION_DATE_TIME"], errors="coerce")


def filter_dataframe(
    df: pd.DataFrame,
    start_date: date,
    end_date: date,
    incident_types: List[str],
    group_descs: List[str],
    arronds: List[str],
) -> pd.DataFrame:
    """
    Apply the combined filter:
    - CREATION_DATE_TIME date between start_date and end_date (inclusive)
    - AND (optional) INCIDENT_TYPE_DESC in incident_types if incident_types not empty
    - AND (optional) DESCRIPTION_GROUPE in group_descs if group_descs not empty
    - AND (optional) NOM_ARROND in arronds if arronds not empty
    """
    # 1) Parse CREATION_DATE_TIME to datetime; coerce unparseable values to NaT
    creation_dt = parse_creation_datetime(df)

    # 2) Convert to date (drops time-of-day). NaT becomes NaN, so we guard with notna().
    creation_date = creation_dt.dt.date

    # 3) Base mask: date within inclusive range + CREATION_DATE_TIME successfully parsed
    mask = creation_dt.notna() & (creation_date >= start_date) & (creation_date <= end_date)

    # 4) Optional filters: only apply if user provided a non-empty list
    if incident_types:
        mask &= df["INCIDENT_TYPE_DESC"].isin(incident_types)

    if group_descs:
        mask &= df["DESCRIPTION_GROUPE"].isin(group_descs)

    if arronds:
        mask &= df["NOM_ARROND"].isin(arronds)

    # 5) Return filtered DataFrame (copy to avoid chained-assignment issues later)
    out = df.loc[mask].copy()

    # Optionally keep a parsed datetime column for downstream work
    out["CREATION_DATE_TIME_PARSED"] = creation_dt.loc[mask].values

    return out


def main() -> int:
    try:
        (start_date, end_date), incident_types, group_descs, arronds = get_user_inputs()

        # Read the CSV
        df = load_data(CSV_PATH)

        # Filter according to the user's criteria
        filtered = filter_dataframe(
            df=df,
            start_date=start_date,
            end_date=end_date,
            incident_types=incident_types,
            group_descs=group_descs,
            arronds=arronds,
        )

        # Report
        print("\n--- Results ---")
        print(f"Input file: {CSV_PATH}")
        print(f"DateRange (inclusive): {start_date} to {end_date}")
        print(f"IncidentTypes filter: {incident_types if incident_types else '(none)'}")
        print(f"GroupDescriptions filter: {group_descs if group_descs else '(none)'}")
        print(f"Arronds filter: {arronds if arronds else '(none)'}")
        print(f"Matched rows: {len(filtered):,} / {len(df):,}")

        # Show a small preview
        if len(filtered) > 0:
            print("\nPreview (first 10 rows):")
            cols_to_show = [
                "INCIDENT_NBR",
                "CREATION_DATE_TIME",
                "CREATION_DATE_TIME_PARSED",
                "INCIDENT_TYPE_DESC",
                "DESCRIPTION_GROUPE",
                "NOM_ARROND",
                "NOM_VILLE",
                "CASERNE",
                "DIVISION",
                "NOMBRE_UNITES",
            ]
            # Only display columns that actually exist (defensive)
            cols_to_show = [c for c in cols_to_show if c in filtered.columns]
            print(filtered[cols_to_show].head(10).to_string(index=False))

        # Save the output in the file "filtered_interventions.csv":
        filtered.to_csv("filtered_interventions.csv", index=False)

        return 0

    except FileNotFoundError:
        print(f"ERROR: Could not find '{CSV_PATH}'. Place the CSV in the same directory as this script.")
        return 2
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

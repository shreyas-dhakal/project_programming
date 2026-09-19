"""
Scrape the CASTLES Gravitational Lens Database main table into a clean CSV.

Source: https://lweb.cfa.harvard.edu/castles/
Citation (please keep, per the site's request):
  C.S. Kochanek, E.E. Falco, C. Impey, J. Lehar, B. McLeod, H.-W. Rix

Usage:
    python scrape_castles.py
    -> writes castles_multiply_imaged.csv and castles_binary_quasars.csv
"""

import os
import re
import pandas as pd
import requests

URL = "https://lweb.cfa.harvard.edu/castles/"

# --- Step 0: always save next to this script, regardless of the working ---------
# directory the script happens to be launched from (fixes "the CSV isn't saving"
# issues caused by relative paths + an unexpected current working directory).
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(PROJECT_DIR, exist_ok=True)
print(f"Project directory: {PROJECT_DIR}")

# --- Step 1: fetch the raw HTML -------------------------------------------------
resp = requests.get(URL, timeout=30)
resp.raise_for_status()
html = resp.text

# --- Step 2: let pandas parse every <table> on the page -------------------------
# pandas.read_html uses lxml/bs4 under the hood and returns a list of DataFrames,
# one per HTML table it finds on the page.
tables = pd.read_html(html)

print(f"Found {len(tables)} tables on the page.")
for i, t in enumerate(tables):
    print(i, t.shape, list(t.columns)[:6])

# On the live CASTLES page, the two tables you want are:
#   - "Summary of Multiply Imaged Systems"  (the big ~101-row table)
#   - "Summary of Binary Quasars"           (the ~17-row table)
# Their index among `tables` can shift if the page layout changes, so we
# identify them by expected column names / row counts rather than hardcoding
# an index blindly.


def find_table(tables, must_have_cols, min_rows=20):
    for t in tables:
        cols = [str(c).strip().lower() for c in t.columns]
        if (
            all(any(mc in c for c in cols) for mc in must_have_cols)
            and len(t) >= min_rows
        ):
            return t
    return None


multiply_imaged = find_table(tables, must_have_cols=["lens name", "zs", "zl"])
binary_quasars = find_table(tables, must_have_cols=["binary name", "zs"], min_rows=5)


# --- Step 3: clean up -------------------------------------------------------------
def clean_numeric(series):
    """Strip footnote markers / uncertainty flags like '(0.69)' or '3.60' -> float."""

    def parse(x):
        if pd.isna(x):
            return None
        x = str(x)
        x = x.replace("?", "").strip()
        # lens redshift sometimes given as "(0.69)" meaning photometric estimate
        is_photometric = x.startswith("(") and x.endswith(")")
        x = x.strip("()")
        try:
            return float(x), is_photometric
        except ValueError:
            return None, is_photometric

    parsed = series.apply(parse)
    values = parsed.apply(lambda p: p[0] if p else None)
    flags = parsed.apply(lambda p: p[1] if p else False)
    return values, flags


if multiply_imaged is not None:
    df = multiply_imaged.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # numeric redshifts + photometric-estimate flag for lens redshift
    df["zs_clean"], _ = clean_numeric(df["zs"])
    df["zl_clean"], df["zl_photometric"] = clean_numeric(df["zl"])

    # magnitudes like "I=20.05" or "I=16.53/2" -> band, value, n_images_used
    def split_mag(x):
        if pd.isna(x):
            return None, None, None
        m = re.match(r"([A-Za-z]*)=?([\d.\-]+)(?:/(\d+))?", str(x))
        if not m:
            return None, None, None
        band, val, n = m.groups()
        return band or None, float(val) if val else None, int(n) if n else None

    if "ms (mag)" in df.columns:
        df[["ms_band", "ms_mag", "ms_nimg"]] = df["ms (mag)"].apply(
            lambda x: pd.Series(split_mag(x))
        )
    if "ml (mag)" in df.columns:
        df[["ml_band", "ml_mag", "ml_nimg"]] = df["ml (mag)"].apply(
            lambda x: pd.Series(split_mag(x))
        )

    # radio flux "F5=1209" -> frequency GHz, flux mJy
    if "FGHz (mJy)" in df.columns:

        def split_flux(x):
            if pd.isna(x):
                return None, None
            m = re.match(r"F([\d.]+)[=~<]([\d.]+)", str(x))
            if not m:
                return None, None
            return float(m.group(1)), float(m.group(2))

        df[["radio_freq_ghz", "radio_flux_mjy"]] = df["FGHz (mJy)"].apply(
            lambda x: pd.Series(split_flux(x))
        )

    # number of images: strip E/R/? flags -> integer, keep flags separately
    if "Nim" in df.columns:
        df["n_images"] = df["Nim"].astype(str).str.extract(r"(\d+)").astype(float)
        df["has_ring"] = df["Nim"].astype(str).str.contains("R")
        df["is_extended"] = df["Nim"].astype(str).str.contains("E")

    for col in ['size (")', "dt (days)", "sigma (km/s)", "E(B-V)"]:
        if col in df.columns:
            df[col + "_clean"] = pd.to_numeric(
                df[col].astype(str).str.replace(r"±.*", "", regex=True), errors="coerce"
            )

    out_path = os.path.join(PROJECT_DIR, "castles_multiply_imaged.csv")
    df.to_csv(out_path, index=False)
    print(f"Wrote {out_path}  (shape: {df.shape})")
else:
    print(
        "WARNING: could not locate the multiply-imaged table on the page — "
        "check the printed table list above and adjust `find_table` if the "
        "page layout changed."
    )

if binary_quasars is not None:
    out_path = os.path.join(PROJECT_DIR, "castles_binary_quasars.csv")
    binary_quasars.to_csv(out_path, index=False)
    print(f"Wrote {out_path}  (shape: {binary_quasars.shape})")
else:
    print("WARNING: could not locate the binary quasars table on the page.")

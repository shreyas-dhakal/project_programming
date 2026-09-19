from astropy.io import fits
from astropy.table import Table
import numpy as np

FILE = "ceers_cat_v1.0.fits"

# ============================================================
# 1. FITS FILE STRUCTURE
# ============================================================

print("=" * 80)
print("FITS FILE STRUCTURE")
print("=" * 80)

with fits.open(FILE) as hdul:
    hdul.info()

    print("\nNumber of HDUs:", len(hdul))

    for i, hdu in enumerate(hdul):
        print(f"\nHDU {i}")
        print(f"Name: {hdu.name}")
        print(f"Type: {type(hdu).__name__}")

        if hdu.data is not None:
            print(f"Shape: {getattr(hdu.data, 'shape', 'N/A')}")

        if hasattr(hdu, "columns") and hdu.columns is not None:
            print(f"Number of columns: {len(hdu.columns)}")


# ============================================================
# 2. INSPECT EVERY TABLE HDU
# ============================================================

with fits.open(FILE) as hdul:
    for hdu_index, hdu in enumerate(hdul):
        if not isinstance(hdu, (fits.BinTableHDU, fits.TableHDU)):
            continue

        print("\n\n")
        print("=" * 100)
        print(f"TABLE HDU {hdu_index}: {hdu.name}")
        print("=" * 100)

        data = hdu.data

        print(f"Rows: {len(data):,}")
        print(f"Columns: {len(hdu.columns)}")

        # ----------------------------------------------------
        # Column names
        # ----------------------------------------------------

        print("\nCOLUMN NAMES")
        print("-" * 100)

        for i, name in enumerate(hdu.columns.names):
            print(f"{i:3d}: {name}")

        # ----------------------------------------------------
        # Detailed column information
        # ----------------------------------------------------

        print("\n\nCOLUMN DETAILS")
        print("-" * 100)

        for i, col in enumerate(hdu.columns):
            print(
                f"{i:3d} | "
                f"{col.name:30s} | "
                f"format={str(col.format):10s} | "
                f"unit={str(col.unit)}"
            )

        # ----------------------------------------------------
        # Look specifically for useful redshift / coordinate
        # columns
        # ----------------------------------------------------

        keywords = [
            "z",
            "redshift",
            "spec",
            "phot",
            "lephare",
            "ra",
            "dec",
            "id",
            "flux",
            "f435",
            "f606",
            "f814",
            "f115",
            "f150",
            "f200",
            "f277",
            "f356",
            "f410",
            "f444",
        ]

        print("\n\nPOTENTIALLY RELEVANT COLUMNS")
        print("-" * 100)

        for name in hdu.columns.names:
            lower = name.lower()

            if any(keyword in lower for keyword in keywords):
                print(name)

        # ----------------------------------------------------
        # Numerical summaries
        # ----------------------------------------------------

        print("\n\nNUMERICAL COLUMN SUMMARY")
        print("-" * 100)

        for name in hdu.columns.names:
            arr = data[name]

            # Only scalar numerical columns
            if np.issubdtype(arr.dtype, np.number) and arr.ndim == 1:
                try:
                    finite = arr[np.isfinite(arr)]

                    if len(finite) == 0:
                        continue

                    print(
                        f"{name:30s} "
                        f"N={len(arr):8d} "
                        f"finite={len(finite):8d} "
                        f"min={np.min(finite):12.5g} "
                        f"median={np.median(finite):12.5g} "
                        f"mean={np.mean(finite):12.5g} "
                        f"max={np.max(finite):12.5g}"
                    )

                except Exception:
                    pass

        # ----------------------------------------------------
        # First 5 rows
        # ----------------------------------------------------

        print("\n\nFIRST 5 ROWS")
        print("-" * 100)

        table = Table(data)

        table.pprint(max_lines=10, max_width=200, show_unit=True)

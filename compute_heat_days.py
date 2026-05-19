#!/usr/bin/env python3
"""
compute_heat_days.py

Counts days > 95°F (35°C) per month from NCEP/NCAR Reanalysis 1 daily 2m max
temperature (tmax.2m.gauss.YYYY.nc), then writes:
  data/heat_days_clim_1991-2020.nc  — 1991-2020 mean counts per month
  data/heat_days_2016.nc            — 2016 counts per month

Run once after grab_data.sh and before plot_anomalies.py.
"""

import xarray as xr
from pathlib import Path

DATA_DIR    = Path("data")
CLIM_YEARS  = range(1991, 2021)
YEAR        = 2016
THRESHOLD_C = 35.0   # °C = 95°F
SURF_MONTHS = [5, 6, 7, 8]  # May–August


def count_hot_days(year, month):
    path = DATA_DIR / f"tmax.2m.gauss.{year}.nc"
    with xr.open_dataset(path) as ds:
        da = ds["tmax"].squeeze()
        units = da.attrs.get("units", "K")
        threshold = THRESHOLD_C if "C" in units else THRESHOLD_C + 273.15
        monthly = da.sel(time=da.time.dt.month == month)
        return (monthly > threshold).sum(dim="time").load()


# ── Climatology (1991–2020) ────────────────────────────────────────────────────
print("Computing 1991–2020 climatology...")
clim_slabs = []
for year in CLIM_YEARS:
    month_counts = [
        count_hot_days(year, m).assign_coords(month=m).expand_dims("month")
        for m in SURF_MONTHS
    ]
    clim_slabs.append(xr.concat(month_counts, dim="month"))
    print(f"  {year}")

clim_mean = xr.concat(clim_slabs, dim="year").mean(dim="year")
clim_mean.name = "heat_days"
clim_mean.attrs.update({
    "long_name":    "Mean days > 35°C (95°F)",
    "units":        "days/month",
    "climatology":  "1991-2020",
    "threshold_C":  THRESHOLD_C,
})

out_clim = DATA_DIR / "heat_days_clim_1991-2020.nc"
clim_mean.to_netcdf(out_clim)
print(f"Saved: {out_clim}")

# ── 2016 ───────────────────────────────────────────────────────────────────────
print(f"\nComputing {YEAR}...")
month_counts = [
    count_hot_days(YEAR, m).assign_coords(month=m).expand_dims("month")
    for m in SURF_MONTHS
]
ds_2016 = xr.concat(month_counts, dim="month")
ds_2016.name = "heat_days"
ds_2016.attrs.update({
    "long_name":   f"Days > 35°C (95°F) in {YEAR}",
    "units":       "days/month",
    "threshold_C": THRESHOLD_C,
})

out_2016 = DATA_DIR / f"heat_days_{YEAR}.nc"
ds_2016.to_netcdf(out_2016)
print(f"Saved: {out_2016}")
print("\nDone. Run plot_anomalies.py to generate maps.")

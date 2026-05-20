#!/usr/bin/env python3
"""
compute_heat_days.py

Computes three derived monthly fields from NCEP/NCAR Reanalysis 1 daily 2m
temperature (tmax/tmin.2m.gauss.YYYY.nc):

    Heat days — days per month where Tmax > 95°F (35°C)
    SDD       — Stress Degree Days (corn): sum of max(Tmax°F − 86, 0) per month
    MGDD      — Modified Growing Degree Days (corn):
                  cap Tmax at 86°F, floor Tmin at 50°F,
                  then sum of max((Tmax_adj + Tmin_adj)/2 − 50, 0) per month

Writes NetCDF files to data/:
    heat_days_clim_1991-2020.nc / heat_days_2016.nc
    sdd_clim_1991-2020.nc       / sdd_2016.nc
    mgdd_clim_1991-2020.nc      / mgdd_2016.nc

Run once after grab_data.sh and before plot_anomalies.py.
"""

import xarray as xr
from pathlib import Path

DATA_DIR    = Path("data")
CLIM_YEARS  = range(1991, 2021)
YEAR        = 2016
SURF_MONTHS = [5, 6, 7, 8]  # May–August
HD_THRESH_F      = 95.0  # °F
SDD_BASE_F       = 86.0  # °F — corn stress base (MRCC definition)
MGDD_BASE_F      = 50.0  # °F — corn development base
MGDD_TMAX_CAP_F  = 86.0  # °F — development ceases above this
MGDD_TMIN_FLOOR_F = 50.0  # °F — development ceases below this


def to_f(da, units):
    if "K" in units:
        return (da - 273.15) * 9 / 5 + 32
    if "C" in units:
        return da * 9 / 5 + 32
    return da


def compute_metrics(year, month):
    """Return (heat_days, sdd, mgdd) DataArrays for the given year and month."""
    path_tmax = DATA_DIR / f"tmax.2m.gauss.{year}.nc"
    with xr.open_dataset(path_tmax) as ds:
        da_max = ds["tmax"].squeeze().sel(time=ds["tmax"].squeeze().time.dt.month == month)
        units  = da_max.attrs.get("units", "K")
        da_max = da_max.load()

    path_tmin = DATA_DIR / f"tmin.2m.gauss.{year}.nc" 
    with xr.open_dataset(path_tmin) as ds:
        da_min = ds["tmin"].squeeze().sel(time=ds["tmin"].squeeze().time.dt.month == month)
        da_min = da_min.load()

    da_max = to_f(da_max, units)
    da_min = to_f(da_min, units)

    heat_days = (da_max > HD_THRESH_F).sum(dim="time")
    sdd       = (da_max - SDD_BASE_F).clip(min=0).sum(dim="time")

    tmean_adj = (da_max.clip(max=MGDD_TMAX_CAP_F) + da_min.clip(min=MGDD_TMIN_FLOOR_F)) / 2
    mgdd      = (tmean_adj - MGDD_BASE_F).clip(min=0).sum(dim="time")

    return heat_days, sdd, mgdd


# ── Climatology (1991–2020) ────────────────────────────────────────────────────
print("Computing 1991–2020 climatology...")

hd_clim_slabs   = []
sdd_clim_slabs  = []
mgdd_clim_slabs = []

for year in CLIM_YEARS:

    hd_months   = []
    sdd_months  = []
    mgdd_months = []

    for m in SURF_MONTHS:

        hd, sdd, mgdd = compute_metrics(year, m)
        hd_months.append(hd.assign_coords(month=m).expand_dims("month"))
        sdd_months.append(sdd.assign_coords(month=m).expand_dims("month"))
        mgdd_months.append(mgdd.assign_coords(month=m).expand_dims("month"))

    hd_clim_slabs.append(xr.concat(hd_months, dim="month"))
    sdd_clim_slabs.append(xr.concat(sdd_months, dim="month"))
    mgdd_clim_slabs.append(xr.concat(mgdd_months, dim="month"))

    print(f"  {year}")

hd_clim_mean = xr.concat(hd_clim_slabs, dim="year").mean(dim="year")
hd_clim_mean.name = "heat_days"
hd_clim_mean.attrs.update({
    "long_name":   "Mean days > 35°C (95°F)",
    "units":       "days/month",
    "climatology": "1991-2020",
})

out = DATA_DIR / "heat_days_clim_1991-2020.nc"
hd_clim_mean.to_netcdf(out)
print(f"Saved: {out}")

sdd_clim_mean = xr.concat(sdd_clim_slabs, dim="year").mean(dim="year")
sdd_clim_mean.name = "sdd"
sdd_clim_mean.attrs.update({
    "long_name":   "Mean Stress Degree Days (corn, base 86°F)",
    "units":       "°F·days/month",
    "climatology": "1991-2020",
})

out = DATA_DIR / "sdd_clim_1991-2020.nc"
sdd_clim_mean.to_netcdf(out)
print(f"Saved: {out}")

mgdd_clim_mean = xr.concat(mgdd_clim_slabs, dim="year").mean(dim="year")
mgdd_clim_mean.name = "mgdd"
mgdd_clim_mean.attrs.update({
    "long_name":   "Mean Modified Growing Degree Days (corn, base 50°F, cap 86°F)",
    "units":       "°F·days/month",
    "climatology": "1991-2020",
})

out = DATA_DIR / "mgdd_clim_1991-2020.nc"
mgdd_clim_mean.to_netcdf(out)
print(f"Saved: {out}")

# ── 2016 ───────────────────────────────────────────────────────────────────────
print(f"\nComputing {YEAR}...")

hd_months   = []
sdd_months  = []
mgdd_months = []

for m in SURF_MONTHS:

    hd, sdd, mgdd = compute_metrics(YEAR, m)
    hd_months.append(hd.assign_coords(month=m).expand_dims("month"))
    sdd_months.append(sdd.assign_coords(month=m).expand_dims("month"))
    mgdd_months.append(mgdd.assign_coords(month=m).expand_dims("month"))

hd_2016 = xr.concat(hd_months, dim="month")
hd_2016.name = "heat_days"
hd_2016.attrs.update({"long_name": f"Days > 35°C (95°F) in {YEAR}", "units": "days/month"})

out = DATA_DIR / f"heat_days_{YEAR}.nc"
hd_2016.to_netcdf(out)
print(f"Saved: {out}")

sdd_2016 = xr.concat(sdd_months, dim="month")
sdd_2016.name = "sdd"
sdd_2016.attrs.update({"long_name": f"Stress Degree Days (corn, base 86°F) in {YEAR}", "units": "°F·days/month"})

out = DATA_DIR / f"sdd_{YEAR}.nc"
sdd_2016.to_netcdf(out)
print(f"Saved: {out}")

mgdd_2016 = xr.concat(mgdd_months, dim="month")
mgdd_2016.name = "mgdd"
mgdd_2016.attrs.update({"long_name": f"Modified Growing Degree Days (corn, base 50°F, cap 86°F) in {YEAR}", "units": "°F·days/month"})

out = DATA_DIR / f"mgdd_{YEAR}.nc"
mgdd_2016.to_netcdf(out)
print(f"Saved: {out}")

print("\nDone. Run plot_anomalies.py to generate maps.")

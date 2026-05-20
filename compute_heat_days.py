#!/usr/bin/env python3
"""
compute_heat_days.py

Computes two derived monthly fields from NCEP/NCAR Reanalysis 1 daily 2m max
temperature (tmax.2m.gauss.YYYY.nc):

    Heat days — days per month where Tmax > 95°F (35°C)
    SDD       — Stress Degree Days (corn): sum of max(Tmax°F − 86, 0) per month
    
Writes NetCDF files to data/:
    heat_days_clim_1991-2020.nc / heat_days_2016.nc
    sdd_clim_1991-2020.nc       / sdd_2016.nc

Run once after grab_data.sh and before plot_anomalies.py.
"""

import xarray as xr
from pathlib import Path

DATA_DIR    = Path("data")
CLIM_YEARS  = range(1991, 2021)
YEAR        = 2016
SURF_MONTHS = [5, 6, 7, 8]  # May–August
HD_THRESH_F = 95.0  # °F - heat day threshold
SDD_BASE_F  = 86.0  # °F — corn stress base (MRCC definition)


def compute_metrics(year, month):
    """Return (heat_days, sdd) DataArrays for the given year and month."""
    path = DATA_DIR / f"tmax.2m.gauss.{year}.nc"
    with xr.open_dataset(path) as ds:
        da    = ds["tmax"].squeeze().sel(time=ds["tmax"].squeeze().time.dt.month == month)
        units = da.attrs.get("units", "K")
        da    = da.load()
        
    if "K" in units:
        da = (da - 273.15) * 9 / 5 + 32
    elif "C" in units:
        da = da * 9 / 5 + 32
        
    heat_days = (da > HD_THRESH_F).sum(dim="time")
    sdd       = (da - SDD_BASE_F).clip(min=0).sum(dim="time")
    
    return heat_days, sdd


# ── Climatology (1991–2020) ────────────────────────────────────────────────────
print("Computing 1991–2020 climatology...")

hd_clim_slabs  = []
sdd_clim_slabs = []

for year in CLIM_YEARS:
    
    hd_months  = []
    sdd_months = []
    
    for m in SURF_MONTHS:
        
        hd, sdd = compute_metrics(year, m)
        hd_months.append(hd.assign_coords(month=m).expand_dims("month"))
        sdd_months.append(sdd.assign_coords(month=m).expand_dims("month"))
        
    hd_clim_slabs.append(xr.concat(hd_months, dim="month"))
    sdd_clim_slabs.append(xr.concat(sdd_months, dim="month"))
    
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

# ── 2016 ───────────────────────────────────────────────────────────────────────
print(f"\nComputing {YEAR}...")
hd_months  = []
sdd_months = []
for m in SURF_MONTHS:
    
    hd, sdd = compute_metrics(YEAR, m)
    hd_months.append(hd.assign_coords(month=m).expand_dims("month"))
    sdd_months.append(sdd.assign_coords(month=m).expand_dims("month"))

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

print("\nDone. Run plot_anomalies.py to generate maps.")

#!/usr/bin/env python3
"""
plot_surface_anomalies.py

2m temperature and precipitation rate anomaly maps for June and July 2016.
Data: NCEP/NCAR Reanalysis 1 monthly means vs. 1991-2020 climatology.
Output: PNG images saved to public_html/images/
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.util as cutil
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from pathlib import Path

DATA_DIR = Path("data")
OUT_DIR  = Path("public_html/images")
OUT_DIR.mkdir(exist_ok=True)

YEAR          = 2016
MONTHS        = {6: "June", 7: "July"}
DAYS_IN_MONTH = {6: 30, 7: 31}
CLIM_STR      = "Climatology: 1991–2020  |  NCEP/NCAR Reanalysis 1"

# State/province lines (shared across NA maps)
states = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none"
)


def prep_data(da):
    """Shift lons from 0-360 to -180-180 and add cyclic point."""
    new_lon = np.where(da.lon.values > 180, da.lon.values - 360, da.lon.values)
    da      = da.assign_coords(lon=new_lon).sortby("lon")
    data_c, lons_c = cutil.add_cyclic_point(da.values, coord=da.lon.values)
    return data_c, lons_c, da.lat.values


def add_titles(ax, title_left):
    ax.set_title(title_left, loc="left", fontsize=13, fontweight="bold")
    ax.set_title(CLIM_STR,   loc="right", fontsize=9,  color="#888888")


def plot_global(data, lons, lats, fill_levs, cmap, title_left, cbar_label):
    proj = ccrs.PlateCarree(central_longitude=0)
    fig, ax = plt.subplots(figsize=(14, 7), subplot_kw={"projection": proj})
    ax.set_global()

    cf = ax.contourf(lons, lats, data,
                     levels=fill_levs, cmap=cmap, extend="both",
                     transform=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    ax.add_feature(cfeature.BORDERS,   linewidth=0.4, linestyle=":")

    gl = ax.gridlines(draw_labels=True, linewidth=0.4,
                      color="gray", alpha=0.5, linestyle="--")
    gl.top_labels   = False
    gl.right_labels = False

    plt.colorbar(cf, ax=ax, orientation="horizontal", pad=0.04, fraction=0.04,
                 label=cbar_label)
    add_titles(ax, title_left)
    return fig


def plot_na(data, lons, lats, fill_levs, cmap, title_left, cbar_label):
    lcc = ccrs.LambertConformal(central_longitude=-96, standard_parallels=(33, 45))
    fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={"projection": lcc})
    ax.set_extent([-165, -55, 15, 75], crs=ccrs.PlateCarree())

    cf = ax.contourf(lons, lats, data,
                     levels=fill_levs, cmap=cmap, extend="both",
                     transform=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.8)
    ax.add_feature(cfeature.BORDERS.with_scale("50m"),   linewidth=0.6)
    ax.add_feature(states,                               linewidth=0.4)

    gl = ax.gridlines(draw_labels=True, linewidth=0.4,
                      color="gray", alpha=0.5, linestyle="--")
    gl.top_labels   = False
    gl.right_labels = False

    plt.colorbar(cf, ax=ax, orientation="horizontal", pad=0.04, fraction=0.04,
                 label=cbar_label)
    add_titles(ax, title_left)
    return fig


def save(fig, path):
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {path}")


# =========================================================================
# 2m TEMPERATURE ANOMALY
# =========================================================================
ds_tmp_mean = xr.open_dataset(DATA_DIR / "air.2m.mon.mean.nc")
ds_tmp_ltm  = xr.open_dataset(DATA_DIR / "air.2m.mon.ltm.1991-2020.nc", use_cftime=True)

tmp_mean = ds_tmp_mean["air"].squeeze()
tmp_ltm  = ds_tmp_ltm["air"]

fill_levs_tmp = np.arange(-9, 9.1, 1)  # °F

for month_num, month_name in MONTHS.items():
    tmp_2016 = tmp_mean.sel(time=f"{YEAR}-{month_num:02d}").squeeze()
    tmp_clim = tmp_ltm.isel(time=month_num - 1)

    # Kelvin anomaly × 9/5 = °F anomaly (offset cancels in difference)
    anom_f = (tmp_2016 - tmp_clim) * 9 / 5

    data_c, lons_c, lats = prep_data(anom_f)
    title = f"2m Temperature Anomaly (°F) — {month_name} {YEAR}"
    stem  = f"tmp2m_anom_{YEAR}_{month_num:02d}_{month_name.lower()}"

    save(plot_global(data_c, lons_c, lats, fill_levs_tmp, "RdBu_r",
                     title, "Temperature Anomaly (°F)"),
         OUT_DIR / f"{stem}.png")

    save(plot_na(data_c, lons_c, lats, fill_levs_tmp, "RdBu_r",
                 title, "Temperature Anomaly (°F)"),
         OUT_DIR / f"{stem}_na.png")

# =========================================================================
# PRECIPITATION RATE ANOMALY
# =========================================================================
ds_prate_mean = xr.open_dataset(DATA_DIR / "prate.sfc.mon.mean.nc")
ds_prate_ltm  = xr.open_dataset(DATA_DIR / "prate.sfc.mon.ltm.1991-2020.nc", use_cftime=True)

prate_mean = ds_prate_mean["prate"]
prate_ltm  = ds_prate_ltm["prate"]

fill_levs_prate = np.arange(-3, 3.1, 0.25)  # in/month

for month_num, month_name in MONTHS.items():
    prate_2016 = prate_mean.sel(time=f"{YEAR}-{month_num:02d}").squeeze()
    prate_clim = prate_ltm.isel(time=month_num - 1)

    # kg m⁻² s⁻¹ → inches/month
    days   = DAYS_IN_MONTH[month_num]
    anom_in = (prate_2016 - prate_clim) * 86400 * days / 25.4

    data_c, lons_c, lats = prep_data(anom_in)
    title = f"Precipitation Anomaly (in/month) — {month_name} {YEAR}"
    stem  = f"prate_anom_{YEAR}_{month_num:02d}_{month_name.lower()}"

    save(plot_global(data_c, lons_c, lats, fill_levs_prate, "BrBG",
                     title, "Precipitation Anomaly (in/month)"),
         OUT_DIR / f"{stem}.png")

    save(plot_na(data_c, lons_c, lats, fill_levs_prate, "BrBG",
                 title, "Precipitation Anomaly (in/month)"),
         OUT_DIR / f"{stem}_na.png")

print("Done.")

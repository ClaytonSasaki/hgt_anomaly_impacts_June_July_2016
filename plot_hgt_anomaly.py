#!/usr/bin/env python3
"""
plot_hgt_anomaly.py

500 mb geopotential height anomaly maps for June and July 2016.
Data: NCEP/NCAR Reanalysis 1 monthly means vs. 1991-2020 climatology.
Output: PNG images saved to public_html/images/
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.util as cutil
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from pathlib import Path

DATA_DIR = Path("data")
OUT_DIR  = Path("public_html/images")
OUT_DIR.mkdir(exist_ok=True)

LEVEL  = 500.0   # hPa
YEAR   = 2016
MONTHS = {6: "June", 7: "July"}

# Contour levels (shared across all plots)
fill_levs = np.arange(-120, 121, 10) # for height anomalies
line_levs = np.arange(480, 591, 6)    # for height contours in dm

# State/province lines
states = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none"
)

# --- Load data ---
ds_mean = xr.open_dataset(DATA_DIR / "hgt.mon.mean.nc")
ds_ltm  = xr.open_dataset(DATA_DIR / "hgt.mon.ltm.1991-2020.nc", use_cftime=True)

hgt_mean = ds_mean["hgt"].sel(level=LEVEL)
hgt_ltm  = ds_ltm["hgt"].sel(level=LEVEL)

for month_num, month_name in MONTHS.items():
    # 2016 monthly mean at 500 mb
    hgt_2016 = hgt_mean.sel(time=f"{YEAR}-{month_num:02d}").squeeze()

    # Climatology: LTM time dim uses year=1 as placeholder, indexed Jan=0 ... Dec=11
    hgt_clim = hgt_ltm.isel(time=month_num - 1)

    # Anomaly (m)
    anom = hgt_2016 - hgt_clim

    # Shift lons from 0-360 to -180-180
    new_lon  = np.where(anom.lon.values > 180, anom.lon.values - 360, anom.lon.values)
    anom     = anom.assign_coords(lon=new_lon).sortby("lon")
    hgt_2016 = hgt_2016.assign_coords(lon=new_lon).sortby("lon")

    # Add cyclic longitude point to eliminate the seam at -180/180°
    lats = anom.lat.values
    anom_c, lons_c = cutil.add_cyclic_point(anom.values,     coord=anom.lon.values)
    hgt_c,  _      = cutil.add_cyclic_point(hgt_2016.values, coord=hgt_2016.lon.values)

    # ========================================================================= 
    # STATIC MAPS
    # =========================================================================
    
    # --------- Global Map ---------
    proj = ccrs.PlateCarree(central_longitude=0)
    fig, ax = plt.subplots(figsize=(14, 7), subplot_kw={"projection": proj})
    
    ax.set_global()

    # Filled anomaly contours (diverging: blue=trough, red=ridge)
    cf = ax.contourf(lons_c, lats, anom_c,
                     levels=fill_levs,
                     cmap="RdBu_r",
                     extend="both",
                     transform=ccrs.PlateCarree())

    # Actual 500 mb height contours in dm
    cl = ax.contour(lons_c, lats, hgt_c / 10,
                    levels=line_levs,
                    colors="k",
                    linewidths=0.7,
                    transform=ccrs.PlateCarree())
    labels = ax.clabel(cl, fmt="%d", fontsize=7, inline=True)
    for txt in labels:
        txt.set_path_effects([pe.withStroke(linewidth=2, foreground="white")])

    # Map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    ax.add_feature(cfeature.BORDERS,   linewidth=0.4, linestyle=":")

    # Gridlines
    gl = ax.gridlines(draw_labels=True, linewidth=0.4,
                      color="gray", alpha=0.5, linestyle="--")
    gl.top_labels   = False
    gl.right_labels = False

    # Colorbar
    plt.colorbar(cf, ax=ax,
                 orientation="horizontal",
                 pad=0.04, fraction=0.04,
                 label="500 mb Height Anomaly (m)")

    ax.set_title(f"500 mb Height (dm) and Anomaly (m) — {month_name} {YEAR}",
                 loc="left", fontsize=13, fontweight="bold")
    ax.set_title("Climatology: 1991–2020  |  NCEP/NCAR Reanalysis 1",
                 loc="right", fontsize=9, color="#888888")

    fname = OUT_DIR / f"hgt500_anom_{YEAR}_{month_num:02d}_{month_name.lower()}.png"
    fig.savefig(fname, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {fname}")

    # --------- North America Map ---------
    lcc = ccrs.LambertConformal(central_longitude=-96, standard_parallels=(33, 45))
    fig_na, ax_na = plt.subplots(figsize=(12, 9), subplot_kw={"projection": lcc})
    ax_na.set_extent([-165, -55, 15, 75], crs=ccrs.PlateCarree())

    # Filled anomaly contours (diverging: blue=trough, red=ridge)
    cf_na = ax_na.contourf(lons_c, lats, anom_c,
                           levels=fill_levs,
                           cmap="RdBu_r",
                           extend="both",
                           transform=ccrs.PlateCarree())

    # Actual 500 mb height contours in dm
    cl_na = ax_na.contour(lons_c, lats, hgt_c / 10,
                          levels=line_levs,
                          colors="k",
                          linewidths=0.7,
                          transform=ccrs.PlateCarree())
    labels_na = ax_na.clabel(cl_na, fmt="%d", fontsize=7, inline=True)
    for txt in labels_na:
        txt.set_path_effects([pe.withStroke(linewidth=2, foreground="white")])

    # Map features
    ax_na.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.8)
    ax_na.add_feature(cfeature.BORDERS.with_scale("50m"),   linewidth=0.6)
    ax_na.add_feature(states,                               linewidth=0.4)

    # Gridlines
    gl_na = ax_na.gridlines(draw_labels=True, linewidth=0.4,
                             color="gray", alpha=0.5, linestyle="--")
    gl_na.top_labels   = False
    gl_na.right_labels = False

    # Colorbar
    plt.colorbar(cf_na, ax=ax_na,
                 orientation="horizontal",
                 pad=0.04, fraction=0.04,
                 label="500 mb Height Anomaly (m)")

    ax_na.set_title(f"500 mb Height (dm) and Anomaly (m) — {month_name} {YEAR}",
                    loc="left", fontsize=13, fontweight="bold")
    ax_na.set_title("Climatology: 1991–2020  |  NCEP/NCAR Reanalysis 1",
                    loc="right", fontsize=9, color="#888888")

    fname_na = OUT_DIR / f"hgt500_anom_{YEAR}_{month_num:02d}_{month_name.lower()}_na.png"
    fig_na.savefig(fname_na, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig_na)
    print(f"Saved: {fname_na}")

    # =========================================================================
    # INTERACTIVE MAP OVERLAY (Transparent overlay PNG for Leaflet) 
    # ========================================================================= 
    # Web Mercator projection to align with Leaflet's default tile CRS. 
    # Square figure matches the 1:1 aspect ratio of the full Mercator world extent.
    LAT_LIMIT = 85.051129  # standard Web Mercator lat limit

    fig_ov = plt.figure(figsize=(8.0, 8.0))
    fig_ov.patch.set_alpha(0)
    ax_ov = fig_ov.add_axes(
        [0, 0, 1, 1],
        projection=ccrs.Mercator(central_longitude=0,
                                  min_latitude=-LAT_LIMIT,
                                  max_latitude=LAT_LIMIT)
    )
    ax_ov.set_extent([-179.99, 179.99, -LAT_LIMIT, LAT_LIMIT], crs=ccrs.PlateCarree())
    
    # Filled anomaly contours (diverging: blue=trough, red=ridge)
    ax_ov.contourf(lons_c, lats, anom_c,
                   levels=fill_levs, cmap="RdBu_r", extend="both",
                   transform=ccrs.PlateCarree())

    # Map features
    ax_ov.add_feature(cfeature.COASTLINE.with_scale("50m"),
                      linewidth=0.6, edgecolor="black")
    ax_ov.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="black")
    ax_ov.add_feature(states, linewidth=0.3, linestyle=":")

    # No axes
    ax_ov.set_axis_off()
    ax_ov.spines["geo"].set_visible(False)

    ov_fname = OUT_DIR / f"overlay_hgt500_anom_{YEAR}_{month_num:02d}_{month_name.lower()}.png"
    fig_ov.savefig(ov_fname, transparent=True, dpi=600, pad_inches=0)
    plt.close(fig_ov)
    print(f"Saved overlay: {ov_fname}")

print("Done.")

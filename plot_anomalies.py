#!/usr/bin/env python3
"""
plot_anomalies.py

500 mb geopotential height, 2m temperature, and precipitation rate anomaly
maps for June and July 2016.
Data: NCEP/NCAR Reanalysis 1 monthly means vs. 1991-2020 climatology.
Output: PNG images saved to public_html/images/
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.util as cutil
import json
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from cartopy.feature import ShapelyFeature
from pathlib import Path
from shapely.geometry import shape as shapely_shape

DATA_DIR = Path("data")
OUT_DIR  = Path("public_html/images")
OUT_DIR.mkdir(exist_ok=True)

YEAR          = 2016
MONTHS        = {6: "June", 7: "July"}
DAYS_IN_MONTH = {6: 30, 7: 31}
CLIM_STR      = "Climatology: 1991–2020  |  NCEP/NCAR Reanalysis 1"

states = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none"
)

# ── Corn Belt feature — loaded from corn_belt.geojson (run make_corn_belt.py first) ──
_cb_path = OUT_DIR.parent / "corn_belt.geojson"
if _cb_path.exists():
    with open(_cb_path) as _f:
        _cb_geoms = [shapely_shape(feat["geometry"])
                     for feat in json.load(_f)["features"]]
    corn_belt_feature = ShapelyFeature(
        _cb_geoms, ccrs.PlateCarree(),
        facecolor="none", edgecolor="#E6A817", linewidth=2.2
    )
else:
    corn_belt_feature = None
    print("Warning: corn_belt.geojson not found — run make_corn_belt.py first. "
          "Corn Belt overlay will be skipped.")


def prep_data(da):
    """Shift lons from 0 to 360 to -180 to 180 and add cyclic point."""
    new_lon = np.where(da.lon.values > 180, da.lon.values - 360, da.lon.values)
    da      = da.assign_coords(lon=new_lon).sortby("lon")
    data_c, lons_c = cutil.add_cyclic_point(da.values, coord=da.lon.values)
    return data_c, lons_c, da.lat.values


def add_titles(ax, title_left):
    ax.set_title(title_left, loc="left", fontsize=13, fontweight="bold")
    ax.set_title(CLIM_STR,   loc="right", fontsize=9,  color="#888888")


def _add_contours(ax, lons, lats, line_data, line_levs):
    cl = ax.contour(lons, lats, line_data,
                    levels=line_levs, colors="k", linewidths=0.7,
                    transform=ccrs.PlateCarree())
    labels = ax.clabel(cl, fmt="%d", fontsize=7, inline=True)
    for txt in labels:
        txt.set_path_effects([pe.withStroke(linewidth=2, foreground="white")])


def plot_global(data, lons, lats, fill_levs, cmap, title_left, cbar_label,
                line_data=None, line_levs=None):
    proj = ccrs.PlateCarree(central_longitude=0)
    fig, ax = plt.subplots(figsize=(14, 7), subplot_kw={"projection": proj})
    ax.set_global()

    cf = ax.contourf(lons, lats, data,
                     levels=fill_levs, cmap=cmap, extend="both",
                     transform=ccrs.PlateCarree())

    if line_data is not None:
        _add_contours(ax, lons, lats, line_data, line_levs)

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


def plot_na(data, lons, lats, fill_levs, cmap, title_left, cbar_label,
            line_data=None, line_levs=None, corn_belt_feat=None):
    lcc = ccrs.LambertConformal(central_longitude=-96, standard_parallels=(33, 45))
    fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={"projection": lcc})
    ax.set_extent([-165, -55, 15, 75], crs=ccrs.PlateCarree())

    cf = ax.contourf(lons, lats, data,
                     levels=fill_levs, cmap=cmap, extend="both",
                     transform=ccrs.PlateCarree())

    if line_data is not None:
        _add_contours(ax, lons, lats, line_data, line_levs)

    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.8)
    ax.add_feature(cfeature.BORDERS.with_scale("50m"),   linewidth=0.6)
    ax.add_feature(states,                               linewidth=0.4)

    if corn_belt_feat is not None:
        ax.add_feature(corn_belt_feat)

    gl = ax.gridlines(draw_labels=True, linewidth=0.4,
                      color="gray", alpha=0.5, linestyle="--")
    gl.top_labels   = False
    gl.right_labels = False

    plt.colorbar(cf, ax=ax, orientation="horizontal", pad=0.04, fraction=0.04,
                 label=cbar_label)
    add_titles(ax, title_left)
    return fig


def plot_overlay(data, lons, lats, fill_levs, cmap):
    """Mercator transparent PNG for Leaflet tile overlay.
    
    Web Mercator projection to align with Leaflet's default tile CRS. 
    Square figure matches the 1:1 aspect ratio of the full Mercator world extent.
    """
    LAT_LIMIT = 85.051129
    fig = plt.figure(figsize=(8.0, 8.0))
    fig.patch.set_alpha(0)
    ax = fig.add_axes(
        [0, 0, 1, 1],
        projection=ccrs.Mercator(central_longitude=0,
                                  min_latitude=-(LAT_LIMIT + 0.25),
                                  max_latitude=(LAT_LIMIT + 0.25))
    )
    ax.set_extent([-179.99, 179.99, -LAT_LIMIT, LAT_LIMIT], crs=ccrs.PlateCarree())

    ax.contourf(lons, lats, data,
                levels=fill_levs, cmap=cmap, extend="both",
                transform=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.6, edgecolor="black")
    ax.add_feature(cfeature.BORDERS,   linewidth=0.3, edgecolor="black")
    ax.add_feature(states,             linewidth=0.3, linestyle=":")

    ax.set_axis_off()
    ax.spines["geo"].set_visible(False)
    
    return fig

# =========================================================================
# 500 mb GEOPOTENTIAL HEIGHT ANOMALY (and actual heights)
# =========================================================================

# --- Load data ---
ds_hgt_mean = xr.open_dataset(DATA_DIR / "hgt.mon.mean.nc")
ds_hgt_ltm  = xr.open_dataset(DATA_DIR / "hgt.mon.ltm.1991-2020.nc", use_cftime=True)

hgt_mean = ds_hgt_mean["hgt"].sel(level=500.0)
hgt_ltm  = ds_hgt_ltm["hgt"].sel(level=500.0)

# Contour levels
fill_levs_hgt = np.arange(-120, 121, 10)  # m
line_levs_hgt = np.arange(480, 591, 6)    # dm

for month_num, month_name in MONTHS.items():
    
    # Get mean values for chosen month and calculate anomalies (m)
    hgt_2016 = hgt_mean.sel(time=f"{YEAR}-{month_num:02d}").squeeze()
    hgt_clim = hgt_ltm.isel(time=month_num - 1)
    anom     = hgt_2016 - hgt_clim

    # Update coordinates for plotting
    anom_c, lons_c, lats = prep_data(anom)
    hgt_c,  _,      _    = prep_data(hgt_2016)

    title = f"500 mb Height (dm) and Anomaly (m) — {month_name} {YEAR}"
    fname = f"hgt500_anom_{YEAR}_{month_num:02d}_{month_name.lower()}"

    # Plot anomalies (m) on global map with contours of actual heights (dm)
    # blue = below normal heights, red = above normal heights
    fig_global = plot_global(anom_c, lons_c, lats, fill_levs_hgt, "RdBu_r", title,
                             "500 mb Height Anomaly (m)",
                             line_data=hgt_c / 10, line_levs=line_levs_hgt)
    
    fig_global.savefig(OUT_DIR / f"{fname}.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig_global)
    print(f"Saved: {OUT_DIR / f'{fname}.png'}")

    # Plot anomalies (m) on North America map with contours of actual heights (dm)
    # blue = below normal heights, red = above normal heights
    fig_na = plot_na(anom_c, lons_c, lats, fill_levs_hgt, "RdBu_r", title,
                     "500 mb Height Anomaly (m)",
                     line_data=hgt_c / 10, line_levs=line_levs_hgt,
                     corn_belt_feat=corn_belt_feature)
    
    fig_na.savefig(OUT_DIR / f"{fname}_na.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig_na)
    print(f"Saved: {OUT_DIR / f'{fname}_na.png'}")

    # Create overlay of anomalies (m) for interactive map
    # blue = below normal heights, red = above normal heights
    fig_overlay = plot_overlay(anom_c, lons_c, lats, fill_levs_hgt, "RdBu_r")
    
    fig_overlay.savefig(OUT_DIR / f"overlay_{fname}.png", transparent=True, dpi=600, pad_inches=0)
    plt.close(fig_overlay)
    print(f"Saved overlay: {OUT_DIR / f'overlay_{fname}.png'}")



# =========================================================================
# 2m TEMPERATURE ANOMALY  (North America only)
# =========================================================================

# --- Load data ---
ds_tmp_mean = xr.open_dataset(DATA_DIR / "air.2m.mon.mean.nc")
ds_tmp_ltm  = xr.open_dataset(DATA_DIR / "air.2m.mon.ltm.1991-2020.nc", use_cftime=True)

tmp_mean = ds_tmp_mean["air"].squeeze()
tmp_ltm  = ds_tmp_ltm["air"]

# Contour levels
fill_levs_tmp = np.arange(-9, 9.1, 1)  # °F

for month_num, month_name in MONTHS.items():
    
    # Get mean values for chosen month and calculate anomalies (m)
    tmp_2016 = tmp_mean.sel(time=f"{YEAR}-{month_num:02d}").squeeze()
    tmp_clim = tmp_ltm.isel(time=month_num - 1)
    anom_f   = (tmp_2016 - tmp_clim) * 9 / 5 # °F anomaly = Kelvin anomaly × 9/5 (offset cancels in difference)

    # Update coordinates for plotting
    data_c, lons_c, lats = prep_data(anom_f)
    
    title = f"2m Temperature Anomaly (°F) — {month_name} {YEAR}"
    fname = f"tmp2m_anom_{YEAR}_{month_num:02d}_{month_name.lower()}"

    # Plot anomalies (°F) on North America map
    # Blue = cooler than normal, Red = warmer than normal
    fig_na = plot_na(data_c, lons_c, lats, fill_levs_tmp, "RdBu_r",
                     title, "Temperature Anomaly (°F)",
                     corn_belt_feat=corn_belt_feature)
    
    fig_na.savefig(OUT_DIR / f"{fname}_na.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig_na)
    print(f"Saved: {OUT_DIR / f'{fname}_na.png'}")


# =========================================================================
# PRECIPITATION RATE ANOMALY  (North America only)
# =========================================================================

# --- Load data ---
ds_prate_mean = xr.open_dataset(DATA_DIR / "prate.sfc.mon.mean.nc")
ds_prate_ltm  = xr.open_dataset(DATA_DIR / "prate.sfc.mon.ltm.1991-2020.nc", use_cftime=True)

prate_mean = ds_prate_mean["prate"]
prate_ltm  = ds_prate_ltm["prate"]

# Contour levels
fill_levs_prate = np.arange(-3, 3.1, 0.25)  # in/month

for month_num, month_name in MONTHS.items():
    
    # Get mean values for chosen month and calculate anomalies (m)
    prate_2016 = prate_mean.sel(time=f"{YEAR}-{month_num:02d}").squeeze()
    prate_clim = prate_ltm.isel(time=month_num - 1)
    days       = DAYS_IN_MONTH[month_num]
    anom_in    = (prate_2016 - prate_clim) * 86400 * days / 25.4 # kg m⁻² s⁻¹ → inches/month

    # Update coordinates for plotting
    data_c, lons_c, lats = prep_data(anom_in)
    
    title = f"Precipitation Anomaly (in/month) — {month_name} {YEAR}"
    fname = f"prate_anom_{YEAR}_{month_num:02d}_{month_name.lower()}"

    # Plot anomalies (in/month) on North America map
    # Brown = drier than normal, Green = wetter than normal
    fig_na = plot_na(data_c, lons_c, lats, fill_levs_prate, "BrBG",
                     title, "Precipitation Anomaly (in/month)",
                     corn_belt_feat=corn_belt_feature)
    
    fig_na.savefig(OUT_DIR / f"{fname}_na.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig_na)
    print(f"Saved: {OUT_DIR / f'{fname}_na.png'}")


print("Done.")

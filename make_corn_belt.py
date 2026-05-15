#!/usr/bin/env python3
"""
make_corn_belt.py

Downloads the NCEI CONUS climate divisions shapefile, filters by the
NOAA-defined Corn Belt CLIMDIV codes, dissolves into a single polygon,
reprojects from NAD83 to WGS84, and writes corn_belt.geojson to public_html/.

Reference map: https://www.ncei.noaa.gov/access/monitoring/reference-maps/corn-belt
"""

import cartopy.io.shapereader as shpreader
import json
import urllib.request
import zipfile
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import mapping
from shapely.ops import transform as shp_transform, unary_union

_here    = Path(__file__).resolve().parent
_pub     = _here / "public_html"
DATA_DIR = _here / "data"
ZIP_URL  = "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/CONUS_CLIMATE_DIVISIONS.shp.zip"
ZIP_PATH = DATA_DIR / "CONUS_CLIMATE_DIVISIONS.shp.zip"
SHP_PATH = DATA_DIR / "GIS.OFFICIAL_CLIM_DIVISIONS.shp"
OUT_FILE = (_pub if _pub.is_dir() else _here.parent / "public_html") / "corn_belt.geojson"

CORN_BELT_CLIMDIVS = {
    "0503",
    "1101", "1102", "1103", "1104", "1105", "1106", "1107",
    "1201", "1202", "1203", "1204", "1205", "1206", "1207", "1208", "1209",
    "1301", "1302", "1303", "1304", "1305", "1306", "1307", "1308", "1309",
    "2008", "2009",
    "2104", "2105", "2107", "2108", "2109",
    "2503", "2505", "2506", "2507", "2508", "2509",
    "3301", "3302", "3304", "3305", "3306", "3308",
    "3603",
    "3903", "3907", "3909",
    "4707", "4708", "4709",
}

# ── Download ──────────────────────────────────────────────────────────────────
DATA_DIR.mkdir(exist_ok=True)
if not ZIP_PATH.exists():
    print(f"Downloading {ZIP_URL} ...")
    urllib.request.urlretrieve(ZIP_URL, ZIP_PATH)
    print(f"Saved: {ZIP_PATH} ({ZIP_PATH.stat().st_size / 1e6:.1f} MB)")

# ── Extract ───────────────────────────────────────────────────────────────────
if not SHP_PATH.exists():
    print(f"Extracting {ZIP_PATH} ...")
    _keep = {".shp", ".dbf", ".shx", ".prj"}
    with zipfile.ZipFile(ZIP_PATH) as zf:
        for member in zf.namelist():
            if Path(member).suffix in _keep:
                zf.extract(member, DATA_DIR)
    print("Extracted.")

# ── Inspect ───────────────────────────────────────────────────────────────────
reader  = shpreader.Reader(str(SHP_PATH))
records = list(reader.records())

print(f"\nFields:         {list(records[0].attributes.keys())}")
print(f"Sample record:  { {k: v for k, v in list(records[0].attributes.items())[:6]} }")
print(f"Total divisions: {len(records)}\n")

# ── Filter ────────────────────────────────────────────────────────────────────
def climdiv_code(attrs):
    for field in ("CLIMDIV", "CLIMDIVID", "CLIMDIV_ID"):
        if field in attrs:
            return str(int(float(str(attrs[field]).strip()))).zfill(4)
    return ""

corn_belt_geoms = [rec.geometry for rec in records
                   if climdiv_code(rec.attributes) in CORN_BELT_CLIMDIVS]
print(f"Matched {len(corn_belt_geoms)} of {len(CORN_BELT_CLIMDIVS)} divisions")

if not corn_belt_geoms:
    print("No matches — printing first 3 records in full for debugging:")
    for rec in records[:3]:
        print(dict(rec.attributes))
    raise ValueError("No CLIMDIV matches — check field names printed above.")

# ── Dissolve ──────────────────────────────────────────────────────────────────
# Small buffer snaps nearly-coincident division borders before dissolving,
# then the negative buffer restores the original boundary.
_tol     = 0.001  # degrees (~100 m) — invisible at map scale
dissolved = unary_union([g.buffer(_tol) for g in corn_belt_geoms]).buffer(-_tol)
print(f"Dissolved geometry type: {dissolved.geom_type}")

# ── Reproject NAD83 → WGS84 ───────────────────────────────────────────────────
_transformer = Transformer.from_crs("EPSG:4269", "EPSG:4326", always_xy=True)
dissolved    = shp_transform(_transformer.transform, dissolved)

# ── Write GeoJSON ─────────────────────────────────────────────────────────────
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_FILE, "w") as f:
    json.dump({
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"name": "NOAA Corn Belt"},
            "geometry": mapping(dissolved)
        }]
    }, f)

print(f"\nSaved: {OUT_FILE}")
print("Preview: open public_html/index.php → Interactive Map tab → toggle Corn Belt on/off")

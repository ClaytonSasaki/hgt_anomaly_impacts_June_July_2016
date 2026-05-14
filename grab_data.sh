#!/bin/bash
#
# grab_data.sh
#
# Download monthly mean and 1991-2020 monthly climatology (WMO standard) files for NCEP/NCAR Reanalysis 1 from NOAA PSL
#
#   Pressure level (2.5° grid):
#     hgt.mon.mean.nc              : geopotential height, all years, all pressure levels 
#     hgt.mon.ltm.1991-2020.nc     : geopotential height climatology
#
#   Surface Gaussian grid:
#     air.2m.mon.mean.nc           : 2m air temperature, all years
#     air.2m.mon.ltm.1991-2020.nc  : 2m air temperature climatology
#
#     prate.sfc.mon.mean.nc        : precipitation rate, all years
#     prate.sfc.mon.ltm.1991-2020.nc : precipitation rate climatology
#
# Safe to re-run; existing up-to-date files are skipped.

set -euo pipefail

DEST_DIR="data"
BASE_PRES="https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Monthlies/pressure"
BASE_SURF="https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Monthlies/surface_gauss"

mkdir -p "${DEST_DIR}"

# -c   resume partial downloads (if the connection drops mid-pull)
# -N   only re-fetch if the server copy is newer than the local copy
# -P   place files in DEST_DIR

echo "Downloading geopotential height..."
wget -c -N -P "${DEST_DIR}" \
    "${BASE_PRES}/hgt.mon.mean.nc" \
    "${BASE_PRES}/hgt.mon.ltm.1991-2020.nc"

echo "Downloading 2m air temperature and surface precipitation rate..."
wget -c -N -P "${DEST_DIR}" \
    "${BASE_SURF}/air.2m.mon.mean.nc" \
    "${BASE_SURF}/air.2m.mon.ltm.1991-2020.nc" \
    "${BASE_SURF}/prate.sfc.mon.mean.nc" \
    "${BASE_SURF}/prate.sfc.mon.ltm.1991-2020.nc"

echo "Done. Files in ${DEST_DIR}/:"
ls -lh "${DEST_DIR}"

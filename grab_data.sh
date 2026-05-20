#!/bin/bash
#
# grab_data.sh
#
# Download NCEP/NCAR Reanalysis 1 data from NOAA PSL
#
# Monthly mean and 1991-2020 monthly climatology (WMO standard) files for
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
# Daily files (where monthly files won't work for our use) for
#
#   Surface Gaussian grid:
#     tmax.2m.gauss.XXXX.nc        : maximum 2m air temperature, each year 1991-2020 and 2016
#     tmin.2m.gauss.XXXX.nc        : minimum 2m air temperature, each year 1991-2020 and 2016
#
# Safe to re-run; existing up-to-date files are skipped.

set -euo pipefail

DEST_DIR="data"
BASE_MON_PRES="https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Monthlies/pressure"
BASE_MON_SURF="https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Monthlies/surface_gauss"

mkdir -p "${DEST_DIR}"

# -c   resume partial downloads (if the connection drops mid-pull)
# -N   only re-fetch if the server copy is newer than the local copy
# -P   place files in DEST_DIR

echo "Downloading monthly mean geopotential height..."
wget -c -N -P "${DEST_DIR}" \
    "${BASE_MON_PRES}/hgt.mon.mean.nc" \
    "${BASE_MON_PRES}/hgt.mon.ltm.1991-2020.nc"

echo "Downloading monthly mean 2m air temperature and surface precipitation rate..."
wget -c -N -P "${DEST_DIR}" \
    "${BASE_MON_SURF}/air.2m.mon.mean.nc" \
    "${BASE_MON_SURF}/air.2m.mon.ltm.1991-2020.nc" \
    "${BASE_MON_SURF}/prate.sfc.mon.mean.nc" \
    "${BASE_MON_SURF}/prate.sfc.mon.ltm.1991-2020.nc"

BASE_DAILY_SURF="https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Dailies/surface_gauss"

echo "Downloading daily 2m max/min temperatures..."
for year in $(seq 1991 2020); do
    wget -c -N -P "${DEST_DIR}" "${BASE_DAILY_SURF}/tmax.2m.gauss.${year}.nc"
    wget -c -N -P "${DEST_DIR}" "${BASE_DAILY_SURF}/tmin.2m.gauss.${year}.nc"
done

echo "Done. Files in ${DEST_DIR}/:"
ls -lh "${DEST_DIR}"

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>500 mb Height Anomaly — June &amp; July 2016</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>

<div class="page-header mb-0">
    <h4 class="fw-bold mb-1">500 mb Height Anomaly and Surface Impacts</h4>
    <p>June &amp; July 2016 &nbsp;&bull;&nbsp; vs. 1991–2020 Climatology &nbsp;&bull;&nbsp; NCEP/NCAR Reanalysis 1</p>
</div>

<div class="container-fluid py-3">

    <ul class="nav nav-tabs" id="mainTab" role="tablist">
        <li class="nav-item" role="presentation">
            <button class="nav-link active" id="tab-maps" data-bs-toggle="tab"
                    data-bs-target="#pane-maps" type="button">500 mb Heights</button>
        </li>
        <li class="nav-item" role="presentation">
            <button class="nav-link" id="tab-surface" data-bs-toggle="tab"
                    data-bs-target="#pane-surface" type="button">Surface Analysis</button>
        </li>
        <li class="nav-item" role="presentation">
            <button class="nav-link" id="tab-interactive" data-bs-toggle="tab"
                    data-bs-target="#pane-interactive" type="button">Interactive Map</button>
        </li>
    </ul>

    <div class="tab-content" id="mainTabContent">

        <!-- ── Static Maps ── -->
        <div class="tab-pane fade show active" id="pane-maps" role="tabpanel">

            <?php
            $caption = "Blue = anomalous troughing &nbsp;|&nbsp; Red = anomalous ridging &nbsp;|&nbsp; Black contours = 500 mb heights (dm)";
            $months  = [
                "June" => ["06", "june"],
                "July" => ["07", "july"],
            ];
            $views = [
                "Global"        => "",
                "North America" => "_na",
            ];
            ?>

            <?php foreach ($views as $view => $suffix): ?>
            <h6 class="text-center fw-semibold mt-4 mb-2"><?php echo $view; ?></h6>
            <div class="row g-4">
                <?php foreach ($months as $month => [$num, $slug]): ?>
                <div class="col-12 col-xl-6">
                    <img src="images/hgt500_anom_2016_<?php echo $num; ?>_<?php echo $slug . $suffix; ?>.png"
                         class="img-fluid rounded shadow-sm d-block mx-auto"
                         alt="<?php echo "$month 2016 $view"; ?>">
                    <p class="static-caption"><?php echo $caption; ?><?php if ($suffix === "_na") echo "<br>Gold outline = Corn Belt"; ?></p>
                </div>
                <?php endforeach; ?>
            </div>
            <?php endforeach; ?>

            <p class="mt-4 fst-italic text-muted">
                <strong class="text-body">Takeaway:</strong>
                Anomalously strong ridge centered just west of corn belt early in growing season
            </p>

        </div>

        <!-- ── Surface Analysis ── -->
        <div class="tab-pane fade" id="pane-surface" role="tabpanel">

            <p class="mt-4 fst-italic text-muted">
                <strong class="text-body">Takeaway:</strong>
                Ridge led to warmer than average temperatures (but NOT excessively hot) and a dry vegetative period,
                resulting in good growth conditions (more modified growing degree days). This was followed by
                near-normal temperatures and wetter than usual conditions during the grain-filling period.
                Throughout, soil moisture levels were near normal.
            </p>

            <div class="d-flex flex-wrap align-items-center gap-3 my-3">

                <div class="btn-group" role="group" aria-label="Zoom selector">
                    <input type="radio" class="btn-check" name="surf-zoom" id="surfZoomNA" value="na" autocomplete="off" checked>
                    <label class="btn btn-outline-secondary" for="surfZoomNA">North America</label>
                    <input type="radio" class="btn-check" name="surf-zoom" id="surfZoomCONUS" value="conus" autocomplete="off">
                    <label class="btn btn-outline-secondary" for="surfZoomCONUS">CONUS</label>
                </div>

                <div class="dropdown">
                    <button class="btn btn-outline-secondary dropdown-toggle" type="button"
                            id="monthsDropdown" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                        Months: Jun, Jul, Aug
                    </button>
                    <ul class="dropdown-menu p-2" style="min-width:130px">
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-month" value="05" data-label="May"> May
                        </label></li>
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-month" value="06" data-label="Jun" checked> June
                        </label></li>
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-month" value="07" data-label="Jul" checked> July
                        </label></li>
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-month" value="08" data-label="Aug" checked> August
                        </label></li>
                    </ul>
                </div>

                <div class="dropdown">
                    <button class="btn btn-outline-secondary dropdown-toggle" type="button"
                            id="varsDropdown" data-bs-toggle="dropdown" data-bs-auto-close="outside">
                        Vars: Temp, MGDD, Precip
                    </button>
                    <ul class="dropdown-menu p-2" style="min-width:210px">
                        <li><h6 class="dropdown-header px-2">Temperature Anomalies</h6></li>
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-var" value="tmp2m_anom" data-label="Temp" checked> 2m Temperature
                        </label></li>
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-var" value="tmax_heatdays_anom" data-label="Heat Days"> Days &gt;95&deg;F
                        </label></li>
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-var" value="sdd_anom" data-label="SDD"> Stress Degree Days
                        </label></li>
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-var" value="mgdd_anom" data-label="MGDD" checked> Modified GDD
                        </label></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><h6 class="dropdown-header px-2">Precipitation Anomalies</h6></li>
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-var" value="prate_anom" data-label="Precip" checked> Precipitation
                        </label></li>
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-var" value="soilw_0_10cm_anom" data-label="Soil 0-10cm"> Soil Moisture 0–10 cm
                        </label></li>
                        <li><label class="dropdown-item d-flex gap-2">
                            <input type="checkbox" class="surf-var" value="soilw_10_200cm_anom" data-label="Soil 10-200cm"> Soil Moisture 10–200 cm
                        </label></li>
                    </ul>
                </div>

            </div>

            <div id="surface-grid"></div>

            <p class="text-muted mt-3 mb-0" style="font-size:.8rem;">
                Agriculture metric source: <a href="https://www.mrcc.purdue.edu/resources/growing-degree-day-description"
                    target="_blank" rel="noopener">Midwestern Regional Climate Center</a>
            </p>

        </div><!-- /surface pane -->

        <!-- ── Interactive Map ── -->
        <div class="tab-pane fade" id="pane-interactive" role="tabpanel">

            <div class="d-flex flex-wrap align-items-center gap-3 my-3">
                <div class="btn-group" role="group" aria-label="Month selector">
                    <input type="radio" class="btn-check" name="month" id="btnMay" value="may" autocomplete="off">
                    <label class="btn btn-outline-primary" for="btnMay">May 2016</label>
                    <input type="radio" class="btn-check" name="month" id="btnJune" value="june" autocomplete="off" checked>
                    <label class="btn btn-outline-primary" for="btnJune">June 2016</label>
                    <input type="radio" class="btn-check" name="month" id="btnJuly" value="july" autocomplete="off">
                    <label class="btn btn-outline-primary" for="btnJuly">July 2016</label>
                    <input type="radio" class="btn-check" name="month" id="btnAugust" value="august" autocomplete="off">
                    <label class="btn btn-outline-primary" for="btnAugust">August 2016</label>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <label for="opacitySlider" class="form-label mb-0 text-muted small">Overlay opacity</label>
                    <input type="range" class="form-range" id="opacitySlider"
                           min="0" max="1" step="0.05" value="0.75" style="width:130px">
                </div>
                <div class="form-check form-switch d-flex align-items-center mb-0">
                    <input class="form-check-input me-2" type="checkbox" id="cornBeltToggle" checked>
                    <label class="form-check-label text-muted small" for="cornBeltToggle">Corn Belt<sup>*</sup></label>
                </div>
            </div>

            <div id="map" class="rounded shadow-sm"></div>

            <p class="text-muted mt-2 mb-0" style="font-size:.8rem;">
                <em><sup>*</sup> Due to projection of interactive map, corn belt outline is slightly displaced</em>
            </p>

        </div><!-- /interactive pane -->

    </div><!-- /tab-content -->

    <p class="text-muted mt-3 mb-0" style="font-size:.8rem;">
        Data source: <a href="https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html"
                        target="_blank" rel="noopener">NOAA PSL — NCEP/NCAR Reanalysis 1</a>
    </p>
    <p class="text-muted mt-1 mb-0" style="font-size:.8rem;">
        Corn Belt source: <a href="https://www.ncei.noaa.gov/access/monitoring/reference-maps/corn-belt"
                             target="_blank" rel="noopener">NOAA NCEI Geographical Reference Maps</a>
    </p>

</div><!-- /container -->

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="js/map.js"></script>
<script src="js/surface.js"></script>

</body>
</html>

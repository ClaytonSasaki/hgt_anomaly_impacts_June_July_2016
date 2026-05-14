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
                    <p class="static-caption"><?php echo $caption; ?></p>
                </div>
                <?php endforeach; ?>
            </div>
            <?php endforeach; ?>

        </div>

        <!-- ── Surface Analysis ── -->
        <div class="tab-pane fade" id="pane-surface" role="tabpanel">

            <?php
            $surface_vars = [
                "2m Temperature Anomaly" => [
                    "stem"    => "tmp2m_anom",
                    "caption" => "Blue = cooler than normal &nbsp;|&nbsp; Red = warmer than normal &nbsp;|&nbsp; Units: °F",
                ],
                "Precipitation Anomaly" => [
                    "stem"    => "prate_anom",
                    "caption" => "Brown = drier than normal &nbsp;|&nbsp; Green = wetter than normal &nbsp;|&nbsp; Units: in/month",
                ],
            ];
            $surf_months = [
                "June" => ["06", "june"],
                "July" => ["07", "july"],
            ];
            ?>

            <?php foreach ($surface_vars as $var_label => $var): ?>
            <h5 class="fw-semibold mt-4 mb-1"><?php echo $var_label; ?></h5>
            <div class="row g-4">
                <?php foreach ($surf_months as $month => [$num, $slug]): ?>
                <div class="col-12 col-xl-6">
                    <img src="images/<?php echo $var['stem']; ?>_2016_<?php echo $num; ?>_<?php echo $slug; ?>_na.png"
                         class="img-fluid rounded shadow-sm d-block mx-auto"
                         alt="<?php echo "$month 2016 $var_label North America"; ?>">
                    <p class="static-caption"><?php echo $var['caption']; ?></p>
                </div>
                <?php endforeach; ?>
            </div>
            <?php endforeach; ?>

        </div><!-- /surface pane -->

        <!-- ── Interactive Map ── -->
        <div class="tab-pane fade" id="pane-interactive" role="tabpanel">

            <div class="d-flex flex-wrap align-items-center gap-3 my-3">
                <div class="btn-group" role="group" aria-label="Month selector">
                    <input type="radio" class="btn-check" name="month" id="btnJune" value="june" autocomplete="off" checked>
                    <label class="btn btn-outline-primary" for="btnJune">June 2016</label>
                    <input type="radio" class="btn-check" name="month" id="btnJuly" value="july" autocomplete="off">
                    <label class="btn btn-outline-primary" for="btnJuly">July 2016</label>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <label for="opacitySlider" class="form-label mb-0 text-muted small">Overlay opacity</label>
                    <input type="range" class="form-range" id="opacitySlider"
                           min="0" max="1" step="0.05" value="0.75" style="width:130px">
                </div>
            </div>

            <div id="map" class="rounded shadow-sm"></div>

        </div><!-- /interactive pane -->

    </div><!-- /tab-content -->

    <p class="text-muted mt-3 mb-0" style="font-size:.8rem;">
        Data source: <a href="https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html"
                        target="_blank" rel="noopener">NOAA PSL — NCEP/NCAR Reanalysis 1</a>
    </p>

</div><!-- /container -->

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="js/map.js"></script>

</body>
</html>

// ── Map init ──────────────────────────────────────────────────────────────────
var LAT = 85.051129;

var map = L.map('map', {
    maxBounds: [[-LAT, -180], [LAT, 180]],
    maxBoundsViscosity: 1.0
}).setView([30, 0], 2);

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 19,
    noWrap: true
}).addTo(map);

// ── Anomaly overlays ──────────────────────────────────────────────────────────
var bounds = [[-LAT, -180], [LAT, 180]];
var opts   = {opacity: 0.75};

var overlays = {
    june: L.imageOverlay('images/overlay_hgt500_anom_2016_06_june.png', bounds, opts),
    july: L.imageOverlay('images/overlay_hgt500_anom_2016_07_july.png', bounds, opts)
};

var activeMonth = 'june';
overlays.june.addTo(map);

// Month toggle
document.querySelectorAll('input[name="month"]').forEach(function(radio) {
    radio.addEventListener('change', function() {
        map.removeLayer(overlays[activeMonth]);
        activeMonth = this.value;
        var opacity = parseFloat(document.getElementById('opacitySlider').value);
        overlays[activeMonth].setOpacity(opacity);
        overlays[activeMonth].addTo(map);
    });
});

// Opacity slider
document.getElementById('opacitySlider').addEventListener('input', function() {
    overlays[activeMonth].setOpacity(parseFloat(this.value));
});

// ── Legend ────────────────────────────────────────────────────────────────────
var legend = L.control({position: 'bottomright'});
legend.onAdd = function() {
    var div = L.DomUtil.create('div');
    div.innerHTML = `
      <div style="background:#fff;padding:8px 10px;border-radius:5px;
                  font-size:11px;box-shadow:0 1px 6px rgba(0,0,0,.25);line-height:1.4">
        <div style="font-weight:600;margin-bottom:4px">500 mb Height Anomaly (m)</div>
        <div style="height:12px;width:200px;border-radius:2px;background:
          linear-gradient(to right,
            #2166ac,#4393c3,#92c5de,#d1e5f0,#f7f7f7,#fddbc7,#f4a582,#d6604d,#b2182b)">
        </div>
        <div style="display:flex;justify-content:space-between;width:200px;margin-top:3px">
          <span>−120</span><span>−60</span><span>0</span><span>+60</span><span>+120</span>
        </div>
      </div>`;
    return div;
};
legend.addTo(map);

// ── Corn Belt GeoJSON ─────────────────────────────────────────────────────────
var cornBeltLayer = null;

fetch('corn_belt.geojson')
    .then(function(r) { return r.json(); })
    .then(function(data) {
        cornBeltLayer = L.geoJSON(data, {
            style: {
                color: '#E6A817',
                weight: 2.5,
                fillOpacity: 0,
                opacity: 0.9
            }
        }).addTo(map);
    });

document.getElementById('cornBeltToggle').addEventListener('change', function() {
    if (!cornBeltLayer) return;
    if (this.checked) {
        cornBeltLayer.addTo(map);
    } else {
        map.removeLayer(cornBeltLayer);
    }
});

// Fix map size when tab becomes visible
document.getElementById('tab-interactive').addEventListener('shown.bs.tab', function() {
    map.invalidateSize();
});

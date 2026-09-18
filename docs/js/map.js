// ── Variable config ───────────────────────────────────────────────────────────
var VAR_CONFIG = [
    {
        id: 'hgt500_anom',
        label: '500 mb Height Anomaly',
        unit: 'm',
        colorStops: '#2166ac,#4393c3,#92c5de,#d1e5f0,#f7f7f7,#fddbc7,#f4a582,#d6604d,#b2182b',
        ticks: ['−120', '−60', '0', '+60', '+120'],
    },
    {
        id: 'tmp2m_anom',
        label: '2m Temp Anomaly',
        unit: '°F',
        colorStops: '#2166ac,#4393c3,#92c5de,#d1e5f0,#f7f7f7,#fddbc7,#f4a582,#d6604d,#b2182b',
        ticks: ['−9', '−4.5', '0', '+4.5', '+9'],
    },
    {
        id: 'tmax_heatdays_anom',
        label: 'Days >95°F Anomaly',
        unit: 'days/month',
        colorStops: '#2166ac,#4393c3,#92c5de,#d1e5f0,#f7f7f7,#fddbc7,#f4a582,#d6604d,#b2182b',
        ticks: ['−20', '−10', '0', '+10', '+20'],
    },
    {
        id: 'sdd_anom',
        label: 'Stress Degree Days Anomaly',
        unit: '°F·days/month',
        colorStops: '#2166ac,#4393c3,#92c5de,#d1e5f0,#f7f7f7,#fddbc7,#f4a582,#d6604d,#b2182b',
        ticks: ['−200', '−100', '0', '+100', '+200'],
    },
    {
        id: 'mgdd_anom',
        label: 'Modified GDD Anomaly',
        unit: '°F·days/month',
        colorStops: '#2166ac,#4393c3,#92c5de,#d1e5f0,#f7f7f7,#fddbc7,#f4a582,#d6604d,#b2182b',
        ticks: ['−200', '−100', '0', '+100', '+200'],
    },
    {
        id: 'prate_anom',
        label: 'Precipitation Anomaly',
        unit: 'in/month',
        colorStops: '#8c510a,#bf812d,#dfc27d,#f6e8c3,#f7f7f7,#c7eae5,#80cdc1,#35978f,#003c30',
        ticks: ['−3', '−1.5', '0', '+1.5', '+3'],
    },
    {
        id: 'soilw_0_10cm_anom',
        label: 'Soil Moisture 0–10 cm Anomaly',
        unit: 'fraction',
        colorStops: '#8c510a,#bf812d,#dfc27d,#f6e8c3,#f7f7f7,#c7eae5,#80cdc1,#35978f,#003c30',
        ticks: ['−0.15', '−0.075', '0', '+0.075', '+0.15'],
    },
    {
        id: 'soilw_10_200cm_anom',
        label: 'Soil Moisture 10–200 cm Anomaly',
        unit: 'fraction',
        colorStops: '#8c510a,#bf812d,#dfc27d,#f6e8c3,#f7f7f7,#c7eae5,#80cdc1,#35978f,#003c30',
        ticks: ['−0.15', '−0.075', '0', '+0.075', '+0.15'],
    },
];

var MONTHS_MAP = [
    {val: 'may',    num: '05'},
    {val: 'june',   num: '06'},
    {val: 'july',   num: '07'},
    {val: 'august', num: '08'},
];

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

// ── Overlay management ────────────────────────────────────────────────────────
var bounds = [[-LAT, -180], [LAT, 180]];
var activeOverlay = null;
var activeVar   = 'hgt500_anom';
var activeMonth = 'june';

function overlayUrl(varId, monthVal, monthNum) {
    return 'images/overlay_' + varId + '_2016_' + monthNum + '_' + monthVal + '.png';
}

function switchOverlay(newVar, newMonth) {
    var opacity = parseFloat(document.getElementById('opacitySlider').value);
    var monthObj = MONTHS_MAP.find(function(m) { return m.val === newMonth; });
    var url = overlayUrl(newVar, monthObj.val, monthObj.num);

    if (activeOverlay) {
        map.removeLayer(activeOverlay);
    }
    activeOverlay = L.imageOverlay(url, bounds, {opacity: opacity}).addTo(map);
    activeVar   = newVar;
    activeMonth = newMonth;
    updateLegend();
}

// ── Variable selector control ─────────────────────────────────────────────────
var VarSelector = L.Control.extend({
    options: {position: 'topright'},
    onAdd: function() {
        var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
        container.style.cssText = 'background:#fff;padding:8px 10px;border-radius:5px;' +
            'font-size:12px;box-shadow:0 1px 6px rgba(0,0,0,.25);min-width:200px;';

        var label = L.DomUtil.create('div', '', container);
        label.style.cssText = 'font-weight:600;margin-bottom:6px;color:#333;';
        label.textContent = 'Variable';

        VAR_CONFIG.forEach(function(v) {
            var row = L.DomUtil.create('label', '', container);
            row.style.cssText = 'display:flex;align-items:center;gap:6px;cursor:pointer;' +
                'padding:2px 0;color:#555;';

            var radio = L.DomUtil.create('input', '', row);
            radio.type  = 'radio';
            radio.name  = 'map-var';
            radio.value = v.id;
            if (v.id === activeVar) radio.checked = true;

            var span = L.DomUtil.create('span', '', row);
            span.textContent = v.label;

            L.DomEvent.on(radio, 'change', function() {
                switchOverlay(this.value, activeMonth);
            });

            container.appendChild(row);
        });

        L.DomEvent.disableClickPropagation(container);
        L.DomEvent.disableScrollPropagation(container);
        return container;
    }
});

new VarSelector().addTo(map);

// ── Legend ────────────────────────────────────────────────────────────────────
var legend = L.control({position: 'bottomright'});
legend.onAdd = function() {
    this._div = L.DomUtil.create('div');
    this.update();
    return this._div;
};
legend.update = function() {
    var v = VAR_CONFIG.find(function(x) { return x.id === activeVar; });
    this._div.innerHTML =
        '<div style="background:#fff;padding:8px 10px;border-radius:5px;' +
        'font-size:11px;box-shadow:0 1px 6px rgba(0,0,0,.25);line-height:1.4">' +
        '<div style="font-weight:600;margin-bottom:4px">' + v.label + ' (' + v.unit + ')</div>' +
        '<div style="height:12px;width:200px;border-radius:2px;background:' +
        'linear-gradient(to right,' + v.colorStops + ')"></div>' +
        '<div style="display:flex;justify-content:space-between;width:200px;margin-top:3px">' +
        v.ticks.map(function(t) { return '<span>' + t + '</span>'; }).join('') +
        '</div></div>';
};
legend.addTo(map);

function updateLegend() {
    legend.update();
}

// ── Month toggle ──────────────────────────────────────────────────────────────
document.querySelectorAll('input[name="month"]').forEach(function(radio) {
    radio.addEventListener('change', function() {
        switchOverlay(activeVar, this.value);
    });
});

// ── Opacity slider ────────────────────────────────────────────────────────────
document.getElementById('opacitySlider').addEventListener('input', function() {
    if (activeOverlay) activeOverlay.setOpacity(parseFloat(this.value));
});

// ── Initial overlay ───────────────────────────────────────────────────────────
switchOverlay(activeVar, activeMonth);

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

var SURF_MONTHS = [
    {val: '05', slug: 'may',    label: 'May'},
    {val: '06', slug: 'june',   label: 'June'},
    {val: '07', slug: 'july',   label: 'July'},
    {val: '08', slug: 'august', label: 'August'},
];

var SURF_VARS = [
    {
        stem:    'tmp2m_anom',
        caption: 'Blue = cooler than normal &nbsp;|&nbsp; Red = warmer than normal &nbsp;|&nbsp; Units: &deg;F'
    },
    {
        stem:    'prate_anom',
        caption: 'Brown = drier than normal &nbsp;|&nbsp; Green = wetter than normal &nbsp;|&nbsp; Units: in/month'
    },
    {
        stem:    'tmax_heatdays_anom',
        caption: 'Blue = fewer days &gt;95&deg;F than normal &nbsp;|&nbsp; Red = more days &gt;95&deg;F than normal &nbsp;|&nbsp; Units: days/month'
    },
    {
        stem:    'sdd_anom',
        caption: 'Blue = fewer stress degree days than normal &nbsp;|&nbsp; Red = more stress degree days than normal &nbsp;|&nbsp; Units: &deg;F&middot;days/month'
    },
    {
        stem:    'mgdd_anom',
        caption: 'Blue = fewer modified growing degree days than normal &nbsp;|&nbsp; Red = more modified growing degree days than normal &nbsp;|&nbsp; Units: &deg;F&middot;days/month'
    },
    {
        stem:    'soilw_0_10cm_anom',
        caption: 'Brown = drier than normal &nbsp;|&nbsp; Green = wetter than normal &nbsp;|&nbsp; Soil moisture 0–10 cm BGL &nbsp;|&nbsp; Units: fraction'
    },
    {
        stem:    'soilw_10_200cm_anom',
        caption: 'Brown = drier than normal &nbsp;|&nbsp; Green = wetter than normal &nbsp;|&nbsp; Soil moisture 10–200 cm BGL &nbsp;|&nbsp; Units: fraction'
    },
];

function updateSurfaceGrid() {
    var zoom = document.querySelector('input[name="surf-zoom"]:checked').value;

    var selectedMonths = Array.from(document.querySelectorAll('.surf-month:checked'))
        .map(function(cb) {
            return SURF_MONTHS.find(function(m) { return m.val === cb.value; });
        });

    var selectedVars = Array.from(document.querySelectorAll('.surf-var:checked'))
        .map(function(cb) {
            return SURF_VARS.find(function(v) { return v.stem === cb.value; });
        });

    var grid = document.getElementById('surface-grid');
    grid.innerHTML = '';

    if (selectedMonths.length === 0 || selectedVars.length === 0) return;

    selectedMonths.forEach(function(month) {
        var row = document.createElement('div');
        row.className = 'row g-4 mt-2';

        var colClass = ['', 'col-12 col-xl-8 mx-auto', 'col-12 col-xl-6', 'col-12 col-xl-4'][selectedVars.length] || 'col-12 col-xl-4';

        selectedVars.forEach(function(v) {
            var fname = v.stem + '_2016_' + month.val + '_' + month.slug + '_' + zoom + '.png';
            var col = document.createElement('div');
            col.className = colClass;
            col.innerHTML =
                '<img src="images/' + fname + '" ' +
                     'class="img-fluid rounded shadow-sm d-block mx-auto" ' +
                     'alt="' + month.label + ' 2016 ' + v.stem + ' ' + zoom + '">' +
                '<p class="static-caption">' + v.caption + '<br>Gold outline = Corn Belt</p>';
            row.appendChild(col);
        });

        grid.appendChild(row);
    });
}

function updateDropdownLabel(btnId, selector) {
    var checked = Array.from(document.querySelectorAll(selector + ':checked'));
    var btn = document.getElementById(btnId);
    var prefix = btnId === 'monthsDropdown' ? 'Months' : 'Vars';
    if (checked.length === 0) {
        btn.textContent = prefix + ': None';
    } else {
        btn.textContent = prefix + ': ' + checked.map(function(cb) { return cb.dataset.label; }).join(', ');
    }
}

document.querySelectorAll('input[name="surf-zoom"]').forEach(function(radio) {
    radio.addEventListener('change', updateSurfaceGrid);
});

document.querySelectorAll('.surf-month').forEach(function(cb) {
    cb.addEventListener('change', function() {
        updateDropdownLabel('monthsDropdown', '.surf-month');
        updateSurfaceGrid();
    });
});

document.querySelectorAll('.surf-var').forEach(function(cb) {
    cb.addEventListener('change', function() {
        updateDropdownLabel('varsDropdown', '.surf-var');
        updateSurfaceGrid();
    });
});

updateSurfaceGrid();

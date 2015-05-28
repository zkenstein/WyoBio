define(['jquery', 'leaflet', 'wq/router', 'wq/locate', 'wq/app', 'wq/map', 'wq/photos', 'wq/template', './config'],
function($, L, router, locate, app, map, photos, tmpl, config) {
L.Icon.Default.imagePath= "/css/lib/images";

config.presync = function() {
    $('button.sync').html("Syncing...");
};
config.postsync = function(items) {
    $('button.sync').html("Sync Now");
    app.syncRefresh(items);
};

$('body').on('login', function() {
    app.prefetchAll();
    _showLogin(true);
});
$('body').on('logout', function() {
    app.prefetchAll();
    _showLogin(false);
});
function _showLogin(loggedIn) {
    if (loggedIn) {
        $('.logged-in').show();
        $('.logged-out').hide();
    } else {
        $('.logged-out').show();
        $('.logged-in').hide();
    }
}

app.init(config).then(function() {
    if (!app.user) {
        _showLogin();
    }
    map.init(config.map);
    photos.init();
    router.addRoute('observations/new', 's', _locatorMap);
    router.addRoute('', 's', function() {
        _showLogin(app.user);
    })
    app.jqmInit();
    app.prefetchAll();
});


function _locatorMap(match, ui, params, hash, evt, $page) {
	// Create Leaflet map
	var m = L.map('observation-new-map').fitBounds(config.map.bounds);
	map.createBaseMaps().Street.addTo(m);
	// Initialize basemaps & location ...

	// Configure Locator

	var fields = {
		'toggle': $page.find('input[name=mode]'),
		'latitude': $page.find('input[name=latitude]'),
		'longitude': $page.find('input[name=longitude]'),
		'accuracy': $('input[name=accuracy]')
	};

	var opts = {
		'onSetMode': function(mode) {
			var $editLoc = $page.find('.edit-loc');
			var $viewLoc = $page.find('.view-loc');
			if (mode == 'manual') {
				$editLoc.show();
				$viewLoc.hide();
			} else {
				$editLoc.hide();
				$viewLoc.show();
			}
		},
		'onUpdate': function(location, accuracy) {
			// TODO: Verify valid coordinates & accuracy
            $page.find('.view-loc').html(tmpl.render("{{>view_loc}}", {
                'latitude': location.lat,
                'longitude': location.lng,
                'accuracy': accuracy
            }));
		}
	}

	var locator = locate.locator(m, fields, opts);
}

});


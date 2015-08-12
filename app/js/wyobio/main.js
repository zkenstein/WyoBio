define(['jquery', 'leaflet',
        'wq/router', 'wq/locate', 'wq/app', 'wq/map', 'wq/photos', 'wq/template',
        './forms', './config',
        './outbox-delete', './add-photo'],
        function ($, L, router, locate, app, map, photos, tmpl, forms, config) {
            config.presync = function () {
                $('button.sync').html("Syncing...");
            };
            config.postsync = function (items) {
                $('button.sync').html("Sync Now");
                app.syncRefresh(items);
            };

            $('body').on('login', function () {
                app.prefetchAll();
                _showLogin(true);
            });
            $('body').on('logout', function () {
                app.prefetchAll();
                _showLogin(false);
            });
            $('body').on('filterablebeforefilter', "#species_list", _speciesLookup);
            $('body').on('click', "#species_list li", _speciesSelect);

            function _showLogin(loggedIn) {
                if (loggedIn) {
                    $('.logged-in').show();
                    $('.logged-out').hide();
                } else {
                    $('.logged-out').show();
                    $('.logged-in').hide();
                }
            }


            app.use(map);
            app.use(photos);
            app.use(forms);
            app.init(config).then(function () {
                if (!app.user) {
                    _showLogin();
                }
                router.addRoute('observations/new', 's', _locatorMap);
                router.addRoute('observations/new', 'h', _stopLocate);
                router.addRoute('', 'i', function () {
                    _showLogin(app.user);
                });
                app.jqmInit();
                app.prefetchAll().then(function () {
                    app.models.species.load().then(function (data) {
                        var types = {};
                        data.list.forEach(function (row) {
                            if (row.elem_type) {
                                types[row.elem_type] = true;
                            }
                        });
                        var type_list = Object.keys(types);
                        type_list.sort();
                        config.type_list = type_list;
                    });
                });
            });

            var _locator;
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
                    'onSetMode': function (mode) {
                        var $editLoc = $page.find('.edit-loc');
                        var $viewLoc = $page.find('.view-loc');
                        if (mode === 'manual') {
                            $editLoc.show();
                            $viewLoc.hide();
                        } else {
                            $editLoc.hide();
                            $viewLoc.show();
                        }
                    },
                    'onUpdate': function (location, accuracy) {
                        // TODO: Verify valid coordinates & accuracy
                        $page.find('.view-loc').html(tmpl.render("{{>view_loc}}", {
                            'latitude': location.lat,
                            'longitude': location.lng,
                            'accuracy': accuracy
                        }));
                    }
                };

                _locator = locate.locator(m, fields, opts);
            }
            
            function _stopLocate() {
                if (_locator) {
                    _locator.gpsStop();
                }
            }

            function _speciesLookup(evt, data) {
                var $ul = $(this),
                        $input = $(data.input),
                        value = $input.val().toLowerCase();
                if (!value || value.length <= 2) {
                    $ul.html("");
                    return;

                }
                var type = $.mobile.activePage.find("#type").val();
                $ul.html("species_loading");
                $ul.listview("refresh");
                app.models.species.load().then(function (data) {
                    var rows = [];
                    data.list.forEach(function (row) {
                        if (rows.length > 10) {
                            return;
                        }
                        if (row.elem_type !== type) {
                            return;
                        }
                        var label = row.label.toLowerCase();
                        if (label.indexOf(value) > -1) {
                            rows.push(row);
                        }
                    });



                    $ul.html(tmpl.render("species_choices", {'list': rows}));
                    $ul.listview("refresh");
                    $ul.trigger("updatelayout");


                });




            }

            function _speciesSelect() {
                var $li = $(this);
                var $page = $.mobile.activePage;
                $page.find("#species_guess").val($li.html().trim());
                $page.find("#species_id").val($li.data('id'));
                $page.find("#species_list").html("");

            }


        });





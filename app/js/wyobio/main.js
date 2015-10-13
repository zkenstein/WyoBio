define(['jquery', 'leaflet',
        'wq/router', 'wq/locate', 'wq/app', 'wq/map', 'wq/photos', 'wq/template', 'wq/owl',
        './forms', './config',
        './outbox-delete', './add-photo'],
        function ($, L, router, locate, app, map, photos, tmpl, owl, forms, config) {
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
			if (window.cordova) {
				_initNative();
			} else {
			    _initWeb();
			}

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
			app.use(owl);
            app.init(config).then(function () {
                if (!app.user) {
                    _showLogin();
                }
                router.addRoute('observations/new', 's', _locatorMap);
                router.addRoute('observations/new', 'h', _stopLocate);
				router.addRoute('outbox/<slug>/edit', 's', function(match) {
					app.runPlugins('observation', 'edit', match[1], match[0]);
				});
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
						if (type_list.length) {
                            config.type_list = type_list;
						}
                    });
                });
            });
			
			function _initNative() {
				var gaPlugin;
				$('body').on('click', "a[target=_blank]", function(evt) {
					window.open(this.href, '_blank', 'location=yes');
					evt.preventDefault();
					if (gaPlugin) {
						gaPlugin.trackPage(noop, noop, this.href);
					}
					owl("link", {'url': this.href});
				});
				if (!window.plugins || !window.plugins.gaPlugin) {
					return;
				}
				gaPlugin = window.plugins.gaPlugin;
				gaPlugin.init(noop, noop, config.mobile_analytics_id, 30);
				$('body').on('pageshow.screen', function() {
					var page = $.mobile.activePage.jqmData('title');
					gaPlugin.trackPage(noop, noop, page);
				});
				function noop() {};
			}
			
			function _initWeb() {
				(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
				(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
				m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
				})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
				ga('create', config.web_analytics_id, 'auto');
				ga('send', 'pageview')
				$('body').on('pageshow.screen', function() {
					var url = $.mobile.activePage.jqmData('url');
					var page = $.mobile.activePage.jqmData('title');
					ga('send', 'pageview', {'page': url, 'title': page});
				});
			}

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





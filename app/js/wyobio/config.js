define(["data/config", "data/version", "data/templates"],
function(config, version, templates) {

config.template = {
        'templates': templates,
        'defaults': {
        'version': version
        }
};

config.backgroundSync = -1;

config.transitions = {
    'default': "slide",
    'save': "flip"
};

config.map = {
    'bounds': [[40.9, -111], [45.0, -104]]
};

return config;

});

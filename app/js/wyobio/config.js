define(["data/config", "data/version", "data/templates"],
function(config, version, templates) {

config.debug = true;

config.type_list = [
    'Amphibian',
    'Arachnid',
    'Bird',
    'Crustacean',
    'Fish',
    'Insect',
    'Fungi',
    'Mammal',
    'Mollusc',
    'Plant',
    'Reptile'
];

config.template = {
    'templates': templates,
    'defaults': {
        'version': version,
        'first_photo': function() {
            if (this.photos && this.photos.length) {
                return this.photos[0];
            } else {
                return this.photos;
            }
        },
        'type_list': function() {
            var types = [];
            config.type_list.forEach(function(name) {
                types.push({
                    'id': name,
                    'label': name,
                    'selected': name === this.type
                });
            }, this);
            return types;
        }
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

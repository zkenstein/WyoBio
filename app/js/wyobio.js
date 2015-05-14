requirejs.config({
    'baseUrl': '/js/lib',
    'paths': {
        'wyobio': '../wyobio',
        'data': '../data/'
    }
});

requirejs(['wyobio/main']);

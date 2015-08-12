define(['wq/app', 'jquery', 'wq/outbox'], function(app, $, outbox) {
    $('body').on('click', 'button.delete', function() {
        var id = $(this).data('outbox-id');
        outbox.model.load().then(function(obdata) {
            var newlist = [];
            obdata.list.forEach(function(item) {
                if (item.id != id) {
                    newlist.push(item);
                }
            });
            obdata.list = newlist;
            outbox.model.overwrite(obdata).then(function() {
                app.go('observation', 'list');
            });
        });
    });
});
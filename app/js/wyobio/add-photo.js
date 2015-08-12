define(['wq/template', 'jquery'], function(tmpl, $) {
    $('body').on('click', 'button.addphoto', function() {
        var $newPhoto = $(tmpl.render("{{>new_photo}}", {
            'rowid': $.mobile.activePage.find('.photo-li').length,
            'deletable': true
        }));
        $(this).parents('li').before($newPhoto);
        $newPhoto.enhanceWithin();
        $newPhoto.parents('ul').listview('refresh');
        $newPhoto.find('button.photo-li-delete').on('click', function() {
            $newPhoto.remove();
        });
    });
});
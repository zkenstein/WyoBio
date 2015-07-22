define(['wq/router', 'jquery', 'jquery.validate'], function(router, $, jqv) {
function setup() {
    // Can't use the same URL for multiple routes
    router.addRoute('observations/ne.', 's', validate);
    router.addRoute('observations/<slug>/edi.', 's', validate);
}

function validate(match, ui, params, hash, evt, $page) {
    $page.find('form').validate({
         'errorPlacement': function(error, element){
             var errname = '.observation-' + element.attr('id') + "-errors";
             $page.find(errname).text(error.text());
         }
    });
}

return {
    'setup': setup
}
});
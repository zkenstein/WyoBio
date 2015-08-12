define(['jquery', 'jquery.validate', 'jquery.mobile'], function($, jqv, jqm) {

return {
    'name': 'forms',
    'init': function() {},
    'run': function(page, mode) {
        var $page = jqm.activePage;
        $page.find('form').validate({
            'ignore': '',
            'errorPlacement': function(error, element){
                var errname = '.observation-' + element.attr('id') + "-errors";
                $page.find(errname).text(error.text());
            }
        });
    }
};

});
jQuery(document).ready(function(){
  jQuery("select.chosen").chosen();
});
$(function() {
  $('.chosen').chosen();
});

function ajax(_url, _postOrGet, _data, _targetDivId) {

    $.ajax({
        type : _postOrGet,
        url : _url,
        data : _data,
        beforeSend : function() {
            // this is where we append a loading image
            $('#'+_targetDivId).html('<div class="loading"><img src="/site_media/static/img/ajax-loader.gif" alt="Loading..." /></div>');
        },
        success : function(data) {
            // successful request; do something with the data
            $('#'+_targetDivId).empty();
            $('#'+_targetDivId).html(data);
        },
        error : function() {
            // failed request; give feedback to user
            $($('#'+_targetDivId)).html('<div class="alert alert-error"><h4>An error occurred.</h4></div>');
        }
    }); 

}

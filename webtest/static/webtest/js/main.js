/* js file for webtest app */
function display_call(data, textStatus, jqXHR){
    alert(data);
    jQuery('#call_response').text(data);
}
function send_call() {
   var data = jQuery('#call_area').val();
   jQuery.post('/api/', data, function(a,b,c){display_call(a,b,c)}, 'json');
}

jQuery(document).ready(function() {
   jQuery('#call_send').click(send_call);
 });
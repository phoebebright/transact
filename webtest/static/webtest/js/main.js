/* js file for webtest app */
// Keep for future use ? Serializes a form to array with {"field_name": "field_value"}
// jQuery.fn.serializeForm = function(){a={};b=this.serializeArray();jQuery.each(b,function(d,c){a[c['name']]=c['value']});return a;}


function display_call(data){
    jQuery('#call_response').append(data);
}
function send_call() {
    var data = jQuery('#call_content').val();
    return false;
    jQuery.ajax({
        url:"/api/",
        type: "POST",
        data: data,
        contentType: "application/json; charset=UTF-8",
        success: display_call,
        accept: 'json'
    });
}

jQuery(document).ready(function() {
    jQuery('#call_api').click(function(){
        send_call();
        return false;
    });
 });
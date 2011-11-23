/* js file for webtest app */
// Keep for future use ? Serializes a form to array with {"field_name": "field_value"}
// jQuery.fn.serializeForm = function(){a={};b=this.serializeArray();jQuery.each(b,function(d,c){a[c['name']]=c['value']});return a;}


function display_call(data){
    data = JSON.stringify(data);
    data = data.replace(/\{/g, "<ul><li>{</li><ul><li>").replace(/\,/g,",</li><li>").replace(/\}/g,"</li></ul><li>}</li></ul>");
    data = jQuery('<div/>', {'id': "call_response", 'html':data});
    jQuery('#call_response').replaceWith(data);
}
function send_call() {
    var data = jQuery('#call_content').val();
    jQuery.ajax({
        url:"/api/",
        type: "POST",
        data: data,
        contentType: "application/json; charset=UTF-8",
        success: function(data){
            display_call(data);
        },
        accept: 'json'
    });
}

jQuery(document).ready(function() {
    jQuery('#call_api').click(function(){
        send_call();
        return false;
    });
 });
/* js file for webtest app */
/* Serializes a form to array with {"field_name": "field_value"} */
jQuery.fn.serializeForm = function(){a={};b=this.serializeArray();jQuery.each(b,function(d,c){a[c['name']]=c['value']});return a;}


function display_call(data){
    data = JSON.stringify(data);
    data = data.replace(/\{/g, "<ul><li>{</li><ul><li>").replace(/\,/g,",</li><li>").replace(/\}/g,"</li></ul><li>}</li></ul>");
    data = jQuery('<div/>', {'id': "call_response", 'html':data});
    jQuery('#call_response').replaceWith(data);
}
function send_call(input_data, callback) {
    jQuery.ajax({
        url:"/api/",
        type: "POST",
        data: input_data,
        contentType: "application/json; charset=UTF-8",
        success: function(data){
            callback(data);
        },
        accept: 'json'
    });
}


function sendFormCall(form){
    data = form.serializeForm();
    send_call(data, alert);
}
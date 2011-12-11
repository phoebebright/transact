var TransactAPI = null;
/*
Requiremnts:
  jQuery (http://jquery.com/)
  JSON (http://www.JSON.org/json2.js)

Basic usage
  TransactAPI.version - gives json api version
  TransactAPI.ping() - performs ping and logs to console results
  TransactAPI.login(username,pass) - performs login and sets TransactAPI.token for every next request
  TransactAPI.token - used with every TransactAPI.call request
  TransactAPI.call(callname, options, callback) - perform api call
    callname - string name of api call
    options - js object with all required options (token will be overridden by TransactAPI.token)
    callback in format:
            function (status, data) {}
              -status string
              -data object



  example:
  TransactAPI.call("PING", {}, function (status, data) {
        console(status);
        console(data);
    });



Advanced features:
  default callback
      TransactAPI.default_callback - by default points to log output to console callback
      if we ommit callback in TransactAPI.call default callback will be used
      so for eg we can use:
        TransactAPI.call("PING"); - with similar results as one example above




Limitations:
  transactcarbon.com currently using http authorization to be done before using this api
TODO: imput validation type checking for call, options, and callback
TODO: initialization of TransactAPI with token, connection string?

 */
(function(){
    
    function log(message){
        if(typeof console == "object"){
            console.log(message);
        }
    }
    function send_call(post_data, callback) {

        jQuery.ajax({
        url:"/api/",
        type: "POST",
        data: JSON.stringify(post_data),
        contentType: "application/json; charset=UTF-8",
        success: function(data){
            var status = data['status'];
            delete data['status'];
            callback(status,data);
        },
        accept: 'json'
    });
    }
    function add_token(status ,data) {
         if(status=="OK"){
             TransactAPI.token = data["token"];
             log('loggin successful');
         }
         else {
             log('could not login' + data);
         }
    }
    function ignore_callback(status, data) {}
    function log_callback(status, data) {
        log('status :' +status);
        log('data :');
        log(data);
    }
    TransactAPI = {
        "login": function(username, password){

            var options = {
                "username": username,
                "password": password
            }
            TransactAPI.call("LOGIN", options, add_token);
        },
        "ping": function(callback) {
          var callback = callback || log_callback;
          TransactAPI.call("PING", {} ,callback);
        },
        "token": "",
        "call": function(callname, options, callback){
            var callback = callback || TransactAPI.default_callback;
            var options = options || {};
            var data = jQuery.extend({
                "call": callname,
                "token": TransactAPI.token
            }, options);
            
            send_call(data, callback);
        },
        "default_callback": log_callback,
        "version": "0.4",
        "gate": "http://transactcarbon.com"
    }
})();

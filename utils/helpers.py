def generate_errors_list():
    from api import exceptions as api_exceptions
    from web import exceptions as web_exceptions
    codes = {}
    for obj_name, obj in api_exceptions.__dict__.items():
        try:
            if issubclass(obj, Exception):
                codes[obj.errorCode] = obj.txtMessage
        except TypeError:
            pass
    for obj_name, obj in web_exceptions.__dict__.items():
        try:
            if issubclass(obj, Exception):
                codes[obj.errorCode] = obj.txtMessage
        except TypeError:
            pass

    text = ""
    for k,v in codes.items():
        text +="<li>%s - %s</li>\n" % (k,v)
    return text

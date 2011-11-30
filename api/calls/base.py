import abc
from decimal import Decimal
import json
import time
import uuid
from api.exceptions import ValidationException, DispatcherException
from django.utils.translation import ugettext_lazy as _

import dispatcher
from django.utils.unittest.util import safe_str

from web.exceptions import ModelException
from api.exceptions import ApiException

ENCODING_JSON = 1


class ResponseJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return json.JSONEncoder.default(self, o)

def wrap(data):
    # FIXME: for some reason the ResponseJsonEncoder.default
    #       is not executed when passing Response object in here
    #       Pass dictionary (via Response.get_response())
    return json.dumps(data, encoding='utf8', cls=ResponseJsonEncoder)

def unwrap(json_data):
    return json.loads(json_data, encoding='utf8')

def dispatch(data):
    call = data.get('call')
    if not call or not isinstance(call, basestring):
        raise AttributeError("'call' missing")
    try:
        (module_name, klass_name) = dispatcher.calls.get(call.upper())
        from api import calls
        module = calls.__dict__[module_name]
        klass = module.__dict__[klass_name]
    except (TypeError, KeyError):
        raise DispatcherException()
    return klass(data)


class Request(object):
    response = None

    def __new__(cls, *args, **kw):
        if not cls.__name__.endswith("Request"):
            raise NameError("Request type class must be named with \
Request at the end, ie. SomeRequest")
        if not hasattr(cls, 'response') \
            or not hasattr(cls.response, '__base__') \
            or cls.response.__base__ is not Response:
            raise AttributeError("%s.request must be of type Response not %s"
                % (cls.__name__, type(cls.response).__name__))
        if kw:
            return super(Request, cls).from_dict(kw)
        return super(Request, cls).__new__(cls)

    def __init__(self, data):
        self.data = data
        self.validate()
        try:
            self.sanitize()
        except ValidationException, e:
            message = _('failed validation with %s') % e.txtMessage
            raise e.__class__(message=message)

    def sanitize(self):
        """ type checking of data should be done here
        """
        pass

    def validate(self):
        """ Validation of data should be done here
        """
        pass

    @abc.abstractmethod
    def run(self):
        """
        After the object is instantiated run this method which will return
        a Response.
        This method in each class inheriting from Request should contain
        all logic related to that request.
        """
        pass

    def get(self, itemname, default=None):
        """ Get optional parameters
        """
        return self.data.get(itemname, default)

    def require(self, itemname):
        """ require parameter optional parameters
            Raises ValidationError if parameter does not exist
        """
        if itemname in self.data.keys():
            return self.data.get(itemname)
        else:
            raise ValidationException(_("parameter '%s' is required") % itemname)

class Response(object):
    def __new__(cls, *args, **kw):
        if not cls.__name__.endswith("Response"):
            raise NameError("Response type class must be named with \
Response at the end, ie. SomeResponse")
        return super(Response, cls).__new__(cls)

    def __init__(self, *args, **kw):
        super(Response, self).__init__()
        self.data = {}
        status = kw.get("status") or "OK"
        self.data["status"] = status
        self.data["timestamp"] = self._timestamp()
        self.data["call"] = self._call()
        for k, v in kw.items():
            self.data[k] = v

    def _timestamp(self):
        return int(time.time() * 1000)

    def _call(self):
        name = self.__class__.__name__
        to_remove = len("Response")
        call = name.upper()[:-to_remove]
        return call

    def get_json(self):
        """ Return wrapped response to json
        """
        return wrap(self.data)

    def set(self, itemname, value):
        self.data[itemname] = value

class ErrorResponse(Response):

    def __init__(self, request=None, exception=None, status="FAILED", call="None", code=500, *args, **kw):
        super(ErrorResponse, self).__init__(*args, **kw)
        description = safe_str(exception)
        if request:
            call = request.response()._call()
            print repr(call)
        if isinstance(exception, (ModelException, ApiException, ValidationException)):
            code = exception.errorCode
            description = exception.txtMessage
        self.data["call"] = call
        self.data["status"] = status
        self.data["code"] = code
        self.data["description"] = description


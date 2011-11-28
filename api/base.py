import abc
from decimal import Decimal
import json
import time
import uuid
from api.exceptions import ValidationException
import micromodels
from django.utils.translation import ugettext_lazy as _

import dispatcher

from web.exceptions import ModelException
from api.exceptions import ApiException

ENCODING_JSON = 1

class StaticClassError(Exception):
    pass


class StaticClass:
    __metaclass__ = abc.ABCMeta

    def __new__(cls, *args, **kw):
        raise StaticClassError(
        "%s is a static class and cannot be instantiated."
        % cls.__name__)


class ResponseJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if hasattr(o, "__class__") \
                and issubclass(o.__class__, Response):
            return o.get_response()
        return json.JSONEncoder.default(self, o)

class JsonWrapper(StaticClass):
    @staticmethod
    def wrap(data):
        # FIXME: for some reason the ResponseJsonEncoder.default
        #       is not executed when passing Response object in here
        #       Pass dictionary (via Response.get_response())
        return json.dumps(data, encoding='utf8', cls=ResponseJsonEncoder)

    @staticmethod
    def unwrap(json_data):
        data = json.loads(json_data, encoding='utf8')
        call = data.get('call')
        if not call or not isinstance(call, basestring):
            raise AttributeError("'call' missing")
        (module, klass) = dispatcher.calls.get(call.upper())
        import api
        module = api.__dict__[module]
        klass = module.__dict__[klass]
        return klass.factory(data)


class CallableField(micromodels.BaseField):
    def to_serial(self):
        return self.data()


class Request(micromodels.Model):
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

    @classmethod
    def dispatch(cls, data, encoding=ENCODING_JSON):
        if encoding == ENCODING_JSON:
            return JsonWrapper.unwrap(data)
        raise AttributeError("Unknown encoding %s" % encoding)

    @abc.abstractmethod
    def run(self):
        """
        After the object is instantiated run this method which will return
        a Response.
        This method in each class inheriting from Request should contain
        all logic related to that request.
        """
        pass

    @classmethod
    def factory(cls, data):
        """
        Pass reference of this method to wrapper when unwrapping data
        """
        return cls.from_dict(data)
    def get(self, itemname, default=None):
        """ Get optional parameters
        """
        if itemname in self.__dict__:
            return self.__getattribute__(itemname)
        else:
            return default

    def require(self, itemname):
        """ require parameter optional parameters
            Raises ValidationError if parameter does not exist
        """
        if itemname in self.__dict__:
            return self.__getattribute__(itemname)
        else:
            raise ValidationException(_("parameter '%s' is required") % itemname)

class Response(micromodels.Model, dict):
    def __new__(cls, *args, **kw):
        if not cls.__name__.endswith("Response"):
            raise NameError("Response type class must be named with \
Response at the end, ie. SomeResponse")
        return super(Response, cls).__new__(cls)

    def __init__(self, *args, **kw):
        super(Response, self).__init__()
        status = kw.get("status") or "OK"
        self.add_field("status", status, micromodels.CharField())
        self.add_field("timestamp", self._timestamp, CallableField())
        self.add_field("call", self._call, CallableField())
        for k, v in kw.items():
            setattr(self, k, v)

    def _timestamp(self):
        return int(time.time() * 1000)

    def _call(self):
        name = self.__class__.__name__
        toremove = len("Response")
        call = name.upper()[:-toremove]
        return call

    def get_response(self):
        """
        Use this to pass data to a wrapper
        """
        return self.to_dict(serial=True)

    def get_json(self):
        """ Return wrapped response to json
        """
        return JsonWrapper.wrap(self.get_response())

# API REQUESTS AND RESPONSES

class ErrorResponse(Response):
    code = micromodels.IntegerField()
    description = micromodels.CharField()

    def __init__(self, request=None, exception=None, status="FAILED", call="None", code=500, *args, **kw):
        super(ErrorResponse, self).__init__(*args, **kw)
        description = str(exception)
        if request:
            call = request.response()._call()
        if isinstance(exception, (ModelException, ApiException, ValidationException)):
            code = exception.errorCode
            description = exception.txtMessage
        self.add_field("call", call, micromodels.CharField())
        self.status = status
        self.code = code
        self.description = description

    

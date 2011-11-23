import abc
import json
import time
import uuid
import micromodels

import dispatcher

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


# API REQUESTS AND RESPONSES

class ErrorResponse(Response):
    code = micromodels.IntegerField()
    description = micromodels.CharField()

    def __init__(self, code=500, call="None", status="FAILED", *args, **kw):
        super(ErrorResponse, self).__init__(*args, **kw)
        self.add_field("call", call, micromodels.CharField())
        self.status = status
        self.code = code

    
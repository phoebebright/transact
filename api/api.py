import abc
import json
import time
import uuid
import micromodels


class StaticClassError(Exception):
    pass


class StaticClass:
    __metaclass__ = abc.ABCMeta

    def __new__(cls, *args, **kw):
        raise StaticClassError(
        "%s is a static class and cannot be instantiated."
        % cls.__name__)


class JsonWrapper(StaticClass):
    @staticmethod
    def wrap(data):
        return json.dumps(data, encoding='utf8')

    @staticmethod
    def unwrap(json_data, factory):
        data = json.loads(json_data, encoding='utf8')
        return factory(data)


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
        return super(Request, cls).__new__(cls)

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


class Response(micromodels.Model):
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
        return self.__class__.__name__.rstrip("Response").upper()

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


class AuthResponse(Response):
    token = micromodels.CharField()
    expires = micromodels.IntegerField()


class AuthRequest(Request):
    authID = micromodels.CharField()
    secret = micromodels.CharField()

    response = AuthResponse

    def run(self):
        if self.authID == "secret" and self.secret == "sauce":
            return self.response(token=uuid.uuid4().hex,
                            expires=int((time.time() + 300) * 1000)
                            )
        else:
            return ErrorResponse(code=401, call="AUTH",
                                description="Authentication failed.")

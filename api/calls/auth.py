from api.exceptions import NotAuthenticatedException, LoginFailedException
from django.contrib.auth import authenticate
from api.calls.base import *
from livesettings import config_value
from django.core.cache import cache

class AuthResponse(Response):
    """
    token - string
    expires - integer
    """


class AuthRequest(Request):
    """
    authID - string
    secret - string
    """

    response = AuthResponse

    def run(self):
        if self.authID == "secret" and self.secret == "sauce":
            return self.response(token=uuid.uuid4().hex,
                            expires=int((time.time() + 300) * 1000),
                            client = user.get_profile().client,
                            
                            )
        raise NotAuthenticatedException()

class LoginResponse(Response):
    """
#    token = micromodels.CharField()
#    expires = micromodels.IntegerField()
    """

class LoginRequest(Request):
    """
#    username = micromodels.CharField()
#    password = micromodels.CharField()
    """
    response = LoginResponse

    def run(self):
        user = authenticate(username=self.require("username"), password=self.require("password"))
        if user and user.is_active:
            token = uuid.uuid4().hex
            
            expires = int(config_value('api','TOKEN_EXPIRY'))
            cache.set(token, user.username, expires)
            return self.response(token=token,
                            expires=expires,
                            )
        raise LoginFailedException()

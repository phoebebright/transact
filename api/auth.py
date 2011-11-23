from django.contrib.auth import authenticate
from base import *
from livesettings import config_value
from django.core.cache import cache

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

class LoginResponse(Response):
    token = micromodels.CharField()
    expires = micromodels.IntegerField()

class LoginRequest(Request):
    username = micromodels.CharField()
    password = micromodels.CharField()

    response = LoginResponse

    def run(self):
        user = authenticate(username=self.username, password=self.password)
        from django.contrib.auth.models import User
        if user and user.is_active:
            token = uuid.uuid4().hex

            expires = int(config_value('api','TOKEN_EXPIRY'))
            cache.set(token, user.username, expires)
            return self.response(token=token,
                            expires=expires
                            )
        else:
            return ErrorResponse(code=402, call="LOGIN",
                                description="Login failed.")

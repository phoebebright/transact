from django.contrib.auth import authenticate
from base import *


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
#        if authenticate():
#            return self.response(token=uuid.uuid4().hex,
#                            expires=int((time.time() + 300) * 1000)
#                            )
#        else:
            return ErrorResponse(code=402, call="LOGIN",
                                description="Login failed.")

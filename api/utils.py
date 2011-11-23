from base import *


class PingResponse(Response):
    pass


class PingRequest(Request):
    response = PingResponse

    def run(self):
        return self.response()

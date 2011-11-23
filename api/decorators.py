from django.contrib.auth.models import User
from django.core.cache import cache
from base import ErrorResponse

def authenticated(run_func):
    """
    """
    def wrapped_view(self):
        value = cache.get(self.token)
        try:
            user = User.objects.get(username=value)
            self.user = user
        except User.DoesNotExist:
            return ErrorResponse(code=403, call=self.response()._call(),
                                description="Not Authenticated")

        resp = run_func(self)
        return resp
    return wrapped_view
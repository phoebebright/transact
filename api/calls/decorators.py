from api.exceptions import NotAuthenticatedException
from django.contrib.auth.models import User
from django.core.cache import cache
from base import ErrorResponse

def authenticated(run_func):
    """
    """
    def wrapped_view(self):
        value = cache.get(self.get("token"))
        try:
            user = User.objects.get(username=value)
            self.user = user
        except User.DoesNotExist:
            raise NotAuthenticatedException()

        resp = run_func(self)
        return resp
    return wrapped_view
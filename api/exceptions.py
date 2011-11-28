from django.utils.translation import ugettext_lazy as _

class ApiException(Exception):
    errorCode = 400
    txtMessage = ""
    def __init__(self, message=None, *args, **kwargs):
        if message:
            self.txtMessage = message


class NotAuthenticatedException(ApiException):
    '''
    raised if invalid Token passed
    '''
    txtMessage = _('Not authenticated')
    errorCode = 401

class LoginFailedException(ApiException):
    '''
    raised if failed login conditionals
    '''
    txtMessage = _('username/password not valid')
    errorCode = 402


class ValidationException(Exception):
    errorCode = 300
    txtMessage = ""
    def __init__(self, message=None, *args, **kwargs):
        if message:
            self.txtMessage = message

    def __str__(self):
        return "(%s) %s [%s]" % (
            self.__class__.__name__,
            self.txtMessage,
            self.errorCode
        )

class ValidationDecimalException(ValidationException):
    errorCode = 301
    txtMessage = "not valid decimal format"
    def __init__(self, message=None, *args, **kwargs):
        if message:
            self.txtMessage = message

class DispatcherException(ValidationException):
    """raises if dispacher fails to find api call"""
    txtMessage = _('API Call not supported')
    errorCode = 302

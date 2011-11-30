
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
    txtMessage = 'Not authenticated'
    errorCode = 401

class LoginFailedException(ApiException):
    '''
    raised if failed login conditionals
    '''
    txtMessage = 'username/password not valid'
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

class DispatcherException(ValidationException):
    """raises if dispacher fails to find api call"""
    txtMessage = 'API Call not supported'
    errorCode = 302

class TransactionClosedException(ApiException):
    txtMessage = 'Transaction Closed'
    errorCode = 403

class TransactionNotExistException(ApiException):
    txtMessage = 'Transaction does not exist'
    errorCode = 404

class TransactionNeedsQtyorValException(ApiException):
    txtMessage = 'Transaction needs a quantity or value'
    errorCode = 405

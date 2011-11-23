from django.utils.translation import ugettext_lazy as _

class ModelException(Exception):

    pass
    
class NoMatchInPoolException(ModelException):
    '''
    raised if no match found criteria when searching the pool
    '''
    txtMessage = _('No match found in Pool')
    errorCode = 101
    
class BelowMinQuantity(ModelException):
    '''
    raised if request to price quantity below minimum in settings
    '''
    txtMessage = _('Below minimum quantity allowed')
    errorCode = 102
        
class AboveMaxQuantity(ModelException):
    '''
    raised if request to price quantity above maximum in settings
    '''
    txtMessage = _('Above maximum quantity allowed')
    errorCode = 103   
    
class Unable2CancelTransaction(ModelException):
    '''
    raised if transaction is still open and therefore cannot cancel it
    '''
    txtMessage = _('Open Transaction cannot be cancelled')
    errorCode = 104       
    
class Unable2RefundTransaction(ModelException):
    '''
    raised if transaction is still open and therefore cannot refund it
    '''
    txtMessage = _('Open Transaction cannot be Refunded')
    errorCode = 105     
    
class Unable2ExpireTransaction(ModelException):
    '''
    raised if transaction is still open and therefore cannot expire it
    '''
    txtMessage = _('Closed Transaction cannot be Expired')
    errorCode = 105         
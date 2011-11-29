from django.utils.translation import ugettext_lazy as _

class ModelException(Exception):
    errorCode = 100
    txtMessage = ""
    def __init__(self, message=None, *args, **kwargs):
        if message:
            self.txtMessage = message
    
class NoMatchInPoolException(ModelException):
    '''
    raised if no match found criteria when searching the pool
    '''
    txtMessage = _('No match found in Pool')
    errorCode = 101

class NoMatchInPoolClientException(ModelException):
    '''
    raised if no match found criteria when searching the pool
    used the criteria set for the client
    '''
    txtMessage = _('No match found in Pool for this clients defaults')
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
    errorCode = 106        
    
class Unable2RemoveUnits(ModelException):
    '''
    raised if trying to remove more units from a Pool item than there are
    units available
    '''
    txtMessage = _('Trying to remove more units than are available')
    errorCode = 107        
    
class ProductQualityRequired(ModelException):
    '''
    raised if trying to put a product in the pool where quality has not been defined
    '''
    txtMessage = _('Product must have a Quality before being put in the Pool')
    errorCode = 108        
    
class ProductTypeRequired(ModelException):
    '''
    raised if trying to remove more units from a Pool item than there are
    units available
    '''
    txtMessage = _('Product must have a Product Type before being put in the Pool')
    errorCode = 109

class InvalidProductType(ModelException):
    '''
    A string product type has been passed to a function but it does not match
    a code in ProductType
    '''
    txtMessage = _('Invalid Product Type')
    errorCode = 110
    

    

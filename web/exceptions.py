
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
    txtMessage = 'No match found in Pool'
    errorCode = 101

class NoMatchInPoolClientException(ModelException):
    '''
    raised if no match found criteria when searching the pool
    used the criteria set for the client
    '''
    txtMessage = 'No match found in Pool for this clients defaults'
    errorCode = 101
    
class BelowMinQuantity(ModelException):
    '''
    raised if request to price quantity below minimum in settings
    '''
    txtMessage = 'Below minimum quantity allowed'
    errorCode = 102
        
class AboveMaxQuantity(ModelException):
    '''
    raised if request to price quantity above maximum in settings
    '''
    txtMessage = 'Above maximum quantity allowed'
    errorCode = 103   
    
class Unable2CancelTransaction(ModelException):
    '''
    raised if transaction is closed and therefore cannot cancel it
    '''
    txtMessage = 'Closed Transaction cannot be cancelled'
    errorCode = 104       
    
class Unable2RefundTransaction(ModelException):
    '''
    raised if transaction is still open and therefore cannot refund it
    '''
    txtMessage = 'Open Transaction cannot be Refunded'
    errorCode = 105     
    
class Unable2ExpireTransaction(ModelException):
    '''
    raised if transaction is still open and therefore cannot expire it
    '''
    txtMessage = 'Closed Transaction cannot be Expired'
    errorCode = 106        
    
class Unable2RemoveUnits(ModelException):
    '''
    raised if trying to remove more units from a Pool item than there are
    units available
    '''
    txtMessage = 'Trying to remove more units than are available'
    errorCode = 107        
    
class ProductQualityRequired(ModelException):
    '''
    raised if trying to put a product in the pool where quality has not been defined
    '''
    txtMessage = 'Product must have a Quality before being put in the Pool'
    errorCode = 108        
    
class ProductTypeRequired(ModelException):
    '''
    raised if trying to remove more units from a Pool item than there are
    units available
    '''
    txtMessage = 'Product must have a Product Type before being put in the Pool'
    errorCode = 109

class InvalidProductType(ModelException):
    '''
    A string product type has been passed to a function but it does not match
    a code in ProductType
    '''
    txtMessage = 'Invalid Product Type'
    errorCode = 110
    

class TransactionNeedsQtyorVal(ModelException):
    ''' Tried to create a new transaction without specify quantity or value
    '''
    txtMessage = 'New Transaction needs a quantity or value'
    errorCode = 111


class NotEnoughFunds(ModelException):
    ''' Tried to pay for a transaction without enough funds
    '''
    txtMessage = 'Not enough Funds'
    errorCode = 112
    
class BelowMinValue(ModelException):
    '''
    raised if request to buy item that has a total price below the minimum
    '''
    txtMessage = 'Below minimum value allowed'
    errorCode = 113
    
class MissingPaymentNotification(ModelException):
    '''
    raised if record in Notification table missing
    '''
    txtMessage = 'Missing item TransactionPaid in web_clientnotification table'
    errorCode = 114
     
class MissingRechargeNotification(ModelException):
    '''
    raised if record in Notification table missing
    '''
    txtMessage = 'Missing item AccountRecharge in web_clientnotification table'
    errorCode = 114    
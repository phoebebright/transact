#from decimal import Decimal

from api.calls.fields import DecimalField
from api.exceptions import TransactionClosedException, TransactionNotExistException, TransactionNeedsQtyorValException, \
        TransactionUserNotAuthorized
from decorators import authenticated
from api.calls.base import *
import api.config
from livesettings import config_value


#
class PriceCheckResponse(Response):
    pass
#    quantity = micromodels.FloatField()
#    type = micromodels.CharField()
#    quality = micromodels.CharField()
#    currencies = micromodels.BaseField()  # dictionary of currencies
#
#
class PriceCheckRequest(Request):
    response = PriceCheckResponse
#    quantity = micromodels.DecimalField()
#    type = micromodels.CharField()
#    quality = micromodels.CharField()
#    token = micromodels.CharField()
#
    def validate(self):
        self.qty = self.require("quantity")

    def sanitize(self):
        field = DecimalField()
        field.populate(self.qty)
        self.qty = field.to_python()

    @authenticated
    def run(self):
        # have to put this here (and have api above web settings.INSTALLED_APPS
        # or you get error
        from web.models import Pool

        item = Pool.PRICECHECK(self.qty, type=self.get("type"), quality=self.get("quality"))

        response_data = {}

        #TODO: once login is working, get the Client entity from the current Authentic
        # and get the fee like this Client.transaction_fee()
        fee = config_value("web", "DEFAULT_FEE")
        # TODO: make it a DictField instance - there is no DictField class yet
        response_data["currencies"] = {
            item.currency: {
                "total": float((item.price * self.qty) + fee),
                "unit": float(item.price)
            }
        }
        response_data["quantity"] = self.qty
        response_data["type"] = item.type.code
        response_data["quality"] = item.quality
        return self.response(**response_data)

class QtyCheckResponse(Response):
    pass
#    quantity = micromodels.FloatField()
#    type = micromodels.CharField()
#    quality = micromodels.CharField()
#    currencies = micromodels.BaseField()  # dictionary of currencies

class QtyCheckRequest(Request):
    response = QtyCheckResponse

    def validate(self):
        self.price = self.require("price")

    def sanitize(self):
        field = DecimalField()
        field.populate(self.price)
        self.price = field.to_python()

    @authenticated
    def run(self):
        from web.models import Pool
        item = Pool.QTYCHECK(self.price, type=self.get("type"), quality=self.get("quality"))

        response_data = {}

        fee = config_value("web", "DEFAULT_FEE")
        response_data["currencies"] = {
            item.currency: {
                "total": float((item.price * item.quantity) + fee),
                "unit": float(item.price)
            }
        }
        response_data["quantity"] = item.quantity
        response_data["type"] = item.type.code
        response_data["quality"] = item.quality
        return self.response(**response_data)


class ListTypesResponse(Response):
    pass

class ListTypesRequest(Request):
    response = ListTypesResponse

    @authenticated
    def run(self):
        from web.models import Pool
        qs = Pool.LISTTYPES(self.get('blank'))
        types_list = []
        for (code, name) in qs:
            types_list.append(dict(code=code, name=name))
        response = self.response(types=types_list)
        #print response.types
        return response

class ListQualitiesResponse(Response):
    pass

class ListQualitiesRequest(Request):
    response = ListQualitiesResponse

    @authenticated
    def run(self):
        from web.models import Pool
        qs = Pool.LISTQUALITIES(self.get('blank'))
        types_list = []
        for (code, name) in qs:
            types_list.append(dict(code=code, name=name))
        response = self.response(types=types_list)
        return response

class TransactResponse(Response):
    pass

class TransactRequest(Request):
    response = TransactResponse

    def validate(self):
        self.qty = self.get('quantity')
        self.value = self.get('value')
        
        if not (self.qty or self.value):
            raise TransactionNeedsQtyorValException

    @authenticated
    def run(self):
        from web.models import Transaction
        client = self.user.profile.client
        if not client:
            raise ValidationException("user profile has no client attached")

        if self.qty:
            transaction = Transaction.new(client, quantity=self.qty)
        elif self.value:
            transaction = Transaction.new(client, value=self.value)
        product = transaction.product
        data = {
            "quantity": transaction.quantity,
            "type": product.type.code,
            "quality": product.quality_name,
            "currency": transaction.currency,
            "total": transaction.total,
            "transID": transaction.uuid
        }
        response = self.response(**data)
        return response


class TransactionRequest(Request):
    """Request that validates That user has ownership over transaction he wants to access
       also validates that transID is valid
    """

    def validate(self):
        from web.models import Transaction
        try:
            self.trans = Transaction.objects.get(uuid=self.require('transID'))
        except:
            raise TransactionNotExistException()
        self._validate_transaction_status()

    def _validate_transaction_status(self):
        if self.trans.is_closed:
            raise TransactionClosedException()

    def _validate_user_ownership(self):
        client = self.user.profile.client
        if not client:
            raise ValidationException("user profile has no client attached")
        if self.trans.client != client:
            raise TransactionUserNotAuthorized("Transaction Belongs to different User")
        
    @authenticated
    def run(self):
        self._validate_user_ownership()
        return self._run()

    def _run(self):
        pass

class PayResponse(Response):
    pass

class PayRequest(TransactionRequest):
    response = PayResponse

    def _run(self):
        self.trans.pay()
        product = self.trans.product
        data = {
            "quantity": self.trans.quantity,
            "type": product.type.code,
            "quality": product.quality_name,
            "currency": self.trans.currency,
            "total": self.trans.total,
            "transID": self.trans.uuid
        }
        response = self.response(**data)
        return response

class TransactInfoResponse(Response):
    pass

class TransactInfoRequest(TransactionRequest):
    response = TransactInfoResponse

    def _validate_transaction_status(self):
        """do not validate status for info"""
        pass
    
    def _run(self):
        product = self.trans.product
        data = {
            "quantity": self.trans.quantity,
            "type": product.type.code,
            "quality": product.quality_name,
            "currency": self.trans.currency,
            "total": self.trans.total,
            "transID": self.trans.uuid,
            "state": self.trans.status_name.upper(),
            "name": product.name,
            "productID": product.uuid,
        }
        response = self.response(**data)
        return response

class TransactCancelResponse(Response):
    pass

class TransactCancelRequest(Request):
    response = TransactCancelResponse

    def validate(self):
        from web.models import Transaction
        try:
            self.trans = Transaction.objects.get(uuid=self.require('transID'))
        except:
            raise TransactionNotExistException()


    @authenticated
    def run(self):
        self.trans.cancel()
        response = self.response()
        return response

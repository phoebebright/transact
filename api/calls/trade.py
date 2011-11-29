#from decimal import Decimal
from api.calls.fields import DecimalField
from decorators import authenticated
from api.calls.base import *
import api.config
from livesettings import config_value
from web.models import ProductType
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
#
#
class ListTypesResponse(Response):
#    types = micromodels.ModelCollectionField(ListTypeModel)
#    #types = micromodels.FieldCollectionField(ListTypeModel())
#    #types = micromodels.BaseField()
    pass

class ListTypesRequest(Request):
    response = ListTypesResponse
#
    def run(self):
        qs = ProductType.LISTTYPES()
        types_list = []
        for item in qs:
            types_list.append(dict(code=item.code, name=item.name))
        response = self.response(types=types_list)
        #print response.types
        return response
from decimal import Decimal
from decorators import authenticated
from api.base import *
import config
from livesettings import config_value
from web.models import ProductType

class PriceCheckResponse(Response):
    quantity = micromodels.FloatField()
    type = micromodels.CharField()
    quality = micromodels.CharField()
    currencies = micromodels.BaseField()  # dictionary of currencies


class PriceCheckRequest(Request):
    response = PriceCheckResponse
    quantity = micromodels.DecimalField()
    type = micromodels.CharField()
    quality = micromodels.CharField()
    token = micromodels.CharField()

    @authenticated
    def run(self):
        # have to put this here (and have api above web settings.INSTALLED_APPS
        # or you get error 
        from web.models import Pool

        item = Pool.price_check(self.require('quantity'), type=self.get("type"), quality=self.get("quality"))


        response = self.response()
        
        #TODO: once login is working, get the Client entity from the current Authentic
        # and get the fee like this Client.transaction_fee()
        fee = Decimal('0.25')
        # TODO: make it a DictField instance - there is no DictField class yet
        response.currencies = {
            item.currency: {
                "total": float((item.price * Decimal(str(self.quantity))) + fee),
                "unit": float(item.price)
            }
        }
        response.quantity = self.quantity
        response.type = item.type.code
        response.quality = item.quality
        return response

class ListTypeModel(micromodels.Model):
    code = micromodels.CharField()
    name = micromodels.CharField()

    def __str__(self):
        return "List Type (%s %s)" % (self.code, self.name)

    def __repr__(self):
        return self.__str__()
class ListTypesResponse(Response):
    types = micromodels.ModelCollectionField(ListTypeModel)

class ListTypesRequest(Request):
    response = ListTypesResponse

    def run(self):
        qs = ProductType.LISTTYPES()
        types_list = []
        for item in qs:
            print item
            types_list.append(ListTypeModel.from_kwargs(code=item.code, name=item.name))
        print types_list
        response = self.response(types = types_list)
        print response.types
        return response
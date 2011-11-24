from decimal import Decimal
from decorators import authenticated
from api.base import *

class PriceCheckResponse(Response):
    quantity = micromodels.FloatField()
    type = micromodels.CharField()
    quality = micromodels.CharField()
    currencies = micromodels.BaseField()  # dictionary of currencies


class PriceCheckRequest(Request):
    response = PriceCheckResponse
    quantity = micromodels.FloatField()
    type = micromodels.CharField()
    quality = micromodels.CharField()
    token = micromodels.CharField()

    @authenticated
    def run(self):
        # have to put this here (and have api above web settings.INSTALLED_APPS
        # or you get error 
        from web.models import Pool
        
        item = Pool.price_check(self.quantity)

        response = self.response()
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

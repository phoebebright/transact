from decimal import Decimal
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

    def run(self):
<<<<<<< HEAD
        kw = dict()
        if hasattr(self, "type"):
            kw['type'] = self.type
        if hasattr(self, "quality"):
            kw['quality'] = self.quality
        item = models.Pool.price_check(self.quantity, **kw)
=======
        # have to put this here (and have api above web settings.INSTALLED_APPS
        # or you get error 
        from web.models import Pool
        
        item = models.Pool.price_check(self.quantity)
>>>>>>> phoebe
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

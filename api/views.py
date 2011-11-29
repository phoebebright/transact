# Create your views here.
from django.http import HttpResponse
from api import base
from django.views.decorators.csrf import csrf_exempt
from api.exceptions import ValidationException
import json

@csrf_exempt
def call(request):
    data = request.raw_post_data
    apirequest=None
    try:
        apirequest = base.Request.dispatch(data)
        result = apirequest.run()
    except ValidationException, e:
        if apirequest:
            result = base.ErrorResponse(request=apirequest, exception=e, status="FAILED VALIDATION")
        else:
            data = json.loads(data, encoding='utf8')
            call = data.get('call')
            result = base.ErrorResponse(request=None, exception=e, status="FAILED VALIDATION", call=call)
    except Exception, e:
        result = base.ErrorResponse(request=apirequest, exception=e)
    return HttpResponse(result.get_json(),
        content_type='application/json')

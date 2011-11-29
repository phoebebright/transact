# Create your views here.
from django.http import HttpResponse
from api.calls import base
from django.views.decorators.csrf import csrf_exempt
from api.exceptions import ValidationException
import json

@csrf_exempt
def call(request):
    jsondata = request.raw_post_data
    apirequest=None
#    data = base.unwrap(jsondata)
#    apirequest = base.dispatch(data)
#    result = apirequest.run()
    try:
        data = base.unwrap(jsondata)
        apirequest = base.dispatch(data)
        result = apirequest.run()
    except ValidationException, e:
        if apirequest:
            result = base.ErrorResponse(request=apirequest, exception=e, status="FAILED VALIDATION")
        else:
            data = json.loads(jsondata, encoding='utf8')
            call = data.get('call')
            result = base.ErrorResponse(request=None, exception=e, status="FAILED VALIDATION", call=call)
    except Exception, e:
        result = base.ErrorResponse(request=apirequest, exception=e)
    return HttpResponse(result.get_json(),
        content_type='application/json')

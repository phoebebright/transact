# Create your views here.
from django.http import HttpResponse
from api import base
from django.views.decorators.csrf import csrf_exempt
from api.exceptions import ValidationException

@csrf_exempt
def call(request):
    data = request.raw_post_data
    apirequest = base.Request.dispatch(data)
    try:
        result = apirequest.run()
    except ValidationException, e:
        result = base.ErrorResponse(request=apirequest, exception=e, status="FAILED VALIDATION")
    except Exception, e:
        result = base.ErrorResponse(request=apirequest, exception=e)
    return HttpResponse(base.JsonWrapper.wrap(result.get_response()),
        content_type='application/json')

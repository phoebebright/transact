# Create your views here.
from django.http import HttpResponse
from api import base
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def call(request):
    data = request.raw_post_data
    apirequest = base.Request.dispatch(data)
    result = apirequest.run()
    return HttpResponse(base.JsonWrapper.wrap(result.get_response()),
        content_type='application/json')

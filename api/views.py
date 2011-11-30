# Create your views here.
from django.http import HttpResponse
from api.calls import base
from django.views.decorators.csrf import csrf_exempt
from api.exceptions import ValidationException
from logger import log
import uuid
import json

@csrf_exempt
def call(request):
    jsondata = request.raw_post_data
    apirequest=None
#    data = base.unwrap(jsondata)
#    apirequest = base.dispatch(data)
#    result = apirequest.run()
    callid = uuid.uuid4().hex
    try:
        data = base.unwrap(jsondata)
        log.info("API CALLID=\"%(callid)s\" REQUEST=\"%(request)s\"" % {"callid": callid, "request": data.get("call")})
        log.debug("API CALLID=\"%(callid)s\" REQUESTDATA=%(data)s" % {"callid": callid, "data": jsondata})
        apirequest = base.dispatch(data)
        result = apirequest.run()
        if result.data.get("status") == "OK":
            log.info("API CALLID=\"%(callid)s\" SUCCESS")
        else:
            log.info("API CALLID=\"%(callid)s\" FAILED ERRCODE=\"%(code)s\" STATUS=\"%(status)s\" REASON=\"%(reason)s\""
                % {"callid": callid,
                   "code": result.data.get("code"),
                   "reason": result.data.get("description"),
                   "status": result.data.get("status")
                }
            )
        log.debug("API CALLID=\"%(callid)s\" RESPONSEDATA=%(data)s" % {"callid": callid, "data": result.get_json()})
    except ValidationException, e:
        if apirequest:
            result = base.ErrorResponse(request=apirequest, exception=e, status="FAILED VALIDATION")
        else:
            data = json.loads(jsondata, encoding='utf8')
            call = data.get('call')
            result = base.ErrorResponse(request=None, exception=e, status="FAILED VALIDATION", call=call)
        log.info("API CALLID=\"%(callid)s\" FAILED ERRCODE=\"%(code)s\" STATUS=\"%(status)s\" REASON=\"%(reason)s\" REQUESTDATA=%(data)s"
                % {"callid": callid,
                   "code": result.data.get("code"),
                   "reason": result.data.get("description"),
                   "status": result.data.get("status"),
                   "data": jsondata
                }
        )
    except Exception, e:
        result = base.ErrorResponse(request=apirequest, exception=e)
        log.error("API CALLID=\"%(callid)s\" FAILED ERRCODE=\"%(code)s\" STATUS=\"%(status)s\" REASUON=\"%(reason)s\" REQUESTDATA=%(data)s"
                % {"callid": callid,
                   "code": result.data.get("code"),
                   "reason": result.data.get("description"),
                   "status": result.data.get("status"),
                   "data": jsondata
                }
        )
    return HttpResponse(result.get_json(),
        content_type='application/json')

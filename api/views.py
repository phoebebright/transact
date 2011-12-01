# Create your views here.
from django.http import HttpResponse
from api.calls import base
from django.views.decorators.csrf import csrf_exempt
from api.exceptions import ValidationException, ApiException
from logger import log
import datetime
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
        log.info("[%(now)s] API CALLID=\"%(callid)s\" REQUEST=\"%(request)s\"" % \
                 {"callid": callid, "request": data.get("call"), "now": datetime.datetime.now()})
        log.debug("[%(now)s] API CALLID=\"%(callid)s\" REQUESTDATA=%(data)s" % \
                  {"callid": callid, "data": jsondata, "now": datetime.datetime.now()})
        apirequest = base.dispatch(data)
        result = apirequest.run()
        if result.data.get("status") == "OK":
            log.info("[%(now)s] API CALLID=\"%(callid)s\" SUCCESS" % \
                {"now": datetime.datetime.now(), "callid": callid}
            )
        else:
            log.info("[%(now)s] API CALLID=\"%(callid)s\" FAILED ERRCODE=\"%(code)s\" STATUS=\"%(status)s\" REASON=\"%(reason)s\""
                % {"callid": callid,
                   "code": result.data.get("code"),
                   "reason": result.data.get("description"),
                   "status": result.data.get("status"),
                   "now": datetime.datetime.now()
                }
            )
        log.debug("[%(now)s] API CALLID=\"%(callid)s\" RESPONSEDATA=%(data)s" % \
                  {"callid": callid, "data": result.get_json(), "now": datetime.datetime.now()})
    except ApiException, e:
        result = base.ErrorResponse(request=apirequest, exception=e)
    except ValidationException, e:
        if apirequest:
            result = base.ErrorResponse(request=apirequest, exception=e, status="FAILED VALIDATION")
        else:
            data = json.loads(jsondata, encoding='utf8')
            call = data.get('call')
            result = base.ErrorResponse(request=None, exception=e, status="FAILED VALIDATION", call=call)
        log.info("[%(now)s] API CALLID=\"%(callid)s\" FAILED ERRCODE=\"%(code)s\" STATUS=\"%(status)s\" REASON=\"%(reason)s\" REQUESTDATA=%(data)s"
                % {"callid": callid,
                   "code": result.data.get("code"),
                   "reason": result.data.get("description"),
                   "status": result.data.get("status"),
                   "data": jsondata,
                   "now": datetime.datetime.now()
                }
        )
    except Exception, e:
        result = base.ErrorResponse(request=apirequest, exception=e)
        log.error("[%(now)s] API CALLID=\"%(callid)s\" FAILED ERRCODE=\"%(code)s\" STATUS=\"%(status)s\" REASUON=\"%(reason)s\" REQUESTDATA=%(data)s"
                % {"callid": callid,
                   "code": result.data.get("code"),
                   "reason": result.data.get("description"),
                   "status": result.data.get("status"),
                   "data": jsondata,
                   "now": datetime.datetime.now()
                }
        )
    return HttpResponse(result.get_json(),
        content_type='application/json')

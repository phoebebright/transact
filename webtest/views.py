#python

#libs
from django.shortcuts import render_to_response

#local
import forms as webtest_forms


def test_view(request):
    content = {}
    return render_to_response('test.html')


def price_check(request):


    form = webtest_forms.PriceCheck(initial={"call":"PRICECHECK", "token":"dummy_token", "testmode":'false'})

    return render_to_response("pricecheck.html", {"form": form})


def transact(request):
    # LUKASZ - see transact version in web/views that doesn't use APIs 
    form = webtest_forms.TransAct(initial={"call":"TRANSACT", "token":"dummy_token", "testmode":"false"})

    return render_to_response("transact.html", {"form": form})


def flight_demo(request):

    return render_to_response("flight_demo.html")
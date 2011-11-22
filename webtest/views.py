# Create your views here.
from django.shortcuts import render_to_response


def test_view(request):
    return render_to_response('test.html')
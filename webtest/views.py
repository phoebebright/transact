# Create your views here.
from django.shortcuts import render_to_response


def test_view(request):
    content = {}
    return render_to_response('test.html')
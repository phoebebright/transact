from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    url(r'^$', 'webtest.views.test_view'),
    url(r'^flight_demo/$', 'webtest.views.flight_demo'),
    url(r'^voucher_demo/$', 'webtest.views.voucher_demo'),
    url(r'^pricecheck/$', 'webtest.views.price_check'),
)
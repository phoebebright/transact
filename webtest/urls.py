from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    url(r'^$', 'webtest.views.test_view'),
    url(r'^flight_demo/$', 'webtest.views.flight_demo'),

)
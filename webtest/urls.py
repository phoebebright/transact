from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    url(r'^$', 'webtest.views.test_view'),
    url(r'^PRICECHECK/$', 'webtest.views.price_check'),
    url(r'^TRANSACT/$', 'webtest.views.transact'),
)
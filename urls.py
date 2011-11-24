import os.path

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()


urlpatterns = patterns('',
   url(r'(.+\.html)$', 'django.views.generic.simple.direct_to_template'),
   url(r'^$',  'django.views.generic.simple.direct_to_template',{'template': 'index.html'}),
)


urlpatterns += patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^webtest/', include('webtest.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^settings/', include('livesettings.urls')),
)

# for development only
if settings.DEBUG:
    urlpatterns += patterns('web.views',
    url(r'^transact/', 'transaction'),
    )
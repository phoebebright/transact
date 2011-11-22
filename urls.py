import os.path

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), "site_media/images")}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), "site_media/css")}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), "site_media/js")}),
   url(r'(.+\.html)$', 'django.views.generic.simple.direct_to_template'),
   url(r'^$',  'django.views.generic.simple.direct_to_template',{'template': 'index.html'}),
)


urlpatterns += patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^settings/', include('livesettings.urls')),
)


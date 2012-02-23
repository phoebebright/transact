import os.path

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'login.html'}, name="logout"),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', name="password_reset"),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name="password_reset_done"),
)


urlpatterns += patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^webtest/', include('webtest.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^settings/', include('livesettings.urls')),
    url(r'^contact/', include('contact_form.urls')),
)

urlpatterns += patterns('web.views',
    url(r'^client_portal/', 'client_portal'),
    )

urlpatterns += patterns('',
    url(r'(.+\.html)$', 'django.views.generic.simple.direct_to_template'),
    url(r'^$',  'django.views.generic.simple.direct_to_template',{'template': 'index.html'}),
)


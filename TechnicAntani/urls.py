from django.conf.urls import patterns, include, url
from TechnicAntani import settings

import cachebuilder.views as cachebuilder

urlpatterns = patterns('',
                       # Auth stuffs
                       url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),

                       #Home - temporarily use cache builder
                       url(r'^$', cachebuilder.index),

                       #Cache builder
                       )

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
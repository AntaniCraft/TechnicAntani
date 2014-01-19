from django.conf.urls import patterns, include, url
from TechnicAntani import settings

urlpatterns = patterns('',
                       url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
                       )

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
from django.conf.urls import patterns, include, url
from TechnicAntani import settings

urlpatterns = patterns('',
                       url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
                       )

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.BASE_DIR + "/static/"}),
    )
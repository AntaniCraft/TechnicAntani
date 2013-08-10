from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from manager.views import *
import api

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TechnicAntani.views.home', name='home'),
    # url(r'^TechnicAntani/', include('TechnicAntani.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^$', index),

    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', logout),

    url(r'^modpacks/$', modpacks_index),
    url(r'^modpacks/create/$', modpacks_create),  # TODO Create modpacks view

    url(r'^modpacks/([0-9]+?)/$', modpack),  # Shows builds
    url(r'^modpacks/([0-9]+?)/create$', modpack_build_create),  # Creates a build
    url(r'^builds/([0-9]+?)/$', modpack_build_change),
    url(r'^builds/add/([0-9]+?)/(.+?)/$', modpack_build_add),
    url(r'^builds/del/([0-9]+?)/([0-9]+?)/$', modpack_build_remove),

    url(r'^mods/$', mods_list),
    url(r'^mods/repair/$', mods_repair),
    url(r'^mods/repair/(.+?)/$', mods_repair_do),
    url(r'^mods/upload/$', mods_upload),
    url(r'^mods/submit/$', mods_submit),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api.urls)),

)

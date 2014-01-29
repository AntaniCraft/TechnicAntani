#############################################################################
#                                                                           #
#    This program is free software: you can redistribute it and/or modify   #
#    it under the terms of the GNU General Public License as published by   #
#    the Free Software Foundation, either version 3 of the License, or      #
#    (at your option) any later version.                                    #
#                                                                           #
#    This program is distributed in the hope that it will be useful,        #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#    GNU General Public License for more details.                           #
#                                                                           #
#    You should have received a copy of the GNU General Public License      #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                           #
#############################################################################

from django.conf.urls import patterns, include, url
from TechnicAntani import settings

import cachebuilder.views as cachebuilder
from api import urls as api_urls

urlpatterns = patterns('',
                       # Auth stuffs
                       url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),

                       # TechnicSolder API
                       url(r'^api/', include(api_urls)),
                       url(r'^apikeys$', 'api.views.apikeys_manage'),

                       # Home - temporarily use cache builder
                       url(r'^$', cachebuilder.index),

                       # Cache builder
                       url(r'^cache/$', cachebuilder.index),
                       url(r'^cache/rebuildall$', cachebuilder.build_all_caches),

                       url(r'^modpack/create$', cachebuilder.create_modpack),
                       url(r'^modpack/modrepo$', cachebuilder.update_modrepo),

                       url(r'^hooks/github$', cachebuilder.github_hook, name="github")
                       )

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
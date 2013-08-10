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

from django.conf.urls import patterns, url
from api.views import *

urls = patterns('',
    url(r'^$', index),

    url(r'^modpack/$', modpack_list),
    url(r'^modpack/(.+?)/(.+?)/$', modpack_build),
    url(r'^modpack/(.+?)/$', modpack),

    url(r'^verify/$', verify),
    url(r'^verify/(.+?)/$', verify),

    url(r'^mod/$', mod),
    url(r'^mod/(.+?)/$', mod)
)
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

from django.contrib import admin
from models import *


class AntaniAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ("key", "value"),
            "description": "This is the list of required settings keys for TechnicAntani<br><ul>"
                           "<li>apikey - Technic Platform API key</li>"
                           "<li>repopath - Path to mod repo</li>"
                           "<li>repourl - URL to where mod repo is served</li></ul>"
                           "<p>Examples:<ul>"
                           "<li><b>key</b> - apikey</li>"
                           "<li><b>value</b> - 7b743f4ac638f4ccb4e311f0389e5f84</li><br>"
                           "<li><b>key</b> - repopath</li>"
                           "<li><b>value</b> - /var/technicantani</li><br>"
                           "<li><b>key</b> - repourl</li>"
                           "<li><b>value</b> - http://repo.example.com/</li>"
                           "</ul></p>"

        }),
    )

admin.site.register(FileCache)
admin.site.register(Modpack)
admin.site.register(Build)
admin.site.register(AntaniSetting, AntaniAdmin)
admin.site.register(McVersion)

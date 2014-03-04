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

from celery import shared_task
from server.models import *
from cachebuilder.pack_manager import *
from cachebuilder.mod_manager import *


@shared_task
def build_all_server():
    mm = ModManager()
    servers = Server.objects.all()

    for server in servers:
        versions = VersionCache.objects.filter(modpack=server.modpack)
        for version in versions:
            for mod in version.mods:
                physmod = mm.get_mod(mod.slug)
                physmod.versions[mod.versions]
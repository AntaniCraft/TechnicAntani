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
from time import sleep


@shared_task
def rebuild_all_caches():
    """
    WIPES and recreates all caches. Takes forever if there are many things to build
    """
    return True

@shared_task
def update_modpack(repo):
    """
    Updates the repo (the param is the dir|slug). It's just a git pull reporting True if there are updates
    """
    return True

@shared_task
def update_mods():
    """
    Updates the mod repo. Returns True if there are updates (pull not empty)
    """
    return True
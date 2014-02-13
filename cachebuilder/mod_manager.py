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

# This will be SLOW. As HELL.

from os import path, walk
from TechnicAntani.settings import MODREPO_DIR
import json


class Mod:
    def __init__(self, dirname):
        # TODO sanitizing and syntax check
        versionf = open(path.join(dirname, "mod.json"))
        obj = json.load(versionf)
        versionf.close()
        self.slug = dirname.split(path.sep)[-1]
        self.name = obj["name"]
        self.description = obj["description"]
        self.author = obj["author"]
        self.url = obj["url"]
        self.type = obj["type"]  # mod, prepackaged
        self.versions = {}

        for version in obj['versions'].keys():
            self.versions[version] = {
                'file': obj["versions"][version]['file'],
                'mcvers': obj["versions"][version]['minecraft']
            }


class ModManager:
    def __init__(self):
        self.fspath = MODREPO_DIR
        self.mods = []
        for root, dirs, files in walk(self.fspath):
            if "mod.json" in files:
                self.mods.append(Mod(root))

    def get_mod(self, slug):
        for mod in self.mods:
            if mod.slug == slug:
                return mod
        return None
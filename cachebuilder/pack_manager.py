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

from TechnicAntani.settings import MODPACKPATH
import os.path as path
from os import listdir
import json


class Modpack:
    def __init__(self, name):
        self.name = name
        mainkeys = [
            'description', 'slug', 'url'
        ]
        versionkeys = [
            'recommended', 'latest',
            'mcversion', 'forgever'
        ]
        modvers = [
            'version'
        ]
        meta = open(path.join(MODPACKPATH, name, "modpack.json"))
        obj = json.load(meta)
        meta.close()
        for mkey in mainkeys:
            setattr(self, mkey, obj[mkey])
            self.versions = {}
            for version in obj['versions'].keys():
                version_obj = {}
                for vkey in versionkeys:
                    version_obj[vkey] = obj['versions'][version][vkey]
                    version_obj['mods'] = {}
                    for mod in obj['versions'][version]['mods'].keys():
                        version_obj['mods'][mod] = obj['versions'][version]['mods'][mod]
                self.versions[version] = version_obj

    def get_background(self):
        return path.join(MODPACKPATH,self.name,"assets","background.jpg")
    def get_logo(self):
        return path.join(MODPACKPATH,self.name,"assets","logo.png")
    def get_icon(self):
        return path.join(MODPACKPATH,self.name,"assets","icon.png")

class ModpackManager:
    """
    Lazy loader for modpack data
    """
    packs = {}

    def __init__(self):
        """
        Initialize in a VERY lazy way
        """
        for dirf in listdir(MODPACKPATH):
            if path.isdir(dirf) and not dirf.startswith("."):
                self.packs[dirf] = None

    def get_pack(self,name):
        """
        Loads the Modpack data or gets it from the cache
        throws IOException if it can't load the json the first time
        """
        try:
            ret = self.packs[name]
        except KeyError:
            if name in self.packs.keys():
                # It may fail
                self.packs[name] = Modpack(name)
                ret = self.packs[name]
        return ret

    def list_packs(self):
        return self.packs.keys()
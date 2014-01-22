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

from os import path, walk, mkdir
from shutil import move
import hashlib
from configparser import ConfigParser
from TechnicAntani.settings import MODREPO_DIR
import json

class Mod:
    def __init__(self, dirname):
        self.slug = dirname.split(path.sep)[-1]
        c = ConfigParser()
        c.read(dirname+path.sep+"Metadata")
        self.name = c.get("Mod", "Name")
        self.description = c.get("Mod", "Description")
        self.author = c.get("Mod", "Author")
        self.url = c.get("Mod", "Url")
        self.versions = {}
        versionf = open(path.join(dirname,"versions.json"))
        obj = json.load(versionf)
        versionf.close()
        for mcver in obj.keys():
            self.versions[mcver] = []
            for version in obj[mcver].keys():
                modver = {
                    'version': version,
                    'file': obj[mcver][version]
                }
                self.versions[mcver].append(modver)


class ModManager:
    def __init__(self):
        self.fspath = MODREPO_DIR
        self.mods = []
        for root, dirs, files in walk(self.fspath):
            if "Metadata" in files:
                self.mods.append(Mod(root))


def checksum_file(dirpath):
    afile = open(dirpath, "rb")
    hasher = hashlib.md5()
    buf = afile.read(65536)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(65536)
    return hasher.hexdigest()
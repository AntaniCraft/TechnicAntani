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

from models import AntaniSetting
from os import path, walk, mkdir
from shutil import move
import tempfile, zipfile, json, hashlib
from ConfigParser import ConfigParser


class Mod:
    def __init__(self, dir, files):
        self.slug = dir.split(path.sep)[-1]
        c = ConfigParser()
        c.read(dir+path.sep+"Metadata")
        self.name = c.get("Mod", "Name")
        self.description = c.get("Mod", "Description")
        self.author = c.get("Mod", "Author")
        self.url = c.get("Mod", "Url")
        self.versions = {}
        for f in files:
            if f == "Metadata":
                continue
            pieces = f.split("-")
            if pieces[0] == self.slug:
                if not pieces[1] in self.versions:
                    self.versions[pieces[1]] = []
                self.versions[pieces[1]].append(pieces[2].replace(".zip", ""))


class ModType:
    CONFIGPACK = 1
    COREMOD = 2
    NORMAL = 3
    PREPACKAGED = 4


class ModManager:
    def __init__(self):
        self.fspath = AntaniSetting.objects.get(key="repopath")
        self.mods = []
        for root, dirs, files in walk(self.fspath.value):
            if "Metadata" in files:
                self.mods.append(Mod(root, files))

    def add_mod(self, slug, name, description, author, url, mcver, ver, tempfile):
        slugdir = self.fspath.value + path.sep + "mods" + path.sep + slug
        if not path.exists(slugdir):
            mkdir(slugdir)
        move(tempfile, self.fspath.value + path.sep + slug + path.sep + slug + "-" + mcver + "-" + ver + ".zip")
        c = ConfigParser()
        c.add_section("Mod")
        c.set("Mod", "Name", name)
        c.set("Mod", "Description", description)
        c.set("Mod", "Author", author)
        c.set("Mod", "Url", url)
        with open(slugdir + path.sep + "Metadata", "w") as fp:
            c.write(fp)


class RawMod:

    def __init__(self, rawpath, type=ModType.NORMAL):
        self.jarpath = rawpath
        self.type = type
        self.modid = ""
        self.name = ""
        self.desc = ""
        self.ver = ""
        self.authors = ""
        self.url = ""
        self.mcversion = ""

    def readMetadata(self):
        try:
            z = zipfile.ZipFile(self.jarpath)
            f = z.open("mcmod.info")
            str = f.read()
            obj = json.loads(str)
            z.close()
            modinfo = obj[0]
            self.modid = modinfo["modid"]
            self.name = modinfo["name"]
            self.desc = modinfo["description"]
            self.ver = modinfo["version"]
            self.url = modinfo["url"]
            self.authors = ",".join(modinfo["authors"])
            self.mcversion = modinfo["mcversion"]
        except KeyError: #YOLO
            pass

    def pack(self):
        tmpfile = tempfile.mktemp(suffix=".zip")
        if self.type == ModType.PREPACKAGED:
            return self.jarpath
        zpack = zipfile.ZipFile(tmpfile, "w")
        name = path.basename(self.jarpath)
        zipname = ""
        if self.type == ModType.NORMAL:
            zipname = "mods/" + name
        elif self.type == ModType.CONFIGPACK:
            zipname = "config/" + name
        else:
            zipname = "coremods/" + name

        zpack.write(self.jarpath, zipname)
        zpack.close()
        return tmpfile

def checksum_file(path):
    afile = open(path, "rb")
    hasher = hashlib.md5()
    buf = afile.read(65536)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(65536)
    return hasher.hexdigest()
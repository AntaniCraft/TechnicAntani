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
import tempfile
import zipfile
import json
import hashlib
from configparser import ConfigParser
from TechnicAntani.settings import MODREPO_DIR


class Mod:
    def __init__(self, dirname, files):
        self.slug = dirname.split(path.sep)[-1]
        c = ConfigParser()
        c.read(dirname+path.sep+"Metadata")
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
        self.fspath = MODREPO_DIR
        self.mods = []
        for root, dirs, files in walk(self.fspath):
            if "Metadata" in files:
                self.mods.append(Mod(root, files))

    def add_mod(self, slug, name, description, author, url, mcver, ver, tmpfile):
        slugdir = self.fspath + path.sep + "mods"
        if not path.exists(slugdir):
            mkdir(slugdir)
        slugdir += path.sep + slug
        if not path.exists(slugdir):
            mkdir(slugdir)
        move(tmpfile,
             self.fspath + path.sep + 'mods' + path.sep + slug + path.sep + slug + "-" + mcver + "-" + ver + ".zip"
             )
        c = ConfigParser()
        c.add_section("Mod")
        c.set("Mod", "Name", name)
        c.set("Mod", "Description", description)
        c.set("Mod", "Author", author)
        c.set("Mod", "Url", url)
        with open(slugdir + path.sep + "Metadata", "w") as fp:
            c.write(fp)


class RawMod:

    def __init__(self, rawpath, modtype=ModType.NORMAL):
        self.jarpath = rawpath
        self.type = modtype
        self.modid = ""
        self.name = ""
        self.desc = ""
        self.ver = ""
        self.authors = ""
        self.url = ""
        self.mcversion = ""

    def read_metadata(self):
        # TODO Rewrite this shit
        z = zipfile.ZipFile(self.jarpath)
        str = ""
        try:
            f = z.open("mcmod.info")
            str = f.read()
        except KeyError: #YOLO
            return
        obj = json.loads(str)
        z.close()
        try:
            modinfo = obj[0]
            self.modid = modinfo["modid"]
        except Exception: #YOLO
            pass
        try:
            self.name = modinfo["name"]
        except Exception: #YOLO
            pass
        try:
            self.desc = modinfo["description"]
        except Exception: #YOLO
            pass
        try:
            self.ver = modinfo["version"]
        except Exception: #YOLO
            pass
        try:
            self.url = modinfo["url"]
        except Exception: #YOLO
            pass
        try:
            self.authors = ",".join(modinfo["authors"])
        except Exception: #YOLO
            pass
        try:
            self.mcversion = modinfo["mcversion"]
        except Exception: #YOLO
            pass

    def pack(self, fname):
        tmpfile = tempfile.mktemp(suffix=".zip")
        if self.type == ModType.PREPACKAGED:
            return self.jarpath
        zpack = zipfile.ZipFile(tmpfile, "w")
        name = fname + ".jar"
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


def checksum_file(dirpath):
    afile = open(dirpath, "rb")
    hasher = hashlib.md5()
    buf = afile.read(65536)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(65536)
    return hasher.hexdigest()
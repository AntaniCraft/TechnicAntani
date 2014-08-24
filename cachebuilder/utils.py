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

# This file has the main actions performed by the scripts.
# It's here the magic happens

from api.models import ModCache, ModInfoCache
from cachebuilder.mod_manager import ModManager
from TechnicAntani.antanisettings import MODBUILD_DIR, MODPACKPATH, MODREPO_DIR
from urllib.request import urlretrieve
import os
import zipfile
import hashlib
import logging
import re
import uuid
import shutil

filename_regex = re.compile("[^/]+\.\w{3}")
cleaner_regex = re.compile("\W+")


def sanitize_path(ugly):
    return re.sub(cleaner_regex, '', str(ugly))


def get_mod_info_by_name(name):
    return ModInfoCache.objects.all().filter(name=name).first()


def checksum_file(dirpath):
    afile = open(dirpath, "rb")
    hasher = hashlib.md5()
    buf = afile.read(65536)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(65536)
    return hasher.hexdigest()


def fetch_forge(version, mcver):
    """
    Fetches forge from files.minecraftforge.org and returns the
    path it was saved into
    """
    logging.getLogger("fetch_forge").info("Fetching forge v" + version)
    url = "http://files.minecraftforge.net/maven/net/minecraftforge/forge/" + mcver + "-" + version + "/forge-" + mcver + "-" + version + "-universal.jar"
    (tpath, message) = urlretrieve(url)
    if message.get_content_type() != "application/java-archive":
        logging.getLogger("fetch_forge").error("Cannot find url " + url)
        return None
    return tpath


def build_forge(version, mcver):
    """
    Builds or returns a ModCache if already in cache
    """
    forge = ModCache.objects.all().filter(modInfo__name="forge").filter(version=version).first()
    if not forge is None:
        return forge
    localfile = fetch_forge(version, mcver)
    built = os.path.join(MODBUILD_DIR, "forge_"+sanitize_path(mcver)+"_"+sanitize_path(version)+".zip")
    with zipfile.ZipFile(built, "w", zipfile.ZIP_DEFLATED) as zipp1:
        zipp1.write(localfile, "bin/modpack.jar")
    os.unlink(localfile)  # We don't need it any more
    mi = get_mod_info_by_name("forge")
    if mi is None:
        mi = ModInfoCache()
        mi.name = "forge"
        mi.author = "cpw,LexManos and MANY others"
        mi.description = "Forge auto-assembled by TechnicAntani"
        mi.link = "http://files.minecraftforge.net"
        mi.pretty_name = "Minecraft Forge"
        mi.save()

    mc = ModCache()
    mc.modInfo = mi
    mc.md5 = checksum_file(built)
    mc.localpath = built
    mc.version = version
    mc.save()
    return mc


def build_config(packname, version):
    """
    Build a config zip from the package name.
    """
    cfg = ModCache.objects.all().filter(modInfo__name=packname+"_config").filter(version=version).first()
    if not cfg is None:
        return cfg
    cp = os.path.join(MODPACKPATH, packname, "config")
    cz = os.path.join(MODBUILD_DIR, sanitize_path(packname) + "_" + sanitize_path(version) + "_config.zip")
    with zipfile.ZipFile(cz, "w", zipfile.ZIP_DEFLATED) as zipp1:
        rootlen = len(cp)
        for base, dirs, files in os.walk(cp):
            for ifile in files:
                fn = os.path.join(base, ifile)
                zipp1.write(fn, "config" + fn[rootlen:])
    mi = get_mod_info_by_name(packname + "_config")
    if mi is None:
        mi = ModInfoCache()
        mi.name = packname + "_config"
        mi.author = "TechnicAntani"
        mi.description = "Config for " + packname + " auto-assembled by TechnicAntani"
        mi.link = "http://github.com/AntaniCraft/TechnicAntani"
        mi.pretty_name = packname + "'s Config"
        mi.save()

    mc = ModCache()
    mc.modInfo = mi
    mc.md5 = checksum_file(cz)
    mc.localpath = cz
    mc.version = version
    mc.save()
    return mc


def build_mod(name, version, mm):
    """
    Builds the mod into the cache. Modmanager is passed for performance reasons
    """
    log = logging.getLogger("build_mod")
    mc = ModCache.objects.all().filter(modInfo__name=name).filter(version=version).first()
    if not mc is None:
        return mc

    mod = mm.get_mod(name)
    if not version in mod.versions.keys():
        log.error("There is no mod " + name + " version " + version)
        return None

    mz = os.path.join(MODBUILD_DIR, sanitize_path(mod.slug) + "_" + sanitize_path(uuid.uuid4()) + ".zip")
    log.info("Will be saved in " + mz)
    if mod.type == "mod":
        with zipfile.ZipFile(mz, "w", zipfile.ZIP_DEFLATED) as zip:
            fnm = re.search(filename_regex, mod.versions[version]["file"])
            fn = mod.versions[version]["file"][fnm.start():fnm.end()]
            zip.write(os.path.join(MODREPO_DIR, mod.slug, fn), os.path.join("mods", fn))
    if mod.type == "prepackaged":
        fn = os.path.basename(mod.versions[version]["file"])
        shutil.copy(os.path.join(MODREPO_DIR, sanitize_path(mod.name), fn), mz)

    mi = get_mod_info_by_name(name)
    if mi is None:
        mi = ModInfoCache()
        mi.author = mod.author
        mi.description = mod.description
        mi.link = mod.url
        mi.pretty_name = mod.name
        mi.name = name
        mi.save()
    mv = ModCache()
    mv.version = version
    mv.modInfo = mi
    mv.localpath = mz
    mv.md5 = checksum_file(mz)
    mv.save()
    return mv


def delete_built():
    for base, dirs, files in os.walk(MODBUILD_DIR):
        for ifile in files:
            os.unlink(os.path.join(base, ifile))
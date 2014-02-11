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
from cachebuilder.mod_manager import *
from cachebuilder.pack_manager import *
from api.models import *
from os import system, path
from shutil import copy
from urllib.request import urlretrieve
from subprocess import Popen, PIPE
import zipfile
import re
import uuid

cleaner_regex = re.compile("\W+")
filename_regex = re.compile("[a-zA-Z0-9_-]+\.\w{3}")


@shared_task
def build_all_caches():
    """
    Updates all caches. Takes forever if there are many things to build
    throws FileNotFoundError if a mod we don't track is requested
    """
    # Diff mods first
    mm = ModManager()  # GASP!
    pm = ModpackManager()
    for pack in pm.list_packs():
        p = pm.get_pack(pack)
        pc = ModpackCache.objects.all().filter(slug=pack)
        if len(pc) == 0:
            # Skip. Not a valid pack
            if p is None:
                continue
            pc = ModpackCache()
            pc.slug = pack
            pc.name = p.name
            pc.description = p.description
            pc.url = p.url
        else:
            pc = pc[0]  # Fetch first
        # Refresh md5 - just in case
        pc.background_md5 = checksum_file(p.get_background())
        pc.logo_md5 = checksum_file(p.get_logo())
        pc.icon_md5 = checksum_file(p.get_icon())
        pc.save()
        # packvers=VersionCache.objects.filter(modpack=pc)
        for packver in p.versions.keys():
            cachedver = VersionCache.objects.all().filter(modpack=pc, version=packver)
            if len(cachedver) == 0:
                cachedver = VersionCache()
                cachedver.forgever = p.versions[packver]['forgever']
                cachedver.latest = p.versions[packver]['latest']
                cachedver.recommended = p.versions[packver]['recommended']
                cachedver.mcversion = p.versions[packver]['mcversion']
                cachedver.mcversion_checksum = _get_mc_md5(p.versions[packver]['mcversion'])
                cachedver.modpack = pc
                cachedver.save()
            else:
                cachedver = cachedver[0]
                # Package forge as modpack.jar. We have to see what to do in the future.
                if not cachedver.forgever == "":
                    forgezip = path.join(MODBUILD_DIR, pc.name + "_forge.zip")
                    with zipfile.ZipFile(configzip, "w", zipfile.ZIP_DEFLATED) as zipp1:
                        (tpath, message) = urlretrieve("http://files.minecraftforge.net/maven/net/minecraftforge/forge/"
                                                       + cachedver.mcversion + "-"
                                                       + cachedver.forgever +
                                                       +"/forge-"+ cachedver.mcversion
                                                       + "-" + cachedver.forgever + "-universal.jar")
                        if message.get_content_type() != "application/java-archive":
                            raise FileNotFoundError
                        zipp1.write(tpath, "bin/modpack.jar")
                    forgecache = ModInfoCache.objects.all.filter(name="Forge", version=cachedver.forgever)
                    if len(forgecache) == 0:
                        forgecache = ModInfoCache()
                        # Shameless Self Advert
                        forgecache.author = "cpw,LexManos and MANY others"
                        forgecache.description = "Forge auto-assembled by TechnicAntani"
                        forgecache.link = "http://files.minecraftforge.net"
                        forgecache.pretty_name = "Forge"
                        forgecache.save()
                    else:
                        forgecache = forgecache[0]

                    fvcache = ModCache()
                    fvcache.localpath = forgezip
                    fvcache.md5 = checksum_file(forgezip)
                    fvcache.modInfo = forgecache # Fixme refactor modInfo
                    fvcache.version = cachedver.forgever
                    fvcache.save()
                    cachedver.mods.add(fvcache)

                # Package the zippone with current config in git
                configzip = path.join(MODBUILD_DIR, pc.name+"_config.zip")
                with zipfile.ZipFile(configzip, "w", zipfile.ZIP_DEFLATED) as zipp1:
                    root = path.join(MODPACKPATH, pack, "config")
                    rootlen = len(root)
                    for base, dirs, files in os.walk(root):
                        for ifile in files:
                            fn = path.join(base, ifile)
                            zipp1.write(fn, path.join("config", fn[rootlen:]))
                confname = pack + "Config"
                confcache = ModInfoCache.objects.get(name=confname)
                if confcache is None:
                    confcache = ModInfoCache()
                    # Shameless Self Advert
                    confcache.author = "TechnicAntani"
                    confcache.description = "Configuration generated from git sources."
                    confcache.link = "http://github.com/AntaniCraft/TechnicAntani"
                    confcache.pretty_name = pack + "'s Configuration"
                    confcache.save()
                confvcache = ModCache()
                confvcache.localpath = configzip
                confvcache.md5 = checksum_file(configzip)
                confvcache.modInfo = confcache  # Fixme refactor modInfo
                confvcache.version = packver
                confvcache.save()
                cachedver.mods.add(confvcache)

            for mod in p.versions[packver]['mods'].keys():
                mc = ModInfoCache.objects.get(name=mod)
                cachedmod = None
                mr = mm.get_mod(mod)
                if mr is None:
                    raise FileNotFoundError()
                if not mc is None:
                    cachedmod = ModCache.objects.get(modInfo=mc)
                if cachedmod is None:
                    cachedmod = _build_cache(mr, p.versions[packver]['mods'][mod])
                cachedver.mods.add(cachedmod)
    return True


@shared_task
def update_modpack(repo):
    """
    Updates the repo (the param is the dir|slug). It's just a git pull reporting True if there are updates
    """
    output = Popen([GIT_EXEC, "pull"], stdout=PIPE, cwd=path.join(MODPACKPATH, repo)).communicate()[0]
    if "No updates found" in output:
        return False
    return True


@shared_task
def clone_modpack(gitrepo, targetdir):
    """
    Clones git repo in a new directory
    """
    cleandir = _sanitize_path(targetdir)
    if path.isdir(path.join(MODPACKPATH, cleandir)):
        print('NOPE. There\'s a dir named like this.')
    system(GIT_EXEC + ' clone "' + gitrepo + '" ' + path.join(MODPACKPATH, cleandir))
    print("Repo created. Building")
    build_all_caches()

@shared_task
def update_mods():
    """
    Updates the mod repo. Returns True if there are updates (pull not empty)
    """
    output = Popen([GIT_EXEC, "pull"], stdout=PIPE, cwd=MODREPO_DIR).communicate()[0]
    if "No updates found" in output:
        return False
    return True


@shared_task
def change_mod_repo(newrepo):
    if path.isdir(path.join(MODREPO_DIR, '.git')):
        system('rm -rf ' + MODREPO_DIR + '/*')
        system('rm -rf ' + MODREPO_DIR + '/.??*')
    system(GIT_EXEC + ' clone "' + newrepo + '" ' + MODREPO_DIR)


def _get_mc_md5(mcver):
    return ""  # TODO get an answer on IRC -> WTF


def _build_cache(mod, version):
    info_cache = ModInfoCache.objects.get(name=mod.name)
    if info_cache is None:
        info_cache = ModInfoCache()
        info_cache.author = mod.author
        info_cache.description = mod.description
        info_cache.link = mod.url
        info_cache.pretty_name = mod.name
        info_cache.save()
    tpath = path.join(MODBUILD_DIR, _sanitize_path(mod.name) + "_" + _sanitize_path(uuid.uuid4()) + ".zip")
    if mod.type == "mod":
        with zipfile.ZipFile(tpath, "w", zipfile.ZIP_DEFLATED) as zip:
            fnm = re.search(filename_regex, mod.versions[version]["file"])
            fn = mod.versions[version]["file"][fnm.start():fnm.end()]
            zip.write(fn, path.join("mods", fn))
    if mod.type == "prepackaged":
        fn = path.basename(mod.versions[version]["file"])
        copy(path.join(MODREPO_DIR,_sanitize_path(mod.name),fn), tpath)
    cache = ModCache()
    cache.version = version
    cache.modInfo = info_cache
    cache.localpath = tpath
    cache.md5 = checksum_file(tpath)
    cache.save()
    return cache


def _sanitize_path(ugly):
    return re.sub(cleaner_regex,'', ugly)
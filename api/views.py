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

from django.http import HttpResponse
from manager.models import *


import json
import re


def fucking_php_escape(str):
    strout = re.sub("([/])", r'\\\1', str)
    return strout


def index(request):
    return HttpResponse('{"api":"TechnicSolder","version":"0.3","stream":"DEV","extraver":"0.1antani"}')


def modpack_list(request):
    result = {}
    result['modpacks'] ={}
    for modpack in Modpack.objects.all():
        result['modpacks'][modpack.slug] = modpack.name
    result['mirror_url'] = fucking_php_escape(AntaniSetting.objects.get(key="repourl").value)
    return HttpResponse(json.dumps(result).replace("\\\\","\\"))


def modpack(request, slug):
    result = {}
    m = Modpack.objects.get(slug=slug)
    result["name"] = m.slug
    result["display_name"] = m.name
    result["url"] = m.url
    result["logo_md5"] = m.logo_md5
    result["icon_md5"] = m.icon_md5
    result["background_md5"] = m.background_md5
    result["builds"] = []
    for b in Build.objects.all().filter(modpack=m):
        result["builds"].append(b.version)
        if b.recommended:
            result["recommended"] = b.version
        if b.latest:
            result["latest"] = b.version

    return HttpResponse(json.dumps(result).replace("\\\\","\\"))


def modpack_build(request, slug, build):
    result = {}
    m = Modpack.objects.get(slug=slug)
    b = Build.objects.all().filter(modpack=m).filter(version=build)[0]
    result["minecraft"] = b.mcversion.version
    result["minecraft_md5"] = b.mcversion.checksum
    result["forge"] = None
    result["mods"] = []
    for mod in b.mods.all():
        m = {
            "name": mod.modInfo.name,
            "version": mod.version,
            "md5": mod.checksum,
            "url": fucking_php_escape(mod.getUrl()),
        }
        result["mods"].append(m)
    return HttpResponse(json.dumps(result).replace("\\\\","\\"))


def verify(request, apikey = None):
    result = {}
    localkey = AntaniSetting.objects.get(key="apikey").value
    if apikey is None:
        result["error"] = "No API key provided."
    elif apikey==localkey:
        result["valid"] = "Key validated."
    else:
        result["error"] = "Invalid key provided."
    return HttpResponse(json.dumps(result))

def mod(request, modSlug=None):
    if modSlug is None:
        result = {
            'error': 'No mod selected.'
        }
        return HttpResponse(json.dumps(result))
    m = ModCache.objects.get(name=modSlug)
    fcs = FileCache.objects.filter(modInfo=m)
    result = {
        'name': m.name,
        'pretty_name': m.pretty_name,
        'author': m.author,
        'description': m.description,
        'link': fucking_php_escape(m.link),
        'versions': []
    }
    for f in fcs:
        result["versions"].append(f.version)
    return HttpResponse(json.dumps(result).replace("\\\\","\\"))
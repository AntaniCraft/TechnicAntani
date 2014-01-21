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

from django.db import models
from TechnicAntani.antanisettings import *


class ApiKey(models.Model):
    key = models.CharField(max_length=64)
    description = models.TextField()


class ModpackCache(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    url = models.URLField()
    logo_md5 = models.CharField(max_length=32)
    icon_md5 = models.CharField(max_length=32)
    background_md5 = models.CharField(max_length=32)


class ModInfoCache(models.Model):
    name = models.CharField(max_length=255)
    pretty_name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    link = models.CharField(max_length=255)


class ModCache(models.Model):
    localpath = models.CharField(max_length=255)
    version = models.CharField(max_length=32)
    md5 = models.CharField(max_length=32)
    modInfo = models.ForeignKey(ModInfoCache)

    def get_url(self, req):
        mirror_url = SERVE_DOMAIN + SERVE_URL if (SERVE_DOMAIN != "") else "http://" + req.get_host() + SERVE_URL
        return mirror_url + "/" + self.localpath


class VersionsCache(models.Model):
    version = models.CharField(max_length=32)
    recommended = models.BooleanField()
    latest = models.BooleanField()
    mcversion = models.CharField(max_length=32)
    mcversion_checksum = models.CharField(max_length=32)
    forgever = models.CharField(max_length=64)
    modpack = models.ForeignKey(ModpackCache)
    mods = models.ManyToManyField(ModCache)
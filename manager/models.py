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


class McVersion(models.Model):
    version = models.CharField(max_length=10, unique=True)
    checksum = models.CharField(max_length=32)

    def __unicode__(self):
        return self.version


class Modpack(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the modpack")
    slug = models.SlugField(max_length=30, help_text="Identifier for the modpack. Only english letters and underscore (_"
                                                     ") is permitted")
    url = models.URLField(help_text="Home page for the modpack")
    logo_md5 = models.CharField(max_length=32)
    icon_md5 = models.CharField(max_length=32)
    background_md5 = models.CharField(max_length=32)

    def __unicode__(self):
        return self.slug

    def getIconUrl(self):
        return AntaniSetting.objects.get(key="repourl").value + "/" + self.slug + "/resources/icon.png"

    def getLogoUrl(self):
        return AntaniSetting.objects.get(key="repourl").value + "/" + self.slug + "/resources/logo_180.png"



class Build(models.Model):
    version = models.CharField(max_length=20, help_text="Build version")
    mods = models.ManyToManyField('FileCache', null=True)
    modpack = models.ForeignKey('Modpack')
    mcversion = models.ForeignKey("McVersion", help_text="Version of minecraft this goes with")
    recommended = models.BooleanField()
    latest = models.BooleanField()



class ModCache(models.Model):
    """
    Just a cache for contents on disk for performance.
    All these are deducted from the filesystem when a
    modpack/modpack build is created

    Careful: can be invalid
    """
    name = models.SlugField(max_length=60, help_text="Slug", unique=True)
    pretty_name = models.CharField(max_length=255, help_text="Name of the mod")
    author = models.CharField(max_length=255, help_text="Name of the author(s)")
    description = models.TextField(help_text="Description for the mod")
    link = models.URLField(help_text="Link to the site of the mod")
    

class FileCache(models.Model):
    """
    A cache for files in use.
    A repair tool can walk through this and check inconsistencies
    with the File System

    Careful: can be invalid
    """
    version = models.CharField(max_length=32, help_text="Mod version")
    mcversion = models.ForeignKey("McVersion", help_text="Version of minecraft this goes with")
    file = models.FilePathField(unique=True, help_text="Path to the mod zip")
    checksum = models.CharField(max_length=32, help_text="md5 checksum of the file")
    modInfo = models.ForeignKey("ModCache")

    def getUrl(self):
        path=AntaniSetting.objects.get(key="repourl").value
        return path + "/mods/" + self.modInfo.name + "/" + self.file + ".zip"


class AntaniSetting(models.Model):
    """
    Known fields
        apikey - technic platform api key
        repopath - absolute path to mod repository
        repourl - root url at which repo is served
    """
    key = models.CharField(max_length=32, unique=True, db_index=True)
    value = models.CharField(max_length=255)

    def __unicode__(self):
        return self.key+": "+self.value

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

from django import template
from manager.models import Build, Modpack, AntaniSetting
from os import path, listdir

register = template.Library()


class ModpackVersions(template.Node):
    def __init__(self, modpack):
        self.modpack = template.Variable(modpack)

    def writeList(self, modpack):
        buf = "<ul>"
        m = Modpack.objects.get(pk=modpack.id)
        builds= Build.objects.filter(modpack=m)
        if len(builds)==0:
            return "<span>No builds yet</span>"
        for build in builds:
            buf += "<li><a href=\"/builds/"
            buf += str(build.id) + "/\">" + build.version + "</a></li>"
        buf += "</ul>"
        return buf

    def render(self, context):
        try:
            resolved = self.modpack.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        return self.writeList(resolved)


@register.tag
def modpack_versions(parser, token):
    try:
        tag_name, modpack = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires an argument" % token.contents.split()[0])
    return ModpackVersions(modpack)

@register.filter()
def mod_versions(value, arg):
    mpath = AntaniSetting.objects.get(key="repopath").value + path.sep + value.slug
    versions = []
    for f in listdir(mpath):
        if f != "Metadata":
            pieces = f.split("-")
            if pieces[1] == arg:
                app = pieces[2].replace(".zip", "")
                versions.append(app)

    return versions

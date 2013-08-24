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
        buf = ""
        m = Modpack.objects.get(pk=modpack.id)
        builds= Build.objects.filter(modpack=m)
        if len(builds) == 0:
            return "<h4 class='warning'>No builds yet</h4>"
        for build in builds:
            cls = "label"
            if build.recommended:
                cls = "label label-success"
            elif build.latest:
                cls = "label label-warning"
            if build.recommended and build.latest:
                cls = "label label-primary"
            buf += "<a href=\"/builds/"
            buf += str(build.id) + "/\" class=\""+cls+"\">" + build.version + "</a></span>"
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
    mpath = AntaniSetting.objects.get(key="repopath").value + path.sep + "mods" + path.sep + value.slug
    versions = []
    files = listdir(mpath)
    if "Metadata" in files:
        for f in files:
            if f != "Metadata":
                pieces = f.split("-")
                if len(pieces) == 3 and pieces[1] == arg:
                    app = pieces[2].replace(".zip", "")
                    versions.append(app)

    return versions

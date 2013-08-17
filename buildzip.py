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

from __future__ import print_function
import sys
import os
import zipfile
from os import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TechnicAntani.settings")
# here be dragons (aka django)
from manager.models import *


def main():
    fspath = AntaniSetting.objects.get(key="repopath").value
    id = sys.argv[1]
    build = Build.objects.get(pk=id)
    print("Overwriting out.zip")
    z = zipfile.ZipFile("out.zip", mode="w", compression=zipfile.ZIP_DEFLATED)
    for fc in build.mods.all():
        slug, mcver, ver = fc.file.split("-")
        mz = zipfile.ZipFile(fspath + path.sep + "mods" + path.sep + slug + path.sep + slug + "-" + mcver + "-"
                             + ver + ".zip", mode="r")
        for fzipped in mz.namelist():
            z.write(fzipped, mz.open(fzipped, mode="rb").read())
        mz.close()
    z.close()




if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please give me the ID of the build to package. You can get the ID from the URL when editing the build.")
    else:
        main()
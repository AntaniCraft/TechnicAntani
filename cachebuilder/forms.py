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

from django import forms
import re
from cachebuilder.pack_manager import ModpackManager


class CreatePack(forms.Form):
    gitrepo = forms.CharField(max_length=255)
    # TODO gitolite support

    def clean_gitrepo(self):
        isgit = re.compile("http.*\.git")
        if isgit.match(self.cleaned_data['gitrepo']) is None:
            raise forms.ValidationError("Not a valid git repo. Please use http git link.", code='invalidurl')
        pm = ModpackManager()
        if get_repo_name(self.cleaned_data['gitrepo']) in pm.list_packs():
            raise forms.ValidationError("Cannot assign a duplicate name. Rename your git repo", code='duplicatename')
        return self.cleaned_data['gitrepo']

def get_repo_name(mrepo):
    matcher = re.compile(".*/(.*?)\.git")
    gm = matcher.match(mrepo)
    return gm.group(1)
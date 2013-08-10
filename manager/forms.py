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
from manager.models import Build, Modpack


class AddModForm(forms.Form):
    modtype = forms.ChoiceField(choices=(
        (1, "Config Pack - BROKEN"),
        (2, "Core Mod"),
        (3, "Normal"),
        (4, "Pre Packaged")
    ), label="Upload Type")
    zipfile = forms.FileField()


class ConfirmDataForm(forms.Form):
    filepath = forms.CharField(widget=forms.HiddenInput)  # I know, i know.
    type = forms.IntegerField(widget=forms.HiddenInput)
    slug = forms.CharField(max_length=20, label="Identifier")
    name = forms.CharField(max_length=255, label="Pretty Name")
    desc = forms.CharField(widget=forms.Textarea, max_length="255", label="Decription")
    mcversion = forms.CharField(max_length=50, label="Minecraft Version")
    version = forms.CharField(max_length=50, label="Version")
    author = forms.CharField(max_length=255, label="Author(s)")
    url = forms.URLField(max_length=255,label="Mod Home Page")


class CreateBuildForm(forms.ModelForm):
    class Meta:
        model = Build
        fields = ['mcversion', 'version']


class CreateModpackForm(forms.ModelForm):
    logo = forms.ImageField(help_text="PNG 180x110")
    icon = forms.ImageField(help_text="PNG 32x32")
    background = forms.ImageField(help_text="JPG 800x510")

    class Meta:
        model = Modpack
        fields = ['slug', 'name', 'url']

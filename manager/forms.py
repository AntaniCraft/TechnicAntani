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
        #(1, "Config Pack - BROKEN"),
        (3, "Normal"),
        (2, "Core Mod"),
        (4, "Pre Packaged")
    ), label="Upload Type", widget=forms.Select(attrs={"class": "form-control"}))
    zipfile = forms.FileField()


class ConfirmDataForm(forms.Form):
    filepath = forms.CharField(widget=forms.HiddenInput)  # I know, i know.
    type = forms.IntegerField(widget=forms.HiddenInput)
    slug = forms.CharField(max_length=20, label="Identifier", widget=forms.TextInput(attrs={"class": "form-control"}))
    name = forms.CharField(max_length=255, label="Pretty Name", widget=forms.TextInput(attrs={"class": "form-control"}))
    desc = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}), max_length="255", label="Decription")
    mcversion = forms.CharField(max_length=50, label="Minecraft Version", widget=forms.TextInput(attrs={"class": "form-control"}))
    version = forms.CharField(max_length=50, label="Version", widget=forms.TextInput(attrs={"class": "form-control"}))
    author = forms.CharField(max_length=255, label="Author(s)", widget=forms.TextInput(attrs={"class": "form-control"}))
    url = forms.URLField(max_length=255,label="Mod Home Page", widget=forms.TextInput(attrs={"class": "form-control"}))


class CreateBuildForm(forms.ModelForm):
    class Meta:
        model = Build
        fields = ['mcversion', 'version']


class CreateModpackForm(forms.ModelForm):
    logo = forms.ImageField(help_text="Logo must be a PNG image, dimension 180x110. This image is the first one visible"
                                      " to the user in the launcher.")
    icon = forms.ImageField(help_text="Icon must be a PNG square image (32x32 will be ok). It's visible in the tray when"
                                      " a user launches your modpack")
    background = forms.ImageField(help_text="The launcher background. It must be a JPG - size 800x510")

    class Meta:
        model = Modpack
        fields = ['slug', 'name', 'url']


class AntaniSettings(forms.Form):
    apikey = forms.CharField(max_length=128, label="API key", help_text="Technic Platform API key")
    repopath = forms.CharField(max_length=255, label="Path to mod repo",
                               help_text="This should be readable/writable from TechnicAntani, so ensure it's running"
                                         " with adequate rights")
    repourl = forms.URLField(max_length=255, label="Url to mod repo",
                             help_text="This is repopath exposed to the web.")
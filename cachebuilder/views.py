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

from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
import cachebuilder.tasks as mytasks
from cachebuilder.forms import CreatePack


@login_required
def index(request):
    context = {
        'menu': 'cachepacks'
    }
    return render(request, "cachebuilder/index.html", context)


@login_required
def build_all_caches(request):
    mytasks.build_all_caches.delay()
    return redirect(index)

@login_required
def create_modpack(request):
    context = {
        'menu': 'createpack'
    }
    if request.method == 'POST':
        form = CreatePack(request)
        if form.is_valid():
            mytasks.clone_modpack(form.cleaned_data['gitrepo'],form.cleaned_data['name']).delay()
            context['packname'] = form.cleaned_data['name']
            return render(request, "cachebuilder/creating.html", context)
    else:
        form = CreatePack()
    context['form'] = form
    return render(request, "cachebuilder/create.html", context)

@login_required
def github_hook(request):
    pass
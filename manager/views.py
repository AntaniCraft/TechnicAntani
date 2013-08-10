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
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import exceptions

import tempfile, re
import os.path

from manager.models import Modpack, Build, FileCache, ModCache, McVersion, AntaniSetting
from manager.forms import AddModForm, ConfirmDataForm, CreateModpackForm
from manager.mod_manager import ModManager, RawMod, checksum_file


def index(request):
    return render_to_response("index.html")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


@login_required(login_url="/login")
def modpacks_index(request):
    mps = []
    for mp in Modpack.objects.all():
        mps.append(mp)
    context = {
        "modpacks": mps,
    }
    return render(request, "technic/index.html", context)


@login_required(login_url="/login")
def modpacks_create(request):
    return render_to_response("technic/index.html")


@login_required(login_url="/login")
def modpack(request, id):
    m = Modpack.objects.get(pk=id)
    builds = Build.objects.filter(modpack=m)
    context = {
        "modpack": m,
        "builds": builds
    }
    return render(request, "technic/builds.html", context)


@login_required(login_url="/login")
def modpack_build_create(request, modpackid):
    m = Modpack.objects.get(pk=modpackid)
    if request.method == 'POST':
        form = CreateModpackForm(request.POST)
        if form.is_valid():
            b = Build()
            b.modpack = m
            b.mcversion = form.cleaned_data['mcversion']
            b.version = form.cleaned_data['version']
            b.save()

            return HttpResponseRedirect("/builds/" + str(b.id))
    else:
        form = CreateModpackForm()
    return render(request, "technic/create.html", {'form': form, 'mod': m})


@login_required(login_url="/login")
def modpack_build_change(request, buildid):
    b = Build.objects.get(pk=buildid)
    mm = ModManager()

    search = request.GET.get('q')
    mods_listed = []
    try:
        pat = re.compile(search)
        for mod in mm.mods:
            if pat.search(mod.name):
                mods_listed.append(mod)
    except TypeError:
        pass  #YOLO
    if len(mods_listed) == 0:
        mods_listed = mm.mods

    context = {
        'modpack': b.modpack,
        'build': b.version,
        'mcver': b.mcversion.version,
        'mods_installed': b.mods.all(),
        'mods_available': mods_listed
    }
    return render(request, "technic/builds/modify.html", context)


@login_required(login_url="/login")
def modpack_build_add(request, buildid, file):
    if not request.method == 'GET':
        return HttpResponseRedirect("/modpacks")

    slug, mcver, ver = file.split("-")
    b = Build.objects.get(pk=buildid)
    # I'm lazy, I know
    mm = ModManager()
    for mod in mm.mods:
        if mod.slug == slug:
            try:
                mc = ModCache.objects.get(name=slug)
            except exceptions.ObjectDoesNotExist:
                mc = ModCache()
            mc.name = slug
            mc.pretty_name = mod.name
            mc.author = mod.author
            mc.description = mod.description
            mc.link = mod.url
            mc.save()
            try:
                fc = FileCache.objects.get(file=file)
            except exceptions.ObjectDoesNotExist:
                fc = FileCache()
            fc.version = ver
            fc.modInfo = mc
            fc.file = file
            try:
                mccver = McVersion.objects.get(version=mcver)
            except exceptions.ObjectDoesNotExist:
                mccver = McVersion.objects.all()[-1]
            fc.mcversion = mccver
            fc.checksum = checksum_file(AntaniSetting.objects.get(key="repopath").value + os.path.sep +
                                        slug + os.path.sep + file + ".zip")
            fc.save()
            b.mods.add(fc)
            b.save()
            break
    return HttpResponseRedirect("/builds/" + str(b.id))


@login_required(login_url="/login")
def modpack_build_remove(request, buildid, fileid):
    if not request.method == 'GET':
        return HttpResponseRedirect("/modpacks")

    fc = FileCache.objects.get(pk=fileid)
    b = Build.objects.get(pk=buildid)
    b.mods.remove(fc)
    b.save()
    return HttpResponseRedirect("/builds/" + str(b.id))



@login_required(login_url="/login")
def mods_list(request):
    mm = ModManager()
    paginator = Paginator(mm.mods, 25)

    page = request.GET.get('page')

    try:
        mods = paginator.page(page)
    except PageNotAnInteger:
        mods = paginator.page(1)
    except EmptyPage:
        mods = paginator.page(paginator.num_pages)

    return render(request, "technic/mods/list.html", { 'mods': mods })

@login_required(login_url="/login")
def mods_upload(request):
    if request.method == 'POST':
        form = AddModForm(request.POST, request.FILES)
        if form.is_valid():
            tempUpload = tempfile.mktemp(".zip")
            with open(tempUpload, 'wb+') as destination:
                for chunk in request.FILES['zipfile'].chunks():
                    destination.write(chunk)
            raw = RawMod(tempUpload, form.cleaned_data['modtype'])
            raw.readMetadata()
            confirmForm = ConfirmDataForm(initial={
                'filepath': raw.jarpath,
                'type': raw.type,
                'slug': raw.modid,
                'name': raw.name,
                'desc': raw.desc,
                'author': raw.authors,
                'url': raw.url,
                'mcversion': raw.mcversion,
                'version': raw.ver
            })
            return render(request, "technic/mods/add_confirm.html", {'form': confirmForm})
    else:
        form = AddModForm()

    return render(request, "technic/mods/add.html", {'form': form })


@login_required(login_url="/login")
def mods_submit(request):
    if not request.method == 'POST':
        return HttpResponseNotFound()
    form = ConfirmDataForm(request.POST)
    if form.is_valid():
        raw = RawMod(form.cleaned_data['filepath'], form.cleaned_data['filepath'])
        raw.readMetadata()
        mm = ModManager()
        mm.add_mod(
            form.cleaned_data['slug'],
            form.cleaned_data['name'],
            form.cleaned_data['desc'],
            form.cleaned_data['author'],
            form.cleaned_data['url'],
            form.cleaned_data['mcversion'],
            form.cleaned_data['version'],
            raw.pack()
        )
        return HttpResponseRedirect("/mods")
    return render(request, "technic/mods/add_confirm.html", {'form': form})


@login_required(login_url="/login")
def mods_repair(request): # TODO
    return render_to_response("technic/index.html")
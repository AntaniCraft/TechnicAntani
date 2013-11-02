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
from os import mkdir
import urllib2
import json

from manager.models import Modpack, Build, FileCache, ModCache, McVersion, AntaniSetting
from manager.forms import AddModForm, ConfirmDataForm, CreateBuildForm, CreateModpackForm, AntaniSettings
from manager.mod_manager import ModManager, RawMod, checksum_file


def index(request):
    context = {
        'modpacks': Modpack.objects.all(),
        'builds': Build.objects.all()
    }
    return render(request, "index.html", context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


@login_required(login_url="/login")
def modpacks_index(request):
    context = {
        "modpacks": Modpack.objects.all(),
    }
    return render(request, "technic/index.html", context)


@login_required(login_url="/login")
def modpacks_create(request):
    if request.method == 'POST':
        createM = CreateModpackForm(request.POST, request.FILES)
        if createM.is_valid():
            rootdir = AntaniSetting.objects.get(key="repopath").value
            m = Modpack()
            m.slug = createM.cleaned_data["slug"]
            m.name = createM.cleaned_data["name"]
            m.url = createM.cleaned_data["url"]
            mdir = rootdir + os.path.sep + m.slug + os.path.sep
            if not os.path.exists(mdir):
                mkdir(mdir)
            resdir = mdir + os.path.sep + "resources" + os.path.sep
            if not os.path.exists(resdir):
                mkdir(resdir)
            with open(resdir + "background.jpg", 'wb+') as destination:
                for chunk in request.FILES['background'].chunks():
                    destination.write(chunk)
                destination.close()
            m.background_md5 = checksum_file(resdir+"background.jpg")
            with open(resdir + "logo_180.png", 'wb+') as destination:
                for chunk in request.FILES['logo'].chunks():
                    destination.write(chunk)
                destination.close()
            m.logo_md5 = checksum_file(resdir+"logo_180.png")
            with open(resdir + "icon.png", 'wb+') as destination:
                for chunk in request.FILES['icon'].chunks():
                    destination.write(chunk)
                destination.close()
            m.icon_md5 = checksum_file(resdir+"icon.png")
            m.save()
            return HttpResponseRedirect("/modpacks/"+str(m.id))
    else:
        createM = CreateModpackForm()
    context = {
        'form': createM
    }
    return render(request, "technic/create.html", context)


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
        form = CreateBuildForm(request.POST)
        if form.is_valid():
            b = Build()
            b.modpack = m
            b.mcversion = form.cleaned_data['mcversion']
            b.version = form.cleaned_data['version']
            b.save()

            return HttpResponseRedirect("/builds/" + str(b.id))
    else:
        form = CreateBuildForm()
    return render(request, "technic/builds/create.html", {'form': form, 'mod': m})


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
        'build': b,
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
                                        "mods" + os.path.sep + slug + os.path.sep + file + ".zip")
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
        raw.type = form.cleaned_data['type']
        mm = ModManager()
        mm.add_mod(
            form.cleaned_data['slug'],
            form.cleaned_data['name'],
            form.cleaned_data['desc'],
            form.cleaned_data['author'],
            form.cleaned_data['url'],
            form.cleaned_data['mcversion'],
            form.cleaned_data['version'],
            raw.pack(form.cleaned_data['slug']+"_"+form.cleaned_data['version'])
        )
        return HttpResponseRedirect("/mods")
    return render(request, "technic/mods/add_confirm.html", {'form': form})


@login_required(login_url="/login")
def mods_repair(request):
    rootdir = AntaniSetting.objects.get(key="repopath").value
    brokenCache = []
    brokenBuilds = {}
    orphanFc = []
    orphanM = {}
    for fc in FileCache.objects.all():
        if not os.path.isfile(rootdir + os.path.sep + fc.modInfo.name + os.path.sep + fc.file + ".zip"):
            brokenCache.append(fc)
        bs = Build.objects.filter(mods__pk=fc.id)
        if len(bs) < 1:
            orphanFc.append(fc)

    for fc in brokenCache:
        bs=Build.objects.filter(mods__pk=fc.id)
        brokenBuilds[fc] = []
        for b in bs:
            brokenBuilds[fc].append(b)

    for mc in ModCache.objects.all():
        bs = Build.objects.filter(modInfo__pk=mc.id)
        found = False
        for b in bs:
            if not b in orphanFc:
                found = True
                break
        if not found:
            orphanM[mc] = bs

    context = {
        "broken": brokenBuilds,
        "orphanFiles": orphanFc,
        "orphanMods": orphanM
    }

    return render(request,"technic/repair.html",context)


@login_required(login_url="/login")
def mods_repair_do(request, what):
    rootdir = AntaniSetting.objects.get(key="repopath").value
    cache = True
    broken = True
    if what == "cache":
        broken = False
    if what == "broken":
        cache = False

    if cache:
        for fc in FileCache.objects.all():
            bs = Build.objects.filter(mods__pk=fc.id)
            if len(bs) < 1:
                fc.delete()

        for mc in ModCache.objects.all():
            bs = Build.objects.filter(modInfo__pk=mc.id)
            if len(bs) < 1:
                mc.delete()

    if broken:
        for fc in FileCache.objects.all():
            if not os.path.isfile(rootdir + os.path.sep + fc.modInfo.name + os.path.sep + fc.file + ".zip"):
                bs=Build.objects.filter(mods__pk=fc.id)
                for b in bs:
                    b.delete()
                fc.delete()

@login_required(login_url="/login")
def modpack_build_flag(request, buildid, mode):
    b = Build.objects.get(pk=buildid)
    if mode == "latest":
        for bn in Build.objects.all():
            bn.latest = False
            bn.save()
        b.latest = True
        b.save()
    else:
        for bn in Build.objects.all():
            bn.recommended = False
            bn.save()
        b.recommended = True
        b.save()
    return HttpResponseRedirect("/modpacks/"+str(b.modpack.id))

@login_required(login_url="/login")
def modpack_build_clone(request, buildid):
    b = Build.objects.get(pk=buildid)
    if request.method == 'POST':
        form = CreateBuildForm(request.POST)
        if form.is_valid():
            nb = Build()
            nb.modpack = b.modpack
            nb.mcversion = form.cleaned_data['mcversion']
            nb.version = form.cleaned_data['version']
            nb.save()
            for mod in b.mods.all():
                nb.mods.add(mod)
            nb.save()

            return HttpResponseRedirect("/builds/" + str(nb.id))
    else:
        form = CreateBuildForm()
    return render(request, "technic/builds/clone.html", {'form': form, 'build': b})

@login_required(login_url="/login")
def modpack_settings(request):
    try:
        fapikey = AntaniSetting.objects.get(key="apikey")
    except exceptions.ObjectDoesNotExist:
        fapikey = AntaniSetting()
        fapikey.key = "apikey"
        fapikey.value = ""
    try:
        frepourl = AntaniSetting.objects.get(key="repourl")
    except exceptions.ObjectDoesNotExist:
        frepourl = AntaniSetting()
        frepourl.key = "repourl"
        frepourl.value = ""
    try:
        frepopath = AntaniSetting.objects.get(key="repopath")
    except exceptions.ObjectDoesNotExist:
        frepopath = AntaniSetting()
        frepopath.key = "repopath"
        frepopath.value = ""
    if request.method == 'POST':
        form = AntaniSettings(request.POST)
        if form.is_valid():
            fapikey.value = form.cleaned_data["apikey"]
            fapikey.save()
            frepopath.value = form.cleaned_data["repopath"]
            frepopath.save()
            frepourl.value = form.cleaned_data["repourl"]
            frepourl.save()

    else:
        form = AntaniSettings(initial={
            'apikey': fapikey.value,
            'repourl': frepourl.value,
            'repopath': frepopath.value,
        })
    return render(request, "technic/settings.html", {'form': form})

@login_required(login_url="/login")
def modpack_settings_mcvers(request):
    resp = urllib2.urlopen("http://www.technicpack.net/api/minecraft")
    obj = json.loads(resp.read())
    for k, v in obj.iteritems():
        try:
            t = McVersion()
            t.version = k
            t.checksum = v["md5"]
            t.save()
        except Exception:
            pass
    return HttpResponseRedirect("/modpacks/settings/")

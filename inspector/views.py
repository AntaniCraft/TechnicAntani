from django.shortcuts import render
from api.models import *

def inspect_mods(request):
    context = {
        'menu': 'inspect_mods',
        'mods': ModInfoCache.objects.all()
    }
    return render(request, 'inspector/mods.html', context)

def inspect_packs(request):
    context = {
        'menu': 'inspect_mods',
        'packs': ModpackCache.objects.all()
    }
    return render(request, 'inspector/packs.html', context)

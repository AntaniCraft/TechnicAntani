#!/usr/bin/python3

import json
from urllib.request import urlopen,urlretrieve
import sys
import shutil
import os
import zipfile

def fetch_forge(version, mcver):
    """
    Fetches forge from files.minecraftforge.org and returns the
    path it was saved into
    """
    print("Fetching forge v" + version)
    url = "http://files.minecraftforge.net/maven/net/minecraftforge/forge/" + mcver + "-" + version + "/forge-" + mcver + "-" + version + "-universal.jar"
    (tpath, message) = urlretrieve(url)
    if message.get_content_type() != "application/java-archive":
        print("Cannot find url " + url)
        return None
    return tpath


data = urlopen(sys.argv[1]).read()

obj = json.loads(data.decode('utf-8'))

forgefile = fetch_forge(obj['forge'], obj['minecraft'])

if not forgefile:
    sys.exit(1)

shutil.move(forgefile, "minecraft-forge.jar")


for mod in obj['mods']:
    url = mod['url'].replace('\\\\/', '/')
    print(url, end='')
    print(" Downloading....", end='', flush=True)
    (tpath, message) = urlretrieve(url)
    if message.get_content_type() != 'application/zip':
        print("Error downloading " + url)
        os.unlink(tpath)
    print("Extracting....", end='', flush=True)
    z = zipfile.ZipFile(tpath)
    z.extractall()
    print("Done!")
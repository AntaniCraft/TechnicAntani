# TechnicAntani
This is a rewrite of TechnicSolder in python-django 1.5. It has a couple of requirements:
 * python >= 2.5
 * python-django >= 1.5
 * python-imaging
 * I recommend running this on Linux or OSX. Though I've coded careful enough to possibly have it running on windows
 I cannot assure it runs 100% smooth there. So you're on your own. Ah, I also happen to drop in /dev/null issues with
 windows OS unless it's a pull request.  

## Why
TechnicSolder is a good thing. Quite the best tool out there. Unfortunately it's not finished and also written in PHP.
TechnicAntani adds some features that I missed when running Solder on my mc server. Here are some:
 * database-less mod repo. It means you can copy a modrepo from somebody and start building your modpack instantly.
 * adding new mods is easy. You just specify whether it's prepackaged, a coremod or a normal mod and TechnicAntani tries
 to deduce some info from it (hint: it reads mcmod.info inside the jar)
 * caching mechanism for mods/files
 * show only relevant mods for the current build. (Eg. When you do a mc 1.6.2 build, it shows only mods for 1.6.2 )
 * Technic Platform integration. Implements solder api
 * Other solder features
 
## Installing
It's quite complicated at the moment.
 * edit TechnicAntani/settings.py
 * Deploy the django app somewhere.
 * run ./manage.py syncdb
 * In the admin page add 3 required antani settings
TODO

## TODO
 * Prettier HTML + templating
 * User managing without django admin
 * Documentation
 * Multiple api key support?
 * Modpack import/export?

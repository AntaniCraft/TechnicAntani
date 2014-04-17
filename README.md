# TechnicAntani 2 [![Build Status](https://travis-ci.org/AntaniCraft/TechnicAntani.svg?branch=master)](https://travis-ci.org/AntaniCraft/TechnicAntani)

# WARNING: This is a WIP of version 2. I've rethought all deployment system and switched to be different from TechnicSolder (aka it's catching up finally so I can do cooler things)

This is a rewrite of TechnicSolder in python-django 1.6. It has a couple of requirements:
 * python >= 3.3
 * python-pip for python3
 * python-virtualenv for python3
 * git
 *
 * I recommend running this on Linux or OSX. Though I've coded careful enough to possibly have it running on windows
 I cannot assure it runs 100% smooth there. So you're on your own. Ah, I also happen to drop in /dev/null issues with
 windows OS unless it's a pull request.  

## Why
Because I want to bring modpack development and server management to a whole new level.

## Planned features (in order of priority)
 * Fabric deployment and documentation
 * External repos support (Github is the first provider we'll support, aka webhooks)
 * Remote Minecraft Server Deployment
 * Remote Minecraft Server Autoupdate
 * Embed gitolite setup in deployment (and easy "magic" management)

#!/bin/bash 

# Default options:

NGINX_DIR="/etc/nginx"
TECH_USER="antani"
GIT_REPO="http://github.com/AntaniCraft/TechnicAntani.git"

debug() { echo "DEBUG: $1" 1>&2; }
error() { echo "ERROR: $1" 1>&2; }

PARAM=$(getopt -n "$0" -o dn:u: --long debug,nginx-dir:,user: -- "$@")

if [ $? != 0 ] ; then error "Oh no! Something has gone wrong!" >&2 ; exit 1 ; fi

eval set -- "$PARAM"

PDEBUG=false

while true ; do
    case "$1" in
        -d|--debug)
	    debug "Debugging mode enabled."
	    PDEBUG=true
	    shift ;;
        -n|--nginx-dir)
	    if $PDEBUG ; then debug "Setting nginx directory to '$2'"; fi
	    NGINX_DIR=$2
	    shift 2 ;;
        -u|--user)
	    if $PDEBUG ; then debug "Setting user to '$2'"; fi
	    TECH_USER=$2
	    shift 2 ;;
        --) 
	    shift ; break ;;
        *) 
	    error "Oh no! Something has gone wrong!" ; exit 1 ;;
    esac
done

useradd -s /sbin/nologin -m $TECH_USER 
if [ $? != 0 ] ; then error "I can't create user '$TECH_USER'" >&2 ; exit 1 ; fi

cd ~$TECH_USER
if [ $? != 0 ] ; then error "I can't open $TECH_USER's home" >&2 ; exit 1 ; fi

su $TECH_USER -c "mkdir source repository"
if [ $? != 0 ] ; then error "I can't create system directories" >&2 ; exit 1 ; fi

cd source
git clone $GIT_REPO .
if [ $? != 0 ] ; then error "I can't create system directories" >&2 ; exit 1 ; fi
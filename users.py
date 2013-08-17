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

from __future__ import print_function
import sys
from getpass import getpass
import os



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TechnicAntani.settings")

# here be dragons (aka django)
from django.contrib.auth.models import User


def list_users(args):
    quiet = False
    if "-q" in args:
        quiet = True
    if not quiet:
        print("ID\tusername")
        print("------------")
    for u in User.objects.all():
        print(str(u.id) + " " + u.username)


def create_user(args):
    if len(args) < 1:
        print_help()
    x = User()
    x.username = args[0]
    if len(args) == 2:
        x.email = args[1]
    x.set_password(getpass())
    x.save()
    print("User created.")


def change_pass(args):
    if len(args) < 1:
        print_help()
    x = User.objects.get(pk=args[0])
    x.set_password(getpass())
    x.save()
    print("Password changed.")


def delete_user(args):
    if len(args) < 1:
        print_help()
    x = User.objects.get(pk=args[0])
    x.delete()
    print("User deleted.")


def main(args):
    if args[0] == "list":
        list_users(args[1:])
    elif args[0] == "create":
        create_user(args[1:])
    elif args[0] == "chpass":
        change_pass(args[1:])
    elif args[0] == "delete":
        delete_user(args[1:])
    else:
        print_help()


def print_help():
    print("""Usage:
\tlist [-q]
\tcreate name [email]
\tchpass id
\tdelete id
          """)
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
    else:
        main(sys.argv[1:])


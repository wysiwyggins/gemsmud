"""
Room

Rooms are simple containers that has no location of their own.

"""
import random
from evennia import CmdSet
from evennia import utils
from evennia import default_cmds
from evennia import gametime
from evennia import DefaultRoom
from django.conf import settings
from evennia import DefaultRoom, DefaultObject, TICKER_HANDLER
from evennia.contrib.extended_room import ExtendedRoom
from evennia.objects.models import ObjectDB
from collections import defaultdict
from evennia.utils.utils import (
    variable_from_module,
    lazy_property,
    make_iter,
    is_iter,
    list_to_string,
    to_str,
)

ECHOES = ["Immense blue skies, roaring and cloudless above.",
    "Clouds gather overhead.",
    "It's starting to drizzle.",
    "A sea breeze blusters overhead.",
    "The wind is picking up.",
    "The air is calm.",
    "Gulls cry in the distance."]  # etc

class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    pass


class OutdoorRoom(ExtendedRoom):
    "This room is ticked at regular intervals"

    def at_object_creation(self):
        "called only when the object is first created"
        TICKER_HANDLER.add(60*5, self.at_weather_update)

    def at_weather_update(self, *args, **kwargs):
        "ticked at regular intervals"
        echo = random.choice(ECHOES)
        self.msg_contents(echo)

class WelcomeRoom(DefaultRoom):
    """
    This is the Welcome Room. There's Weather here and you can see if people are in the recreation area
    """

    def return_appearance(self, looker, **kwargs):
        tennis_court = ObjectDB.objects.get(id=88)

        rec_message = "The nearby tennis courts are (always) empty."
        for x in tennis_court.contents:
            if x.has_account:
                rec_message=" You can see people milling about on the tennis court."
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not looker:
            return ""
        # get and identify all objects
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(key)
            elif con.has_account:
                users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)
        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        if desc:
            string += "%s" % desc
            string += " " + rec_message
        if exits:
            string += "\n|wExits:|n " + list_to_string(exits)
        if users or things:
            # handle pluralization of things (never pluralize users)
            thing_strings = []
            for key, itemlist in sorted(things.items()):
                nitem = len(itemlist)
                if nitem == 1:
                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                else:
                    key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
                        0
                    ]
                thing_strings.append(key)

            string += "\n|wYou see:|n " + list_to_string(users + thing_strings)

        return string

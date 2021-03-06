"""
Object

The Object is the "naked" base class for things in the game world.

Note that the default Character, Room and Exit does not inherit from
this Object, but from their respective default implementations in the
evennia library. If you want to use this class as a parent to change
the other types, you can do so by adding this as a multiple
inheritance.

"""
from evennia import DefaultObject, DefaultExit, Command, CmdSet, search_object
from evennia.utils.search import search_object_attribute
from evennia.objects.models import ObjectDB
import inspect
from typeclasses.characters import Character
from typeclasses.itemator.itemator import Item
from evennia.prototypes.spawner import spawn



class Object(DefaultObject):
    """
    This is the root typeclass object, implementing an in-game Evennia
    game object, such as having a location, being able to be
    manipulated or looked at, etc. If you create a new typeclass, it
    must always inherit from this object (or any of the other objects
    in this file, since they all actually inherit from BaseObject, as
    seen in src.object.objects).

    The BaseObject class implements several hooks tying into the game
    engine. By re-implementing these hooks you can control the
    system. You should never need to re-implement special Python
    methods, such as __init__ and especially never __getattribute__ and
    __setattr__ since these are used heavily by the typeclass system
    of Evennia and messing with them might well break things for you.


    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation

     account (Account) - controlling account (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       account above). Use `sessions` handler to get the
                       Sessions directly.
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     has_account (bool, read-only)- will only return *connected* accounts
     contents (list of Objects, read-only) - returns all objects inside this
                       object (including exits)
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser

    * Handlers available

     aliases - alias-handler: use aliases.add/remove/get() to use.
     permissions - permission-handler: use permissions.add/remove() to
                   add/remove new perms.
     locks - lock-handler: use locks.add() to add new lock strings
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().
     sessions - sessions-handler. Get Sessions connected to this
                object with sessions.get()
     attributes - attribute-handler. Use attributes.add/remove/get.
     db - attribute-handler: Shortcut for attribute-handler. Store/retrieve
            database attributes using self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
            a database entry when storing data

    * Helper methods (see src.objects.objects.py for full headers)

     search(ostring, global_search=False, attribute_name=None,
             use_nicks=False, location=None, ignore_errors=False, account=False)
     execute_cmd(raw_string)
     msg(text=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     copy(new_key=None)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_cmdset_get(**kwargs) - this is called just before the command handler
                            requests a cmdset from this object. The kwargs are
                            not normally used unless the cmdset is created
                            dynamically (see e.g. Exits).
     at_pre_puppet(account)- (account-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (account-controlled objects only) called just
                            after completing connection account<->object
     at_pre_unpuppet()    - (account-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(account) - (account-controlled objects only) called just
                            after disconnecting account<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_before_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_after_move(source_location)          - always called after a move has
                        been successfully performed.
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_object_receive(obj, source_location) - called when this object receives
                        another object

     at_traverse(traversing_object, source_loc) - (exit-objects only)
                              handles all moving across the exit, including
                              calling the other exit hooks. Use super() to retain
                              the default functionality.
     at_after_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_drop(dropper)          - called when this object has been dropped.
     at_say(speaker, message)  - by default, called if an object inside this
                                 object speaks

     """

    pass


class Mirror(DefaultObject):

    def at_desc(self, looker, **kwargs):
        super().at_desc(looker)
        looker.msg("You peer into the mirror. Describe what you see.")
        looker.execute_cmd("setdesc")
        


class CmdActivate(Command):
    key = "activate"
    locks = "cmd:all()"
    """ Generating books is busted, I think I'd like to have individual object type generators so that players have a little more control over what they're making without having full builder access. 
    """
    def func(self):
        newItem = Item()
        item_proto = newItem.generateItem()
        if not self.args:
            self.caller.msg("What do you want to activate?")
            return
        obj = self.caller.search(self.args.strip())
        if not obj:
            return
        if obj != self.obj:
            self.caller.msg("It doesn't seem to be functioning.")
            return
        # incinerator = search_object("incinerator") #not working
        real_item = spawn(item_proto)
        # self.caller.msg(real_item)
        real_item[0].location = self.caller.location
        # incinerator.db.itemcounter += 1 #not working
        self.caller.msg("The object womb heats up tremendously and then excretes one " + real_item[0].name)


class CmdSetItemator(CmdSet):
    """
    A CmdSet for itemators.
    """

    def at_cmdset_creation(self):
        """
        Called when the cmdset is created.
        """
        self.add(CmdActivate())

class Itemator(Object):
    def at_object_creation(self):
        """
        Called when the cmdset is created.
        """
        self.cmdset.add(CmdSetItemator, permanent=True)

# -------------------------------------------------------------
#
# Readable object
#
# The Readable object from the tutorialWorld
#
# -------------------------------------------------------------

class CmdRead(Command):
    """
    Usage:
      read [obj]

    Read some text of a readable object.
    """

    key = "read"
    locks = "cmd:all()"

    def func(self):
        """
        Implements the read command. This simply looks for an
        Attribute "readable_text" on the object and displays that.
        """

        if self.args:
            obj = self.caller.search(self.args.strip())
        else:
            obj = self.obj
        if not obj:
            return
        # we want an attribute read_text to be defined.
        readtext = obj.db.readable_text
        if readtext:
            string = "You read |C%s|n:\n  %s" % (obj.key, readtext)
        else:
            string = "There is nothing to read on %s." % obj.key
        self.caller.msg(string)


class CmdSetReadable(CmdSet):
    """
    A CmdSet for readables.
    """

    def at_cmdset_creation(self):
        """
        Called when the cmdset is created.
        """
        self.add(CmdRead())
        super().at_cmdset_creation()


class Readable(DefaultObject):
    """
    This simple object defines some attributes and
    """

    def at_object_creation(self):
        """
        Called when object is created. We make sure to set the needed
        Attribute and add the readable cmdset.
        """
        super().at_object_creation()
        self.db.readable_text = "There is no text written on %s." % self.key
        # define a command on the object.
        self.cmdset.add_default(CmdSetReadable, permanent=True)

class Incinerator(DefaultObject):
    def at_object_creation(self):
        self.db.itemcounter = 0

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """
        Called after an object has been moved into this object.

        Args:
            moved_obj (Object): The object moved into this one
            source_location (Object): Where `moved_object` came from.
                Note that this could be `None`.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        message = "object received"
        self.location.msg_contents(message)
        """
        if Character in inspect.getmro(moved_obj):
            message = "|500the {objectname} is making a very embarassing racket about being on fire.|n".format(objectname=moved_obj.name)
            self.location.msg_contents(message)
        else:
            message = "|500the {objectname} bursts into flames inside the incinerator.|n".format(objectname=moved_obj.name)
            self.location.msg_contents(message) 
        """
        if moved_obj.db.cursed == True: #this isn't working
            message = "|500the {objectname} smoulders. A sinister presence leaves the room as you feel your jaw unclench.|n".format(objectname=moved_obj.name)
        else:
            message = "|500the {objectname} bursts into flames inside the incinerator.|n".format(objectname=moved_obj.name)
        self.location.msg_contents(message)
        moved_obj.delete()
        super().at_object_receive(self, moved_obj, source_location, **kwargs)

class Counter(Readable):
    def at_desc(self, looker=None):

        """
        I'd love to also maybe show how many items each character has incinerated too, I tried using the source_location arg of at_obj_received in incinerator, but it gets the room, not the player who gave the item.
        """
        cursed = search_object_attribute(key="cursed", category=None, value="true")
        cursedList = []
        for item in cursed:
            cursedList.append(item.name)
        cursedCount = len(cursedList)
        cursedNames = "\n \t".join(cursedList)
        arts = search_object_attribute(
            key="artwork", category=None, value="true")
        artsList = []
        for item in arts:
            artsList.append(item.name)
        artsCount = len(artsList)
        artsNames = "\n \t".join(artsList)
        cnt_omit = Object.objects.filter(db_typeclass_path="typeclasses.rooms.DefaultRoom, typeclasses.hybrid_room.HybridRoom, typeclasses.exits.Exit").count()
        cnt_all = ObjectDB.objects.all().count()
        cnt = cnt_all - cnt_omit
        signtext = "|355    ___  ___    _ ___ ___ _____   ___ _  _ ___  _____  __ \n  / _ \|| _ )_ || || __/ __||_   _|| ||_ _|| \|| ||   \|| __\ \/ / \n || (_) || _ \ |||| || _|| (__  || ||    || |||| .` || ||) || _|| >  <\n  \\___/||___/\__/||___\___|| ||_||   ||___||_||\_||___/||___/_/\_\     |n"
        countertext = "There are currently {count} items in Zone 25. Maximum count is 1000 items.".format(
            count=cnt)
        warningtext = " "
        breakdowntext = "\n \n|555CITIZENS AND BELONGINGS:|n"
        for x in Character.objects.all():
            breakdowntext += "\n |035" + "{x}|n".format(x=x)
            for i in x.contents:
                breakdowntext += "\n \t |555{i}|n".format(i=i)
        if cnt > 1000:
            overcount = 1000 - cnt
            warningtext = "|500Warning, Zone 25 is now {overcount} item(s) over allowed limits.|n".format(overcount=overcount)
        self.db.readable_text = signtext + "\n" + countertext + "\n" + warningtext + breakdowntext + "\n|044Masterpeices: {artsCount}".format(
            artsCount=artsCount) + "\n \t" + artsNames + "\n|500Cursed Objects: {cursedCount}".format(cursedCount=cursedCount) + "\n \t" + cursedNames + "|n" + "\n" + "Check your own inventory at any time with |555inv|n."

        self.db.desc = self.db.readable_text
        super().at_desc(looker)

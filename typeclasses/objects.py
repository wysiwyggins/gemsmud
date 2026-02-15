"""
Object

The Object is the class for general items in the game world.

Use the ObjectParent class to implement common features for *all* entities
with a location in the game world (like Characters, Rooms, Exits).

"""

from evennia import Command, CmdSet
from evennia.objects.objects import DefaultObject
from evennia.contrib.rpg.rpsystem import ContribRPObject
from evennia.utils.search import search_object_attribute


def _broadcast_masterpiece(new_obj):
    """Broadcast a server-wide announcement when a masterpiece is created."""
    from typeclasses.characters import Character

    room = new_obj.location
    room_name = room.key if room else "somewhere"
    msg = (
        f"|044A masterpiece has appeared: |w{new_obj.key}|044 "
        f"(in {room_name}).|n"
    )
    for char in Character.objects.filter(db_account__isnull=False):
        if char.has_account:
            char.msg(msg)


class ObjectParent:
    """
    This is a mixin that can be used to override *all* entities inheriting at
    some distance from DefaultObject (Objects, Exits, Characters and Rooms).

    Just add any method that exists on `DefaultObject` to this class. If one
    of the derived classes has itself defined that same hook already, that will
    take precedence.

    """


class Object(ObjectParent, ContribRPObject):
    """
    This is the root Object typeclass, representing all entities that
    have an actual presence in-game. Inherits from ContribRPObject to
    support poses and sdesc-aware display.
    """

    pass


# -------------------------------------------------------------
# Mirror
# -------------------------------------------------------------


class Mirror(ObjectParent, DefaultObject):
    """
    An object that, when looked at, prompts the looker to set their
    description.
    """

    def at_desc(self, looker, **kwargs):
        super().at_desc(looker, **kwargs)
        looker.msg("You peer into the mirror. Describe what you see.")
        looker.execute_cmd("setdesc")


# -------------------------------------------------------------
# Readable
# -------------------------------------------------------------


class CmdRead(Command):
    """
    Read some text on a readable object.

    Usage:
      read [obj]
    """

    key = "read"
    locks = "cmd:all()"

    def func(self):
        if self.args:
            obj = self.caller.search(self.args.strip())
        else:
            obj = self.obj
        if not obj:
            return
        # Allow dynamic objects (like Counter) to refresh before reading
        obj.at_desc(looker=self.caller)
        readtext = obj.db.readable_text
        if readtext:
            string = "You read |C%s|n:\n  %s" % (obj.key, readtext)
        else:
            string = "There is nothing to read on %s." % obj.key
        self.caller.msg(string)


class CmdSetReadable(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdRead())


class Readable(ObjectParent, DefaultObject):
    """
    An object with readable text. Use `read <obj>` to read it.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.readable_text = "There is no text written on %s." % self.key
        self.cmdset.add_default(CmdSetReadable, permanent=True)


# -------------------------------------------------------------
# Edible
# -------------------------------------------------------------


class CmdEat(Command):
    """
    Eat a food item, destroying it and reducing platform weight.

    Usage:
      eat <item>
    """

    key = "eat"
    aliases = ["consume", "taste"]
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Eat what?")
            return

        obj = self.caller.search(self.args.strip(), location=self.caller)
        if not obj:
            return

        if not obj.db.edible:
            self.caller.msg(f"You can't eat {obj.key}.")
            return

        flavor = obj.db.flavor_text or "It's surprisingly satisfying."
        self.caller.msg(f"You eat the {obj.key}. {flavor}")
        self.caller.location.msg_contents(
            f"$You() $conj(eat) the {obj.key}.",
            from_obj=self.caller,
            exclude=[self.caller],
        )
        from evennia.utils import delay

        delay(0, obj.delete)


class CmdSetEdible(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdEat())


class EdibleObject(ObjectParent, DefaultObject):
    """
    A food item that can be eaten with `eat <item>`, destroying it
    and reducing platform weight.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.edible = True
        self.cmdset.add_default(CmdSetEdible, permanent=True)

    def return_appearance(self, looker, **kwargs):
        appearance = super().return_appearance(looker, **kwargs)
        hint = "\nYou could try to |555eat|n it."
        return (appearance or "") + hint


# -------------------------------------------------------------
# Ration Dispenser (Cafetorium)
# -------------------------------------------------------------


class CmdUseDispenser(Command):
    """
    Take a ration biscuit from the dispenser.

    Usage:
      use <dispenser>
      activate <dispenser>
      operate <dispenser>
    """

    key = "use"
    aliases = ["activate", "operate"]
    locks = "cmd:all()"

    def func(self):
        import datetime
        from django.conf import settings as conf
        from evennia import create_object

        caller = self.caller
        dispenser = self.obj
        limit = getattr(conf, "RATION_DAILY_LIMIT", 3)

        # Lazy daily reset
        today = str(datetime.date.today())
        if dispenser.db.last_reset_date != today:
            dispenser.db.daily_usage = {}
            dispenser.db.last_reset_date = today

        usage = dispenser.db.daily_usage or {}
        used = usage.get(caller.id, 0)

        if used >= limit:
            caller.msg(
                "|yThe dispenser clicks but nothing comes out. "
                "You've had your rations for today.|n"
            )
            return

        # Spawn the biscuit
        biscuit = create_object(
            "typeclasses.objects.EdibleObject",
            key="ration biscuit",
            location=caller.location,
            attributes=[
                ("edible", True),
                ("desc",
                 "A dense, off-white biscuit stamped with the Zone 25 "
                 "seal. It smells faintly of yeast and nothing else."),
                ("flavor_text",
                 "It tastes like compressed sawdust held together by "
                 "good intentions. Nutritionally complete, allegedly."),
            ],
        )

        # Update usage
        usage[caller.id] = used + 1
        dispenser.db.daily_usage = usage
        remaining = limit - (used + 1)

        caller.msg(
            f"The dispenser hums and ejects a |wration biscuit|n. "
            f"({remaining} remaining today)"
        )
        caller.location.msg_contents(
            f"$You() $conj(take) a ration biscuit from the dispenser.",
            from_obj=caller,
            exclude=[caller],
        )


class CmdSetDispenser(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdUseDispenser())


class RationDispenser(ObjectParent, DefaultObject):
    """
    A wall-mounted food dispenser that produces free ration biscuits.
    Each player can take a limited number per day (RATION_DAILY_LIMIT).
    No ash cost. Place in the Cafetorium.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.daily_usage = {}
        self.db.last_reset_date = None
        self.cmdset.add_default(CmdSetDispenser, permanent=True)

    def return_appearance(self, looker, **kwargs):
        import datetime
        from django.conf import settings as conf

        appearance = super().return_appearance(looker, **kwargs)
        limit = getattr(conf, "RATION_DAILY_LIMIT", 3)

        # Calculate remaining for this looker
        today = str(datetime.date.today())
        if self.db.last_reset_date != today:
            remaining = limit
        else:
            usage = self.db.daily_usage or {}
            used = usage.get(looker.id, 0)
            remaining = max(0, limit - used)

        hint = (
            f"\n|555use|n it to take a ration biscuit. "
            f"({remaining} remaining today)"
        )
        return (appearance or "") + hint


# -------------------------------------------------------------
# Counter
# -------------------------------------------------------------


class Counter(Readable):
    """
    A readable sign that dynamically rebuilds its description every
    time it is looked at, querying the database for current game state
    (total item count, danger level, characters and their inventories,
    artwork, cursed objects).
    """

    def at_desc(self, looker, **kwargs):
        from typeclasses.characters import Character
        from django.conf import settings
        from world.zone_monitor import (
            get_item_count, get_danger_level, get_unowned_item_count,
            get_player_item_count,
        )
        from world.economy import get_station_pool

        # --- cursed objects ---
        cursed = search_object_attribute(key="cursed", category=None, value="true")
        cursed_names = [item.name for item in cursed]
        cursed_count = len(cursed_names)

        # --- artwork / masterpieces with holder info ---
        arts = search_object_attribute(key="artwork", category=None, value="true")
        arts_count = len(arts)

        # --- total item count and danger level (shared utility) ---
        cnt = get_item_count()
        limit = settings.ZONE_ITEM_LIMIT
        level, _, _ = get_danger_level(cnt)

        # --- build the sign text ---
        signtext = (
            "|355"                                                      
            "   ___ _                   ___           _             \n"
            "  ||_ _|| ||_ ___ _ __ ___   ||_ _||_ __   __|| || _____  __  \n"
            "   || |||| __/ _ \ '_ ` _ \   || |||| '_ \ / _` ||/ _ \ \/ /  \n"
            "   || |||| ||||  __/ || || || || ||  || |||| || || || (_|| ||  __/>  <   \n"
            "  ||___||\__\___||_|| ||_|| ||_|| ||___||_|| ||_||\__,_||\___/_/\_\  \n"
            "     |n"
        )
        countertext = (
            "There are currently {count} items in Zone 25. "
            "Maximum count is {limit} items."
        ).format(count=cnt, limit=limit)

        # --- danger-level-aware warning ---
        warningtext = " "
        if level == "sinking":
            over = cnt - limit
            warningtext = (
                "|[500|555 EMERGENCY: Zone 25 is {over} item(s) OVER CAPACITY. "
                "THE PLATFORM IS SINKING. |n"
            ).format(over=over)
        elif level == "critical":
            warningtext = (
                "|500DANGER: Structural integrity compromised. "
                "Incinerate excess items immediately.|n"
            )
        elif level == "warning":
            warningtext = (
                "|yNotice: The platform is getting heavy. "
                "Please recycle unneeded items at the KonMarie Temple.|n"
            )

        # --- economy stats ---
        pool = get_station_pool()
        PLAYER_WEIGHT = getattr(settings, "PLAYER_BODY_WEIGHT", 5)
        connected = [
            c for c in Character.objects.filter(db_account__isnull=False)
            if c.has_account
        ]
        body_total = len(connected) * PLAYER_WEIGHT
        stash_count = get_unowned_item_count()

        economytext = (
            f"\n \n|355Station Ash Reserve: {pool} ash|n"
            f"\n|555Citizens aboard: {len(connected)} "
            f"(body weight: {body_total} units)|n"
            f"\n|555Unattended items in rooms: {stash_count}|n"
        )

        # --- citizens breakdown with item counts and ash ---
        breakdowntext = "\n \n|555CITIZENS AND BELONGINGS:|n"
        heaviest_name = None
        heaviest_count = -1
        lightest_name = None
        lightest_count = float("inf")

        for char in Character.objects.all():
            inv_items = list(char.contents)
            total_count = get_player_item_count(char)
            shelf_count = total_count - len(inv_items)
            ash = char.db.ash_tokens or 0

            if total_count > heaviest_count:
                heaviest_count = total_count
                heaviest_name = str(char)
            if total_count < lightest_count:
                lightest_count = total_count
                lightest_name = str(char)

            shelf_note = (
                f" + {shelf_count} on shelf" if shelf_count > 0 else ""
            )
            breakdowntext += (
                f"\n |035{char}|n "
                f"|555({total_count} items{shelf_note}, {ash} ash)|n"
            )
            for item in inv_items:
                breakdowntext += f"\n \t |555{item}|n"

        if heaviest_name:
            breakdowntext += (
                f"\n \n |500Heaviest citizen: {heaviest_name} "
                f"({heaviest_count} items)|n"
            )
        if lightest_name:
            breakdowntext += (
                f"\n |044Lightest traveler: {lightest_name} "
                f"({lightest_count} items)|n"
            )

        # --- masterpieces with holder info ---
        masterpiece_lines = []
        for art in arts:
            loc = art.location
            if loc and loc.is_typeclass(
                "typeclasses.characters.Character", exact=False
            ):
                holder = f"carried by |035{loc}|044"
            elif loc and loc.is_typeclass(
                "typeclasses.objects.DisplayShelf", exact=False
            ):
                room = loc.location
                room_name = room.key if room else "unknown"
                holder = f"displayed in |035{room_name}|044"
            else:
                room_name = loc.key if loc else "unknown"
                holder = f"in |035{room_name}|044"
            masterpiece_lines.append(f"{art.name} ({holder})")

        # --- displayed items by shelf ---
        shelf_lines = []
        shelves = DisplayShelf.objects.all()
        for shelf in shelves:
            shelf_items = [
                o for o in shelf.contents
                if not getattr(o, "destination", None)
            ]
            if shelf_items:
                room = shelf.location
                room_name = room.key if room else "unknown"
                owner = shelf.db.shelf_owner
                owner_name = owner.key if owner and owner.pk else "unclaimed"
                for item in shelf_items:
                    shelf_lines.append(
                        f"{item.name} (in {room_name}, "
                        f"shelf of {owner_name})"
                    )

        self.db.readable_text = (
            signtext + "\n"
            + countertext + "\n"
            + warningtext
            + economytext
            + breakdowntext
            + "\n \n|044Masterpieces: {ac}".format(ac=arts_count)
            + ("\n \t" + "\n \t".join(masterpiece_lines) if masterpiece_lines else "")
            + "\n|500Cursed Objects: {cc}".format(cc=cursed_count)
            + ("\n \t" + "\n \t".join(cursed_names) if cursed_names else "")
            + "\n \n|355On Display:|n"
            + ("\n \t" + "\n \t".join(shelf_lines) if shelf_lines else "\n \tNothing.")
            + "|n\n"
            + "Check your own inventory at any time with |555inv|n."
        )
        self.db.desc = self.db.readable_text
        super().at_desc(looker, **kwargs)


# -------------------------------------------------------------
# Incinerator
# -------------------------------------------------------------


class CmdBurn(Command):
    """
    Burn an object in the incinerator.

    Usage:
      burn <object>
      incinerate <object>
      put <object> in incinerator
    """

    key = "burn"
    aliases = ["incinerate"]
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Burn what?")
            return

        obj = self.caller.search(self.args.strip(), location=self.caller)
        if not obj:
            return

        # Move to the incinerator — triggers at_object_receive
        obj.move_to(self.obj, quiet=True)


class CmdPutIn(Command):
    """
    Put an object into the incinerator.

    Usage:
      put <object> in <incinerator>
    """

    key = "put"
    locks = "cmd:all()"

    def func(self):
        args = self.args.strip()
        if not args:
            self.caller.msg("Put what in the incinerator?")
            return

        # Parse "X in Y" syntax
        if " in " in args:
            obj_name, _, target_name = args.partition(" in ")
            obj_name = obj_name.strip()
            target_name = target_name.strip()

            # Verify the target is this incinerator
            target = self.caller.search(target_name)
            if not target:
                return
            if target != self.obj:
                self.caller.msg("You can't put things in that.")
                return
        else:
            # No "in" — assume the arg is the object to burn
            obj_name = args

        obj = self.caller.search(obj_name, location=self.caller)
        if not obj:
            return

        obj.move_to(self.obj, quiet=True)


class CmdSetIncinerator(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdBurn())
        self.add(CmdPutIn())


class Incinerator(ObjectParent, DefaultObject):
    """
    An object that destroys anything placed inside it.
    Supports: burn X, incinerate X, put X in incinerator,
    give X to incinerator.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(CmdSetIncinerator, permanent=True)

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        from django.conf import settings as conf
        from evennia.utils import delay

        # Determine ash reward (configurable via settings)
        ash = getattr(conf, "ASH_REWARD_NORMAL", 1)
        if moved_obj.db.artwork:
            ash = getattr(conf, "ASH_REWARD_ARTWORK", 3)
        if moved_obj.db.cursed:
            ash = getattr(conf, "ASH_REWARD_CURSED", 2)

        # Award ash to the character who put the item in
        if source_location and hasattr(source_location, "db"):
            current = source_location.db.ash_tokens or 0
            source_location.db.ash_tokens = current + ash
            source_location.msg(
                f"|555+{ash} ash reclaimed "
                f"(total: {source_location.db.ash_tokens})|n"
            )

        if moved_obj.db.cursed:
            message = (
                "|500The {name} smoulders and hisses as the incinerator "
                "breaks it down. A sinister presence leaves "
                "the room as you feel your jaw unclench. "
                "The feedstock gauges tick upward.|n"
            ).format(name=moved_obj.name)
        else:
            message = (
                "|500The {name} catches and flares inside the incinerator. "
                "It breaks apart into constituent matter, reclaimed "
                "for the station's fabrication systems.|n"
            ).format(name=moved_obj.name)
        self.location.msg_contents(message)
        # Defer deletion so the calling command (give/put) can finish
        # before the object loses its database id.
        delay(0, moved_obj.delete)


# -------------------------------------------------------------
# Itemator (Object Womb)
# -------------------------------------------------------------


class CmdUseItemator(Command):
    """
    Use the object womb to generate a random item.

    Usage:
      use <itemator>
      activate <itemator>
      operate <itemator>
    """

    key = "use"
    aliases = ["activate", "operate"]
    locks = "cmd:all()"

    def func(self):
        from django.conf import settings as conf
        from evennia.prototypes.spawner import spawn
        from world.zone_monitor import get_danger_level, LEVEL_SINKING

        # Check platform capacity before spawning
        level, count, limit = get_danger_level()
        if level == LEVEL_SINKING:
            self.caller.msg(self.obj.sinking_message())
            return

        # Check ash cost
        cost = getattr(conf, "ITEMATOR_COST", 1)
        ash = self.caller.db.ash_tokens or 0
        if ash < cost:
            self.caller.msg(
                f"|yThe womb needs feedstock to fabricate -- {cost} ash "
                f"worth of material. You have {ash}. "
                f"Try incinerating something first.|n"
            )
            return

        # Deduct cost
        self.caller.db.ash_tokens = ash - cost

        # Generate and spawn the item
        proto = self.obj.generate_item()
        new_obj = spawn(proto)[0]
        new_obj.location = self.caller.location

        # Set db attributes from proto keys
        for attr in ("artwork", "cursed", "readable_text",
                     "material", "material_category", "material_station",
                     "flavor_words", "weight_fraction"):
            val = proto.get(attr)
            if val is not None:
                setattr(new_obj.db, attr, val)

        # Announce via the parent object (allows subclasses to customize)
        self.obj.announce_spawn(self.caller, new_obj)

        # Broadcast if a masterpiece was created
        if proto.get("artwork"):
            _broadcast_masterpiece(new_obj)

        # Warn if platform is strained after spawning
        new_level, _, _ = get_danger_level()
        if new_level != "safe":
            self.caller.msg(
                "|yThe platform groans beneath the new weight.|n"
            )


class CmdSetItemator(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdUseItemator())


class Itemator(ObjectParent, DefaultObject):
    """
    A mysterious device that generates random items when used.
    Players can 'use', 'activate', or 'operate' it.
    Refuses to spawn when the platform is at sinking capacity.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(CmdSetItemator, permanent=True)

    def generate_item(self):
        from world.itemator_generator import generate_item_proto
        return generate_item_proto()

    def sinking_message(self):
        return (
            "|500The womb shudders and goes dark. The platform is too "
            "heavy -- it refuses to bring anything else into the world.|n"
        )

    def announce_spawn(self, caller, new_obj):
        caller.msg(
            f"The womb draws from the feedstock reserve, hums, "
            f"and vibrates. Something emerges: |w{new_obj.key}|n."
        )
        caller.location.msg_contents(
            f"The womb pulses with light as it processes raw material. "
            f"|w{new_obj.key}|n materializes on the ground.",
            exclude=[caller],
        )

    def return_appearance(self, looker, **kwargs):
        from django.conf import settings as conf
        cost = getattr(conf, "ITEMATOR_COST", 1)
        appearance = super().return_appearance(looker, **kwargs)
        hint = (
            f"\n|555use|n it to fabricate something "
            f"({cost} ash worth of feedstock)."
        )
        if appearance:
            return appearance + hint
        return hint


# -------------------------------------------------------------
# Material Womb (Industrial Park)
# -------------------------------------------------------------


class MaterialWomb(Itemator):
    """
    A workshop machine that produces raw materials instead of finished
    items. Each MaterialWomb is assigned to a station (e.g. "textile",
    "laser", "wax") via db.station. Materials carry flavor words that
    influence crafted item descriptions, and count at fractional weight
    toward the sinking limit.
    """

    def at_object_creation(self):
        super().at_object_creation()
        # db.station must be set after creation, e.g.:
        #   @set machine/station = textile
        if not self.db.station:
            self.db.station = "textile"

    def generate_item(self):
        import random
        from world.materials import get_station_materials, MATERIAL_WEIGHT_FRACTION

        materials = get_station_materials(self.db.station)
        if not materials:
            materials = get_station_materials("textile")

        mat = random.choice(materials)
        return {
            "key": mat["name"],
            "typeclass": "typeclasses.objects.Object",
            "desc": mat["desc"],
            "material": True,
            "material_category": mat["category"],
            "material_station": self.db.station,
            "flavor_words": mat["flavor_words"],
            "weight_fraction": MATERIAL_WEIGHT_FRACTION,
        }

    def sinking_message(self):
        return (
            "|500The machine grinds to a halt. The platform is too "
            "heavy -- it refuses to produce anything else.|n"
        )

    def announce_spawn(self, caller, new_obj):
        caller.msg(
            f"The machine whirs and deposits: |w{new_obj.key}|n."
        )
        caller.location.msg_contents(
            f"The machine hums to life and produces |w{new_obj.key}|n.",
            exclude=[caller],
        )


# -------------------------------------------------------------
# Workbench (Industrial Park Crafting)
# -------------------------------------------------------------


class CmdCombine(Command):
    """
    Combine two materials at a workbench to craft an item.

    Usage:
      combine <material1> and <material2>
      combine <material1>, <material2>
      craft <material1> and <material2>
      mix <material1> and <material2>
    """

    key = "combine"
    aliases = ["craft", "mix"]
    locks = "cmd:all()"

    def func(self):
        from evennia.prototypes.spawner import spawn
        from world.zone_monitor import get_danger_level, LEVEL_SINKING
        from world.crafting import craft_item

        if not self.args:
            self.caller.msg("Combine what? Usage: combine <material1> and <material2>")
            return

        # Parse "X and Y" or "X, Y"
        args = self.args.strip()
        if " and " in args:
            parts = args.split(" and ", 1)
        elif "," in args:
            parts = args.split(",", 1)
        else:
            self.caller.msg("Combine what with what? Usage: combine <material1> and <material2>")
            return

        if len(parts) != 2:
            self.caller.msg("You need exactly two materials to combine.")
            return

        name1 = parts[0].strip()
        name2 = parts[1].strip()

        if not name1 or not name2:
            self.caller.msg("You need exactly two materials to combine.")
            return

        # Search for both materials in the caller's inventory
        mat1 = self.caller.search(name1, location=self.caller,
                                  nofound_string=f"You aren't carrying '{name1}'.")
        if not mat1:
            return
        mat2 = self.caller.search(name2, location=self.caller,
                                  nofound_string=f"You aren't carrying '{name2}'.")
        if not mat2:
            return

        # Verify both are materials
        if not mat1.db.material:
            self.caller.msg(f"{mat1.key} is not a raw material.")
            return
        if not mat2.db.material:
            self.caller.msg(f"{mat2.key} is not a raw material.")
            return

        # Make sure they aren't the same object
        if mat1 == mat2:
            self.caller.msg("You need two different materials.")
            return

        # Check platform capacity
        level, count, limit = get_danger_level()
        if level == LEVEL_SINKING:
            self.caller.msg(
                "|500The workbench shudders. The platform can't take "
                "any more weight.|n"
            )
            return

        # Craft the item
        proto = craft_item(mat1, mat2)
        new_obj = spawn(proto)[0]
        new_obj.location = self.caller.location

        # Set db attributes from proto
        for attr in ("artwork", "cursed", "readable_text"):
            val = proto.get(attr)
            if val is not None:
                setattr(new_obj.db, attr, val)

        # Delete the materials
        mat1_name = mat1.key
        mat2_name = mat2.key
        mat1.delete()
        mat2.delete()

        # Announce
        self.caller.msg(
            f"You feed the {mat1_name} and {mat2_name} into the "
            f"workbench. After a moment, it produces: |w{new_obj.key}|n."
        )
        self.caller.location.msg_contents(
            f"The workbench whirs as it combines materials into "
            f"|w{new_obj.key}|n.",
            exclude=[self.caller],
        )

        # Broadcast if a masterpiece was created
        if proto.get("artwork"):
            _broadcast_masterpiece(new_obj)

        # Platform strain warning
        new_level, _, _ = get_danger_level()
        if new_level != "safe":
            self.caller.msg(
                "|yThe platform groans beneath the new weight.|n"
            )


class CmdSetWorkbench(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdCombine())


class Workbench(ObjectParent, DefaultObject):
    """
    A crafting station where players combine two raw materials into
    a finished item. The materials' flavor words influence the
    resulting item's description.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(CmdSetWorkbench, permanent=True)

    def return_appearance(self, looker, **kwargs):
        appearance = super().return_appearance(looker, **kwargs)
        hint = "\nYou could try to |555combine|n materials here."
        if appearance:
            return appearance + hint
        return hint


# -------------------------------------------------------------
# Display Shelf
# -------------------------------------------------------------


class CmdClaim(Command):
    """
    Claim a display shelf as your own. Items on a claimed shelf
    count toward the owner's item total for hoarding enforcement.
    Only one player may claim a shelf at a time.

    Usage:
      claim shelf
      claim
    """

    key = "claim"
    locks = "cmd:all()"

    def func(self):
        shelf = self.obj
        owner = shelf.db.shelf_owner

        if owner and owner.pk:
            if owner == self.caller:
                self.caller.msg("You already own this shelf.")
            else:
                self.caller.msg(
                    f"This shelf is claimed by {owner.key}."
                )
            return

        shelf.db.shelf_owner = self.caller
        self.caller.msg("You claim the display shelf as your own.")
        self.caller.location.msg_contents(
            f"$You() $conj(claim) the display shelf.",
            from_obj=self.caller,
            exclude=[self.caller],
        )


class CmdUnclaim(Command):
    """
    Release your claim on a display shelf. Any items still on the
    shelf remain, but will no longer count toward your item total.

    Usage:
      unclaim shelf
      unclaim
    """

    key = "unclaim"
    locks = "cmd:all()"

    def func(self):
        shelf = self.obj
        owner = shelf.db.shelf_owner

        if not owner or not owner.pk:
            self.caller.msg("This shelf is not claimed by anyone.")
            return

        if owner != self.caller:
            self.caller.msg(
                f"This shelf belongs to {owner.key}, not you."
            )
            return

        shelf.db.shelf_owner = None
        self.caller.msg(
            "You release your claim on the display shelf."
        )
        self.caller.location.msg_contents(
            f"$You() $conj(release) $pron(your) claim on the display shelf.",
            from_obj=self.caller,
            exclude=[self.caller],
        )


class CmdDisplay(Command):
    """
    Place an item from your inventory onto the display shelf.
    You must own the shelf to display items on it.

    Usage:
      display <item> [on shelf]
      display <item>
    """

    key = "display"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Display what?")
            return

        shelf = self.obj
        owner = shelf.db.shelf_owner
        if not owner or owner != self.caller:
            self.caller.msg(
                "You must claim this shelf first. Use |555claim|n."
            )
            return

        args = self.args.strip()
        if " on " in args:
            obj_name, _, _ = args.partition(" on ")
            obj_name = obj_name.strip()
        else:
            obj_name = args

        obj = self.caller.search(obj_name, location=self.caller)
        if not obj:
            return

        current = [o for o in shelf.contents if not getattr(o, "destination", None)]
        capacity = shelf.db.shelf_capacity or 5
        if len(current) >= capacity:
            self.caller.msg("The shelf is full.")
            return

        # Save original weight fraction so we can restore it on retrieval
        original_fraction = obj.db.weight_fraction
        if original_fraction is not None:
            obj.db.original_weight_fraction = original_fraction

        obj.move_to(shelf, quiet=True)
        obj.db.displayed = True
        from django.conf import settings as conf
        obj.db.weight_fraction = getattr(conf, "DISPLAY_WEIGHT_FRACTION", 0.5)

        self.caller.msg(f"You place {obj.key} on the display shelf.")
        self.caller.location.msg_contents(
            f"$You() $conj(place) {obj.key} on the display shelf.",
            from_obj=self.caller,
            exclude=[self.caller],
        )


class CmdRetrieve(Command):
    """
    Take an item from the display shelf.
    Only the shelf owner can retrieve items.

    Usage:
      retrieve <item> [from shelf]
      retrieve <item>
    """

    key = "retrieve"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Retrieve what?")
            return

        shelf = self.obj
        owner = shelf.db.shelf_owner
        if not owner or owner != self.caller:
            self.caller.msg("This isn't your shelf.")
            return

        args = self.args.strip()
        if " from " in args:
            obj_name, _, _ = args.partition(" from ")
            obj_name = obj_name.strip()
        else:
            obj_name = args

        obj = self.caller.search(obj_name, location=shelf)
        if not obj:
            self.caller.msg("That isn't on the shelf.")
            return

        obj.move_to(self.caller, quiet=True)

        # Restore original weight fraction or clear display attributes
        original = obj.db.original_weight_fraction
        if original is not None:
            obj.db.weight_fraction = original
            del obj.db.original_weight_fraction
        else:
            if obj.db.weight_fraction is not None:
                del obj.db.weight_fraction
        if obj.db.displayed:
            del obj.db.displayed

        self.caller.msg(f"You take {obj.key} from the display shelf.")
        self.caller.location.msg_contents(
            f"$You() $conj(take) {obj.key} from the display shelf.",
            from_obj=self.caller,
            exclude=[self.caller],
        )


class CmdSetDisplayShelf(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdClaim())
        self.add(CmdUnclaim())
        self.add(CmdDisplay())
        self.add(CmdRetrieve())


class DisplayShelf(ObjectParent, DefaultObject):
    """
    A display shelf where players can showcase items. Items on a
    claimed shelf count toward the owner's item total for hoarding
    enforcement. A shelf must be claimed before items can be placed
    on it.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.shelf_capacity = 5
        self.db.shelf_owner = None
        self.cmdset.add_default(CmdSetDisplayShelf, permanent=True)

    def return_appearance(self, looker, **kwargs):
        appearance = super().return_appearance(looker, **kwargs)
        owner = self.db.shelf_owner
        if owner and owner.pk:
            owner_text = f"\n|555Claimed by:|n {owner.key}"
        else:
            owner_text = "\n|555Unclaimed.|n Use |555claim|n to make it yours."
        items = [o for o in self.contents if not getattr(o, "destination", None)]
        if items:
            item_list = "\n".join(f"  {item.key}" for item in items)
            shelf_text = f"\n|wOn display:|n\n{item_list}"
        else:
            shelf_text = "\nThe shelf is empty."
        hint = "\n|555claim|n / |555unclaim|n / |555display <item>|n / |555retrieve <item>|n"
        return (appearance or "") + owner_text + shelf_text + hint

"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.contrib.rpg.rpsystem import ContribRPCharacter
from evennia.contrib.game_systems.clothing import ClothedCharacter

from .objects import ObjectParent


class Character(ObjectParent, ContribRPCharacter, ClothedCharacter):
    """
    The Character combines RP system features (sdescs, recogs, poses,
    emoting) with the clothing system. ContribRPCharacter provides
    sdesc-based names and RP commands; ClothedCharacter adds wearable
    clothing to the character description.
    """

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """Called when an object is moved into this character's inventory."""
        super().at_object_receive(moved_obj, source_location, **kwargs)

        # If the received object is cursed, attach CurseEffectScript
        if moved_obj.db.cursed:
            existing = self.scripts.get("curse_effect")
            if not existing:
                from evennia import create_script

                create_script(
                    "typeclasses.scripts.CurseEffectScript",
                    key="curse_effect",
                    obj=self,
                    persistent=True,
                )

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        """Stamp last_holder when an item leaves inventory for a room."""
        super().at_object_leave(moved_obj, target_location, **kwargs)
        # Only stamp if the item is being dropped into a room
        if target_location and target_location.is_typeclass(
            "typeclasses.rooms.Room", exact=False
        ):
            moved_obj.db.last_holder = self

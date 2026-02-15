"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Standard exit connecting two rooms.
    """

    pass


# -------------------------------------------------------------
# SimpleDoor
# -------------------------------------------------------------
# The SimpleDoor contrib is available at evennia.contrib.grid.simpledoor.
# To use it, add SimpleDoorCmdSet to your CharacterCmdSet and create
# doors with: @open doorway:evennia.contrib.grid.simpledoor.SimpleDoor = otherroom
#
# If you need custom door behavior beyond the contrib, extend it here.

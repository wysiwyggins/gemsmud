"""
Room

Rooms are simple containers that has no location of their own.

"""

import random

from evennia import Command, CmdSet, TICKER_HANDLER
from evennia.contrib.rpg.rpsystem import ContribRPRoom
from evennia.contrib.grid.extended_room import ExtendedRoom

from .objects import ObjectParent


class Room(ObjectParent, ContribRPRoom):
    """
    Base room typeclass. Inherits from ContribRPRoom to support
    pose display and sdesc-aware lookups.
    """

    pass


# Default weather echoes for outdoor rooms
WEATHER_ECHOES = [
    "Immense blue skies, roaring and cloudless above.",
    "Clouds gather overhead.",
    "It's starting to drizzle.",
    "A sea breeze blusters overhead.",
    "The wind is picking up.",
    "The air is calm.",
    "Gulls cry in the distance.",
]


class OutdoorRoom(ObjectParent, ExtendedRoom, ContribRPRoom):
    """
    An outdoor room with time-of-day/seasonal descriptions, details,
    and periodic weather echoes. Combines ExtendedRoom (stateful descs,
    details, broadcast messages) with ContribRPRoom (poses, sdescs).

    Features:
      - Time-of-day and seasonal description switching (via ExtendedRoom)
      - Room details system (look <detail> without creating objects)
      - Weather echoes every 5 minutes
      - RP-aware display (poses, sdescs)

    Use @desc/morning, @desc/evening, @desc/summer etc. to set
    time/season-specific descriptions. Use `detail <key> = <desc>`
    to add details.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.weather_echoes = WEATHER_ECHOES
        TICKER_HANDLER.add(60 * 5, self.at_weather_update)

    def at_weather_update(self, *args, **kwargs):
        """
        Called by the ticker every 5 minutes to show a weather echo.
        At higher danger levels, ominous platform-stress echoes are
        blended in or replace weather entirely.
        """
        from world.zone_monitor import (
            get_item_monitor,
            OMINOUS_ECHOES,
            LEVEL_SAFE,
            LEVEL_WARNING,
            LEVEL_CRITICAL,
            LEVEL_SINKING,
        )

        echoes = self.db.weather_echoes or WEATHER_ECHOES

        # Read the cached danger level from the monitor script
        monitor = get_item_monitor()
        level = monitor.db.danger_level if monitor else LEVEL_SAFE

        if level == LEVEL_SINKING:
            # Full replacement: only ominous echoes
            pool = OMINOUS_ECHOES.get(LEVEL_SINKING, echoes)
        elif level == LEVEL_CRITICAL:
            # 2/3 chance ominous, 1/3 chance weather
            if random.random() < 0.67:
                pool = OMINOUS_ECHOES.get(LEVEL_CRITICAL, echoes)
            else:
                pool = echoes
        elif level == LEVEL_WARNING:
            # 1/3 chance ominous, 2/3 chance weather
            if random.random() < 0.33:
                pool = OMINOUS_ECHOES.get(LEVEL_WARNING, echoes)
            else:
                pool = echoes
        else:
            pool = echoes

        self.msg_contents(random.choice(pool))


# -------------------------------------------------------------
# Laser Room (IRC Bridge)
# -------------------------------------------------------------


def _get_laser_channel():
    """Return the laser_irc channel, or None."""
    from evennia.comms.models import ChannelDB

    try:
        return ChannelDB.objects.get(db_key="laser_irc")
    except ChannelDB.DoesNotExist:
        return None


class CmdTransmit(Command):
    """
    Send a message through the Laser array (to IRC).

    Usage:
      transmit <message>
    """

    key = "transmit"
    aliases = ["broadcast"]
    help_category = "Communication"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Transmit what?")
            return

        channel = _get_laser_channel()
        if not channel:
            self.caller.msg(
                "The array crackles but nothing connects. "
                "No communication channel is active."
            )
            return

        msg = self.args.strip()
        # Send to the channel (which relays to IRC)
        channel.msg(msg, senders=self.caller)

        self.caller.msg(f"You transmit: {msg}")
        self.caller.location.msg_contents(
            f"$You() $conj(transmit) a message through the array.",
            from_obj=self.caller,
            exclude=[self.caller],
        )


class CmdTune(Command):
    """
    Tune into or out of the Laser array frequency.

    Usage:
      tune     - subscribe to the channel
      tune out - unsubscribe from the channel
    """

    key = "tune"
    help_category = "Communication"
    locks = "cmd:all()"

    def func(self):
        channel = _get_laser_channel()
        if not channel:
            self.caller.msg(
                "The array is offline. No channel to tune into."
            )
            return

        account = self.caller.account
        if not account:
            self.caller.msg("You need to be logged in.")
            return

        args = self.args.strip().lower()
        if args == "out":
            if channel.has_connection(account):
                channel.disconnect(account)
                self.caller.msg(
                    "You tune out of the Laser array. Static fills the silence."
                )
            else:
                self.caller.msg("You aren't tuned in.")
        else:
            if channel.has_connection(account):
                self.caller.msg("You are already tuned in.")
            else:
                channel.connect(account)
                self.caller.msg(
                    "You tune into the Laser array. "
                    "The frequency crackles to life."
                )


class CmdSetLaserRoom(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdTransmit())
        self.add(CmdTune())


class LaserRoom(ObjectParent, ContribRPRoom):
    """
    The Laser/Archimedes Array room. Functions as an IRC bridge endpoint.
    Characters in this room can send and receive messages via the
    laser_irc channel, which is bridged to an IRC network.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add_default(CmdSetLaserRoom, permanent=True)

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """Auto-subscribe characters entering the room."""
        super().at_object_receive(moved_obj, source_location, **kwargs)

        account = getattr(moved_obj, "account", None)
        if not account:
            return

        channel = _get_laser_channel()
        if channel and not channel.has_connection(account):
            channel.connect(account)
            moved_obj.msg(
                "The Laser array hums. You are now receiving transmissions."
            )

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        """Notify when characters leave, but keep them subscribed."""
        super().at_object_leave(moved_obj, target_location, **kwargs)

        account = getattr(moved_obj, "account", None)
        if not account:
            return

        channel = _get_laser_channel()
        if channel and channel.has_connection(account):
            moved_obj.msg(
                "You step away from the Laser array. "
                "Transmissions fade to static."
            )

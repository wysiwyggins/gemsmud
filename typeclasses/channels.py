"""
Channel

The channel class represents the out-of-character chat-room usable by
Accounts in-game. It is mostly overloaded to change its appearance, but
channels can be used to implement many different forms of message
distribution systems.

Note that sending data to channels are handled via the CMD_CHANNEL
syscommand (see evennia.syscmds). The sending should normally not need
to be modified.

"""

from evennia.comms.comms import DefaultChannel


class Channel(DefaultChannel):
    """
    Base channel class for the game.
    """

    pass


class LaserChannel(DefaultChannel):
    """
    A channel that only distributes messages to characters currently
    in the Laser room. Used as the game-side endpoint for the IRC bridge.
    """

    def at_channel_creation(self):
        """Cache the Laser room reference."""
        self.db.laser_room = None

    def get_laser_room(self):
        """Return the Laser room object, caching it on first lookup."""
        if not self.db.laser_room:
            from evennia.utils.search import search_object

            results = search_object(
                "Laser", typeclass="typeclasses.rooms.LaserRoom"
            )
            if not results:
                # Fall back to name search across all rooms
                results = search_object("Laser")
            if results:
                self.db.laser_room = results[0]
        return self.db.laser_room

    def distribute_message(self, msg, online=False):
        """
        Override to only deliver messages to accounts whose character
        is currently in the Laser room.
        """
        room = self.get_laser_room()
        if not room:
            return

        for obj in room.contents:
            account = getattr(obj, "account", None)
            if account and self.has_connection(account):
                if online and not account.sessions.count():
                    continue
                account.msg(msg)

    def format_external(self, msg, senders, emit=False):
        """Format messages arriving from IRC."""
        if senders:
            return f"|c[|yIRC|c]|n {senders}: {msg}"
        return f"|c[|yIRC|c]|n {msg}"

    def channel_prefix(self, msg=None, emit=False):
        """No prefix for this channel — the room context is enough."""
        return ""

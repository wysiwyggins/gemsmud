"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_init()
at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""


def at_server_init():
    """
    This is called first as the server is starting up, regardless of how.
    """
    pass


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    # Ensure the Zone 25 item monitor script exists (idempotent).
    from evennia.scripts.models import ScriptDB
    from evennia import create_script

    if not ScriptDB.objects.filter(db_key="item_monitor").exists():
        create_script(
            "typeclasses.scripts.ItemMonitorScript",
            key="item_monitor",
            persistent=True,
        )

    # Initialize station ash pool on the monitor if not yet set.
    monitor = ScriptDB.objects.filter(db_key="item_monitor").first()
    if monitor and monitor.db.station_ash_pool is None:
        from django.conf import settings as conf

        monitor.db.station_ash_pool = getattr(
            conf, "STATION_INITIAL_ASH_POOL", 500
        )

    # Ensure the shop restock script exists (idempotent).
    if not ScriptDB.objects.filter(db_key="shop_restock").exists():
        create_script(
            "typeclasses.scripts.ShopRestockScript",
            key="shop_restock",
            persistent=True,
        )

    # Ensure the Laser IRC channel exists (idempotent).
    from evennia.comms.models import ChannelDB

    if not ChannelDB.objects.filter(db_key="laser_irc").exists():
        from evennia.utils.create import create_channel

        create_channel(
            "laser_irc",
            typeclass="typeclasses.channels.LaserChannel",
            desc="Laser room IRC bridge",
        )


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    pass


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    pass


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    pass


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    pass


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    pass

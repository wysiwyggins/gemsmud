"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

import random

from evennia.scripts.scripts import DefaultScript


class Script(DefaultScript):
    """
    This is the base TypeClass for all Scripts. Scripts describe
    all entities/systems without a physical existence in the game world
    that require database storage (like an economic system or
    combat tracker). They
    can also have a timer/ticker component.

    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties (check docs for full listing, this could be
      outdated).

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    * Helper methods

     create(key, **kwargs)
     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - stop script, and delete it
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there is
                  actual combat going on).
      at_start() - Called every time the script is started, which for persistent
                  scripts is at least once every server start. Note that this is
                  unaffected by self.delay_start, which only delays the first
                  call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True, which
                  will delay the first call of this method by self.interval
                  seconds. If self.interval==0, this method will never
                  be called.
      at_pause()
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned False.
      at_script_delete()
      at_server_reload() - Called when server reloads. Can be used to
                  save temporary variables you want should survive a reload.
      at_server_shutdown() - called at a full server shutdown.
      at_server_start()

    """

    pass


class CurseEffectScript(DefaultScript):
    """
    Attached to a character carrying cursed items. Fires periodically
    to apply negative effects. Removes itself when no cursed items remain.
    """

    def at_script_creation(self):
        self.key = "curse_effect"
        self.desc = "Applies negative effects from cursed items"
        self.interval = 300  # 5 minutes
        self.persistent = True
        self.start_delay = True

    def at_repeat(self):
        char = self.obj
        if not char or not char.location:
            self.stop()
            return

        cursed_items = [o for o in char.contents if o.db.cursed]
        if not cursed_items:
            self.stop()
            return

        # Atmospheric discomfort
        effects = [
            "A chill runs through you. Something you carry feels wrong.",
            "The hair on the back of your neck stands up.",
            "You feel a weight on your shoulders that has nothing to do with gravity.",
            "Something whispers at the edge of hearing. You can't make out the words.",
            "Your hands tremble for a moment. A cold sweat breaks out.",
        ]
        char.msg(f"|500{random.choice(effects)}|n")

        # With multiple cursed items, chance of dropping something
        if len(cursed_items) >= 2 and random.random() < 0.2:
            droppable = [
                o for o in char.contents
                if not getattr(o.db, "worn", False)
            ]
            if droppable:
                drop_item = random.choice(droppable)
                drop_item.move_to(char.location, quiet=True)
                char.msg(
                    f"|500{drop_item.key} slips from your grasp!|n"
                )
                char.location.msg_contents(
                    f"|500{drop_item.key} tumbles from "
                    f"{char.key}'s hands.|n",
                    exclude=[char],
                )

    def is_valid(self):
        if not self.obj:
            return False
        return any(o.db.cursed for o in self.obj.contents)


class InvestigationScript(DefaultScript):
    """
    Timed investigation of a hoarding suspect. Ticks down, broadcasting
    escalating messages. On completion, spawns a SecurityRobot.
    """

    def at_script_creation(self):
        from django.conf import settings as conf

        self.key = "investigation"
        self.desc = "Hoarding investigation"
        self.interval = getattr(conf, "INVESTIGATION_INTERVAL", 60)
        self.persistent = True
        self.start_delay = True
        self.db.ticks_remaining = getattr(conf, "INVESTIGATION_TICKS", 5)
        self.db.total_ticks = self.db.ticks_remaining
        self.db.reporters = []
        self.db.target = None

    def add_reporter(self, reporter):
        """Add a reporter and speed up the investigation."""
        from django.conf import settings as conf

        reporters = self.db.reporters or []
        if reporter not in reporters:
            reporters.append(reporter)
            self.db.reporters = reporters
            speedup = getattr(conf, "INVESTIGATION_SPEEDUP_PER_REPORT", 1)
            self.db.ticks_remaining = max(
                1, self.db.ticks_remaining - speedup
            )

    def at_repeat(self):
        from typeclasses.characters import Character

        target = self.db.target
        if not target or not target.pk:
            self.stop()
            return

        self.db.ticks_remaining -= 1
        remaining = self.db.ticks_remaining

        if remaining > 0:
            # Broadcast escalating investigation messages
            messages = [
                (
                    "|y[ZONE 25] Investigation into {target} is underway. "
                    "{remaining} cycle(s) remain.|n"
                ),
                (
                    "|y[ZONE 25] Enforcement drones are scanning the "
                    "platform for {target}.|n"
                ),
                (
                    "|500[ZONE 25] Investigation of {target} nearing "
                    "completion. {remaining} cycle(s) remain.|n"
                ),
                (
                    "|500[ZONE 25] Security protocols activated. "
                    "{target}'s case is nearly resolved.|n"
                ),
                (
                    "|[500|555[ZONE 25] ENFORCEMENT IMMINENT. {target} "
                    "should report to the KonMarie Temple.|n"
                ),
            ]
            elapsed = self.db.total_ticks - remaining
            idx = min(elapsed, len(messages) - 1)
            msg = messages[idx].format(
                target=target.key, remaining=remaining,
            )
            for char in Character.objects.filter(db_account__isnull=False):
                if char.has_account:
                    char.msg(msg)
        else:
            # Investigation complete -- spawn security robot
            self._spawn_robot()
            target.db.under_investigation = False
            self.stop()

    def _spawn_robot(self):
        """Spawn a SecurityRobot to handle the target."""
        from evennia import create_object, create_script, search_object

        target = self.db.target
        reporters = self.db.reporters or []

        # Find KonMarie Temple
        temple_results = search_object("KonMarie Temple")
        if not temple_results:
            # Fallback: try alternate names
            temple_results = search_object("KonMarie")
        if not temple_results:
            return

        temple = temple_results[0]

        robot = create_object(
            "typeclasses.npcs.SecurityRobot",
            key="Security Unit Z25-09",
            location=temple,
        )

        create_script(
            "typeclasses.npcs.RobotBehaviorScript",
            key=f"robot_behavior_{target.id}",
            obj=robot,
            persistent=True,
            attributes=[
                ("target", target),
                ("reporters", list(reporters)),
                ("phase", "announce"),
            ],
        )


class ShopRestockScript(DefaultScript):
    """
    Global singleton that periodically restocks all shop counters.
    Created at server start via at_server_startstop.py.
    """

    def at_script_creation(self):
        from django.conf import settings as conf

        self.key = "shop_restock"
        self.desc = "Periodically restocks shop counters"
        self.interval = getattr(conf, "SHOP_RESTOCK_INTERVAL", 600)
        self.persistent = True
        self.start_delay = True

    def at_repeat(self):
        from typeclasses.shops import ShopCounter

        for shop in ShopCounter.objects.all():
            shop.restock()


class ItemMonitorScript(DefaultScript):
    """
    Global singleton script that periodically checks the Zone 25 item
    count and broadcasts warnings when danger thresholds are crossed.

    Also caches the current danger level in self.db so other systems
    (OutdoorRoom weather echoes) can read it without re-querying the DB.

    Created once at server start via at_server_startstop.py.
    """

    def at_script_creation(self):
        self.key = "item_monitor"
        self.desc = "Monitors Zone 25 item count and broadcasts warnings"
        self.interval = 180  # 3 minutes
        self.persistent = True
        self.start_delay = True
        self.db.danger_level = "safe"
        self.db.last_count = 0

    def at_repeat(self):
        """Called every self.interval seconds."""
        from django.conf import settings as conf
        from world.zone_monitor import (
            get_danger_level,
            BROADCAST_MESSAGES,
            LEVEL_SAFE,
        )
        from world.economy import credit_station_pool
        from typeclasses.characters import Character

        level, count, limit = get_danger_level()
        old_level = self.db.danger_level

        # Update cached state for other systems to read
        self.db.danger_level = level
        self.db.last_count = count

        # Passive ash recharge — background material recovery from ocean
        # intake, biological waste, and industrial byproducts
        recharge = getattr(conf, "STATION_ASH_RECHARGE", 5)
        if recharge > 0:
            credit_station_pool(recharge)

            # Occasionally echo recovery activity in industrial rooms
            if random.random() < 0.15:
                from evennia import search_object

                RECOVERY_ECHOES = [
                    "Somewhere below, filtration pumps cycle ocean water "
                    "through the reclamation system.",
                    "A low hum resonates through the deck plates as "
                    "the waste processors turn over.",
                    "The feedstock gauges on a nearby panel tick up "
                    "a fraction.",
                    "You hear the distant gurgle of intake valves "
                    "pulling in seawater for processing.",
                    "A faint chemical smell wafts from the recycling "
                    "vents -- the station digesting something.",
                ]
                echo = random.choice(RECOVERY_ECHOES)
                # Send to a random industrial room if occupied
                industrial_names = [
                    "Industrial Park", "Textile megaspools", "Glazier",
                    "Wax extruders", "Polyclay intubators",
                    "\"Milk\" vats", "Confectionary tanks",
                ]
                for name in industrial_names:
                    results = search_object(name, typeclass="typeclasses.rooms.Room")
                    if not results:
                        results = search_object(
                            name, typeclass="typeclasses.rooms.OutdoorRoom"
                        )
                    if results:
                        room = results[0]
                        chars = [
                            c for c in room.contents
                            if hasattr(c, "has_account") and c.has_account
                        ]
                        if chars:
                            room.msg_contents(f"|555{echo}|n")
                            break

        # Broadcast if level changed away from safe, or if critical/sinking
        # (those levels get repeated warnings each tick)
        should_broadcast = False
        if level != old_level and level != LEVEL_SAFE:
            should_broadcast = True
        elif level in ("critical", "sinking"):
            should_broadcast = True

        if not should_broadcast:
            return

        messages = BROADCAST_MESSAGES.get(level, [])
        if not messages:
            return

        over = max(0, count - limit)
        msg = random.choice(messages).format(
            count=count, limit=limit, over=over,
        )

        # Send to all connected characters
        for char in Character.objects.filter(db_account__isnull=False):
            if char.has_account:
                char.msg(msg)

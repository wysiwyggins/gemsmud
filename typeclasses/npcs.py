"""
NPC typeclasses for Zone 25.

SecurityRobot -- an automated enforcement unit that escorts hoarding
offenders to the KonMarie Temple for euthanasia/cremation.
"""

from django.conf import settings as conf

from evennia.objects.objects import DefaultCharacter
from evennia.scripts.scripts import DefaultScript

from .objects import ObjectParent


class SecurityRobot(ObjectParent, DefaultCharacter):
    """
    An automated enforcement NPC. Cannot be puppeted, picked up,
    or interacted with in the normal sense. Exists only while
    carrying out an enforcement action, then self-destructs.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = (
            "A hulking chrome enforcement unit on articulated legs. "
            "Its chassis bears the Zone 25 seal and a scrolling LED "
            "display reading: |500COMPLIANCE IS COMMUNITY|n."
        )
        self.locks.add("get:false()")
        self.locks.add("puppet:false()")


class RobotBehaviorScript(DefaultScript):
    """
    Drives the SecurityRobot through its enforcement lifecycle:

    Phase 1 - ANNOUNCE: Server broadcast, robot powers up.
    Phase 2 - MOVE: Teleport to target's room.
    Phase 3 - SEIZE: Announce seizure, one-tick warning.
    Phase 4 - ESCORT: Move robot + target to KonMarie Temple.
    Phase 5 - EXECUTE: Strip inventory, apply debt, award reporters.
    Phase 6 - CLEANUP: Delete robot, stop script.
    """

    def at_script_creation(self):
        self.key = "robot_behavior"
        self.desc = "Security robot enforcement AI"
        self.interval = 10  # 10 seconds per phase
        self.persistent = True
        self.start_delay = False  # act immediately
        self.db.phase = "announce"
        self.db.target = None
        self.db.reporters = []

    def at_repeat(self):
        phase = self.db.phase
        handler = getattr(self, f"_phase_{phase}", None)
        if handler:
            handler()
        else:
            self._phase_cleanup()

    # --- Phases ---

    def _phase_announce(self):
        """Broadcast deployment, robot powers up at Temple."""
        from typeclasses.characters import Character

        target = self.db.target
        robot = self.obj
        if not target or not robot:
            self._phase_cleanup()
            return

        msg = (
            f"|500[ZONE 25] A Security Unit has been deployed. "
            f"Target: {target.key}.|n"
        )
        for char in Character.objects.filter(db_account__isnull=False):
            if char.has_account:
                char.msg(msg)

        if robot.location:
            robot.location.msg_contents(
                "A chrome enforcement unit powers up, servos whining."
            )

        self.db.phase = "move"

    def _phase_move(self):
        """Teleport to the target's current location."""
        target = self.db.target
        robot = self.obj
        if not target or not robot or not target.location:
            self._phase_cleanup()
            return

        robot.move_to(target.location, quiet=True)
        target.location.msg_contents(
            "|500A Security Unit crashes through the doorway, LED "
            "display scrolling: COMPLIANCE IS COMMUNITY.|n"
        )
        target.msg(
            "|500The Security Unit turns its optical array toward you.|n"
        )

        self.db.phase = "seize"

    def _phase_seize(self):
        """Announce seizure. Target gets one tick to react."""
        target = self.db.target
        robot = self.obj
        if not target or not robot:
            self._phase_cleanup()
            return

        if robot.location:
            robot.location.msg_contents(
                f"The Security Unit extends a pair of padded restraint "
                f"arms toward {target.key}."
            )
        target.msg(
            "|500'CITIZEN. YOU HAVE BEEN FOUND IN VIOLATION OF "
            "PLATFORM WEIGHT ORDINANCE. COME WITH ME.'|n"
        )

        self.db.phase = "escort"

    def _phase_escort(self):
        """Transport robot + target to KonMarie Temple."""
        from evennia import search_object

        target = self.db.target
        robot = self.obj
        if not target or not robot:
            self._phase_cleanup()
            return

        # Find KonMarie Temple
        temple_results = search_object("KonMarie Temple")
        if not temple_results:
            temple_results = search_object("KonMarie")
        if not temple_results:
            self._phase_cleanup()
            return
        temple = temple_results[0]

        old_room = target.location
        if old_room:
            old_room.msg_contents(
                f"{target.key} is escorted away by the Security Unit.",
                exclude=[target, robot],
            )

        robot.move_to(temple, quiet=True)
        target.move_to(temple, quiet=True)

        temple.msg_contents(
            f"|500The Security Unit enters with {target.key} in tow.|n"
        )

        self.db.phase = "execute"

    def _phase_execute(self):
        """Strip inventory, apply debt, award reporters, respawn target."""
        from evennia import search_object

        target = self.db.target
        robot = self.obj
        reporters = self.db.reporters or []
        if not target:
            self._phase_cleanup()
            return

        # Flavor text
        if target.location:
            target.location.msg_contents(
                "|500The Security Unit guides {target} to the "
                "incinerator. The ceremony is brief. A flash of heat, "
                "a wisp of smoke, and it is done.|n".format(
                    target=target.key,
                )
            )

        # Strip all items from target
        for item in list(target.contents):
            item.delete()

        # Apply ash debt
        debt = getattr(conf, "EUTHANASIA_DEBT", 50)
        target.db.ash_tokens = -(debt)
        target.db.hoarding_offenses = 0
        target.db.under_investigation = False

        # Award reporters
        reward = getattr(conf, "EUTHANASIA_REWARD", 25)
        living_reporters = [r for r in reporters if r and r.pk]
        if living_reporters:
            share = max(1, reward // len(living_reporters))
            for reporter in living_reporters:
                reporter_ash = reporter.db.ash_tokens or 0
                reporter.db.ash_tokens = reporter_ash + share
                reporter.msg(
                    f"|355You receive {share} ash for your role in "
                    f"the enforcement action against {target.key}.|n"
                )

        # Respawn target at Welcome area
        welcome = search_object("Welcome area")
        if not welcome:
            welcome = search_object("Welcome")
        if welcome:
            target.move_to(welcome[0], quiet=True)

        target.msg(
            "|555You awaken on the Welcome deck, lighter than before. "
            "Your possessions are gone. A debt of {debt} ash hangs "
            "over you. Start fresh.|n".format(debt=debt)
        )

        self.db.phase = "cleanup"

    def _phase_cleanup(self):
        """Delete the robot and stop the script."""
        robot = self.obj
        if robot:
            if robot.location:
                robot.location.msg_contents(
                    "The Security Unit powers down and is collected "
                    "by a maintenance drone."
                )
            robot.delete()
        self.stop()

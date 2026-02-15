"""
Commands

Commands describe the input the account can do to the game.

"""

from evennia.commands.command import Command as BaseCommand
from evennia.commands.default.general import CmdGet as DefaultCmdGet
from evennia import default_cmds, syscmdkeys, utils
from evennia.utils.ansi import raw as raw_ansi


class Command(BaseCommand):
    """
    Base command (you may see this if a child command had no help text defined)

    Note that the class's `__doc__` string is used by Evennia to create the
    automatic help entry for the command, so make sure to document consistently
    here. Without setting one, the parent's docstring will show (like now).

    """

    # Each Command class implements the following methods, called in this order
    # (only func() is actually required):
    #
    #     - at_pre_cmd(): If this returns anything truthy, execution is aborted.
    #     - parse(): Should perform any extra parsing needed on self.args
    #         and store the result on self.
    #     - func(): Performs the actual work.
    #     - at_post_cmd(): Extra actions, often things done after
    #         every command, like prompts.
    #
    pass


def _auto_accept_gift(target_id):
    """Auto-accept a pending gift after timeout."""
    from evennia.utils.search import search_object

    results = search_object(f"#{target_id}")
    if not results:
        return
    target = results[0]
    pending = target.ndb.pending_gift
    if not pending:
        return

    item = pending["item"]
    giver = pending["from"]

    if not item or not item.pk:
        target.ndb.pending_gift = None
        return

    item.move_to(target, quiet=True)
    target.msg(f"|355The gift of |w{item.key}|355 has been accepted automatically.|n")
    if giver and giver.pk:
        giver.msg(
            f"|355{target.key} accepted your gift of |w{item.key}|355.|n"
        )
    target.ndb.pending_gift = None


class CmdGift(BaseCommand):
    """
    Offer an item to another player as a gift.

    The recipient can accept or reject the gift. If they don't
    respond within 60 seconds, the gift is accepted automatically.

    Usage:
      gift <item> to <player>
    """

    key = "gift"
    help_category = "Social"
    locks = "cmd:all()"

    def func(self):
        from evennia.utils import delay

        args = self.args.strip()
        if " to " not in args:
            self.caller.msg("Usage: gift <item> to <player>")
            return

        item_name, _, target_name = args.partition(" to ")
        item_name = item_name.strip()
        target_name = target_name.strip()

        item = self.caller.search(item_name, location=self.caller)
        if not item:
            return
        target = self.caller.search(target_name)
        if not target:
            return

        if not target.is_typeclass(
            "typeclasses.characters.Character", exact=False
        ):
            self.caller.msg("You can only gift items to other citizens.")
            return

        if target == self.caller:
            self.caller.msg("You can't gift something to yourself.")
            return

        # Check if target already has a pending gift
        if target.ndb.pending_gift:
            self.caller.msg(
                f"{target.key} already has a gift offer pending."
            )
            return

        # Clear display attributes if the item was displayed
        if item.db.displayed:
            del item.db.displayed
        original = item.db.original_weight_fraction
        if original is not None:
            item.db.weight_fraction = original
            del item.db.original_weight_fraction

        # Hold the item in limbo while pending
        item.move_to(None, quiet=True)

        target.ndb.pending_gift = {
            "item": item,
            "from": self.caller,
        }

        self.caller.msg(
            f"|355You offer |w{item.key}|355 to {target.key} as a gift.|n"
        )
        target.msg(
            f"|355{self.caller.key} offers you |w{item.key}|355 as a gift. "
            f"Use |555accept|n|355 or |555reject|n|355.|n"
        )
        self.caller.location.msg_contents(
            f"|355$You() $conj(offer) |w{item.key}|355 "
            f"to {target.key} as a gift.|n",
            from_obj=self.caller,
            exclude=[self.caller, target],
        )

        # Auto-accept after 60 seconds
        delay(60, _auto_accept_gift, target.id)


class CmdAcceptGift(BaseCommand):
    """
    Accept a pending gift from another player.

    Usage:
      accept
    """

    key = "accept"
    help_category = "Social"
    locks = "cmd:all()"

    def func(self):
        pending = self.caller.ndb.pending_gift
        if not pending:
            self.caller.msg("You have no pending gift to accept.")
            return

        item = pending["item"]
        giver = pending["from"]
        self.caller.ndb.pending_gift = None

        if not item or not item.pk:
            self.caller.msg("The offered item no longer exists.")
            return

        item.move_to(self.caller, quiet=True)

        self.caller.msg(
            f"|355You accept |w{item.key}|355 from {giver.key}.|n"
        )
        if giver and giver.pk:
            giver.msg(
                f"|355{self.caller.key} accepted your gift of "
                f"|w{item.key}|355.|n"
            )
        if self.caller.location:
            self.caller.location.msg_contents(
                f"|355$You() $conj(accept) a gift of |w{item.key}|355 "
                f"from {giver.key}.|n",
                from_obj=self.caller,
                exclude=[self.caller, giver],
            )


class CmdRejectGift(BaseCommand):
    """
    Reject a pending gift, returning it to the giver.

    Usage:
      reject
    """

    key = "reject"
    help_category = "Social"
    locks = "cmd:all()"

    def func(self):
        pending = self.caller.ndb.pending_gift
        if not pending:
            self.caller.msg("You have no pending gift to reject.")
            return

        item = pending["item"]
        giver = pending["from"]
        self.caller.ndb.pending_gift = None

        if not item or not item.pk:
            self.caller.msg("The offered item no longer exists.")
            return

        # Return to giver if they still exist
        if giver and giver.pk:
            item.move_to(giver, quiet=True)
            giver.msg(
                f"|y{self.caller.key} declined your gift of "
                f"|w{item.key}|y. It has been returned.|n"
            )
        else:
            # Giver gone — drop in the room
            if self.caller.location:
                item.move_to(self.caller.location, quiet=True)

        self.caller.msg(
            f"|yYou decline the gift of |w{item.key}|y from "
            f"{giver.key if giver else 'someone'}.|n"
        )
        if self.caller.location:
            self.caller.location.msg_contents(
                f"|y$You() $conj(decline) a gift from "
                f"{giver.key if giver else 'someone'}.|n",
                from_obj=self.caller,
                exclude=[self.caller, giver] if giver else [self.caller],
            )


class CmdAsh(BaseCommand):
    """
    Check your ash token balance.

    Usage:
      ash
    """

    key = "ash"
    help_category = "Economy"
    locks = "cmd:all()"

    def func(self):
        tokens = self.caller.db.ash_tokens or 0
        self.caller.msg(f"You have {tokens} ash.")


class CmdScore(BaseCommand):
    """
    View your personal status summary.

    Shows your ash balance, item count, hoarding standing,
    and the current platform danger level.

    Usage:
      score
      status
    """

    key = "score"
    aliases = ["status"]
    help_category = "General"
    locks = "cmd:all()"

    def func(self):
        from django.conf import settings as conf
        from world.zone_monitor import (
            get_item_count,
            get_danger_level,
            get_player_item_count,
        )

        caller = self.caller
        ash = caller.db.ash_tokens or 0
        items_carried = len(caller.contents)
        total_items = get_player_item_count(caller)
        offenses = caller.db.hoarding_offenses or 0
        under_inv = caller.db.under_investigation or False

        count = get_item_count()
        level, _, limit = get_danger_level(count)

        level_colors = {
            "safe": "|g",
            "warning": "|y",
            "critical": "|500",
            "sinking": "|[500|555",
        }
        color = level_colors.get(level, "|n")

        minor_thresh = getattr(conf, "HOARDING_MINOR_THRESHOLD", 10)
        if under_inv:
            standing = "|500UNDER INVESTIGATION|n"
        elif offenses > 0:
            standing = f"|y{offenses} offense(s)|n"
        elif total_items >= minor_thresh:
            standing = "|yAt risk|n"
        else:
            standing = "|gClean|n"

        text = (
            f"\n|b--- Citizen Status ---|n"
            f"\n Ash balance: |y{ash}|n"
            f"\n Items carried: {items_carried}"
            f"\n Total items (incl. shelves): {total_items}"
            f"\n Hoarding standing: {standing}"
            f"\n"
            f"\n|b--- Zone 25 ---|n"
            f"\n Platform: {color}{level.upper()}|n"
            f" ({count}/{limit} items)"
            f"\n"
        )
        caller.msg(text)


class CmdInventory(default_cmds.MuxCommand):
    """
    View your inventory and ash balance.

    Usage:
      inventory
      inv
      i
    """

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        items = self.caller.contents
        ash = self.caller.db.ash_tokens or 0
        if not items:
            string = "You are not carrying anything."
        else:
            table = self.styled_table(border="header")
            for key, desc, _ in utils.group_objects_by_key_and_desc(
                items, caller=self.caller
            ):
                table.add_row(
                    f"|C{key}|n",
                    "{}|n".format(
                        utils.crop(raw_ansi(desc or ""), width=50) or ""
                    ),
                )
            string = f"|wYou are carrying:\n{table}"
        string += f"\n|yAsh: {ash}|n"
        self.msg(text=(string, {"type": "inventory"}))


class CmdReport(BaseCommand):
    """
    Report a player for hoarding items on the platform.

    Minor hoarders receive escalating fines. Major hoarders trigger
    a formal investigation that may end with the security robot.

    Usage:
      report <player>
    """

    key = "report"
    help_category = "Rules"
    locks = "cmd:all()"

    def func(self):
        from django.conf import settings as conf

        if not self.args:
            self.caller.msg("Report whom? Usage: report <player>")
            return

        target = self.caller.search(self.args.strip())
        if not target:
            return

        # Must be a character
        if not target.is_typeclass(
            "typeclasses.characters.Character", exact=False
        ):
            self.caller.msg("You can only report other citizens.")
            return

        if target == self.caller:
            self.caller.msg("You can't report yourself.")
            return

        # Count target's inventory + claimed shelf items
        from world.zone_monitor import get_player_item_count

        item_count = get_player_item_count(target)
        minor_threshold = getattr(conf, "HOARDING_MINOR_THRESHOLD", 10)
        major_threshold = getattr(conf, "HOARDING_MAJOR_THRESHOLD", 20)

        if item_count < minor_threshold:
            self.caller.msg(
                f"{target.key} is carrying {item_count} items -- "
                f"they don't seem to be hoarding."
            )
            return

        # Already under investigation? Add reporter and speed up.
        if target.db.under_investigation:
            from evennia.scripts.models import ScriptDB

            try:
                inv_script = ScriptDB.objects.get(
                    db_key=f"investigation_{target.id}"
                )
                inv_script.add_reporter(self.caller)
                remaining = inv_script.db.ticks_remaining
                self.caller.msg(
                    f"|yYour report has been added to the ongoing "
                    f"investigation of {target.key}. "
                    f"{remaining} cycle(s) remain.|n"
                )
            except ScriptDB.DoesNotExist:
                self.caller.msg(
                    f"{target.key} is already under investigation."
                )
            return

        # Determine tier
        if item_count >= major_threshold:
            self._start_investigation(target)
            return

        # --- Tier 1: escalating fines ---
        offenses = target.db.hoarding_offenses or 0
        fine_schedule = getattr(
            conf, "HOARDING_FINE_SCHEDULE", [5, 15, 0]
        )

        if offenses < len(fine_schedule):
            fine = fine_schedule[offenses]
        else:
            fine = 0  # escalate

        if fine == 0:
            # Third strike -- escalate to investigation
            self.caller.msg(
                f"|500Third offense for {target.key}. "
                f"A formal investigation has been opened.|n"
            )
            target.msg(
                "|500Third offense. A formal investigation has been "
                "opened against you.|n"
            )
            self._start_investigation(target)
            return

        # Apply fine — recycle into station pool to prevent deflation
        from world.economy import credit_station_pool

        ash = target.db.ash_tokens or 0
        target.db.ash_tokens = ash - fine
        target.db.hoarding_offenses = offenses + 1
        credit_station_pool(fine)

        if offenses == 0:
            target.msg(
                f"|500You have been reported for hoarding "
                f"({item_count} items). A fine of {fine} ash has "
                f"been deducted. Consider visiting the KonMarie "
                f"Temple.|n"
            )
            self.caller.location.msg_contents(
                f"|y{target.key} has been cited for suspected hoarding. "
                f"A fine of {fine} ash has been levied.|n",
                exclude=[target],
            )
        else:
            target.msg(
                f"|500Offense #{offenses + 1}. {fine} ash deducted. "
                f"Further violations will trigger a formal "
                f"investigation.|n"
            )
            self.caller.location.msg_contents(
                f"|y{target.key} has been cited for hoarding again. "
                f"A fine of {fine} ash has been levied.|n",
                exclude=[target],
            )

        self.caller.msg(
            f"You report {target.key} for hoarding. "
            f"Fine of {fine} ash applied."
        )

    def _start_investigation(self, target):
        """Open a formal investigation against *target*."""
        from evennia import create_script

        target.db.under_investigation = True

        create_script(
            "typeclasses.scripts.InvestigationScript",
            key=f"investigation_{target.id}",
            obj=target,
            persistent=True,
            attributes=[
                ("target", target),
                ("reporters", [self.caller]),
            ],
        )

        # Server-wide broadcast
        from typeclasses.characters import Character

        msg = (
            f"|y[ZONE 25 ENFORCEMENT] {target.key} is under "
            f"investigation for hoarding.|n"
        )
        for char in Character.objects.filter(db_account__isnull=False):
            if char.has_account:
                char.msg(msg)

        self.caller.msg(
            f"You file a formal hoarding report against {target.key}. "
            f"An investigation has begun."
        )


class CmdGet(DefaultCmdGet):
    """
    Pick up something.

    Usage:
      get <obj>
      get <number> <obj>     - pick up multiple identical items
      get all                - pick up everything you can
      get all <obj>          - pick up all matching items

    Examples:
      get casein powder
      get 3 casein powder
      get all casein
      get all
    """

    def func(self):
        caller = self.caller

        if not self.args:
            self.msg("Get what?")
            return

        args = self.args.strip()

        # Handle "get all" and "get all <name>"
        if args.lower() == "all" or args.lower().startswith("all "):
            self._get_all(args)
            return

        # Default Evennia CmdGet behavior (supports "get 3 casein powder")
        super().func()

    def _get_all(self, args):
        """Pick up all objects, or all matching a name."""
        caller = self.caller
        location = caller.location
        if not location:
            return

        filter_name = ""
        if args.lower() != "all":
            filter_name = args[4:].strip().lower()

        # Collect gettable items from the room
        candidates = [
            obj for obj in location.contents
            if obj != caller
            and not getattr(obj, "destination", None)  # skip exits
            and obj.access(caller, "get")
        ]

        if filter_name:
            candidates = [
                obj for obj in candidates
                if filter_name in obj.key.lower()
                or any(filter_name in a.lower()
                       for a in obj.aliases.all())
            ]

        if not candidates:
            if filter_name:
                self.msg(f"You can't find any '{filter_name}' to pick up.")
            else:
                self.msg("There's nothing here to pick up.")
            return

        moved = []
        for obj in candidates:
            if not obj.at_pre_get(caller):
                continue
            if obj.move_to(caller, quiet=True, move_type="get"):
                obj.at_get(caller)
                moved.append(obj)

        if not moved:
            self.msg("You couldn't pick anything up.")
            return

        # Group by name for a clean message
        from collections import Counter
        counts = Counter(obj.key for obj in moved)
        parts = []
        for name, count in counts.items():
            if count > 1:
                parts.append(f"{count} {name}")
            else:
                parts.append(name)

        item_str = ", ".join(parts)
        caller.location.msg_contents(
            f"$You() $conj(pick) up {item_str}.",
            from_obj=caller,
        )


class CmdAutoMultimatch(default_cmds.MuxCommand):
    """
    Auto-resolve command disambiguation when args exactly match an
    object's name.  Falls back to the normal numbered prompt otherwise.
    """

    key = syscmdkeys.CMD_MULTIMATCH
    locks = "cmd:all()"

    def func(self):
        matches = self.matches
        if not matches:
            return

        # Args are the same across all match tuples (index 1).
        args = matches[0][1].strip().lower()

        if args:
            for _cmdname, _args, cmdobj, *_rest in matches:
                obj = getattr(cmdobj, "obj", None)
                if obj is None:
                    continue
                # Exact match on key or any alias → run that command
                if obj.key.lower() == args or args in [
                    a.lower() for a in obj.aliases.all()
                ]:
                    # Copy runtime attributes from the system command
                    # (which was properly initialized by the handler)
                    # onto the matched command before executing it.
                    cmdobj.caller = self.caller
                    cmdobj.session = self.session
                    cmdobj.cmdset = self.cmdset
                    cmdobj.raw_string = self.raw_string
                    cmdobj.cmdstring = _cmdname
                    cmdobj.args = _args
                    cmdobj.parse()
                    cmdobj.func()
                    return

        # No exact match — show numbered list with usage hint.
        lines = []
        obj_names = []
        for i, (_cmdname, _args, cmdobj, *_rest) in enumerate(matches, 1):
            obj = getattr(cmdobj, "obj", None)
            label = f" (on {obj.key})" if obj else ""
            lines.append(f" {i}-{_cmdname}{label}")
            if obj:
                obj_names.append((_cmdname, obj.key))
        self.caller.msg(
            "More than one match:\n" + "\n".join(lines)
        )
        # Suggest typing the command with the object name
        if obj_names:
            example = obj_names[0]
            self.caller.msg(
                f"|555Hint: try |n{example[0]} {example[1]}"
            )


# -------------------------------------------------------------
#
# The default commands inherit from
#
#   evennia.commands.default.muxcommand.MuxCommand.
#
# If you want to make sweeping changes to default commands you can
# uncomment this copy of the MuxCommand parent and add
#
#   COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"
#
# to your settings file. Be warned that the default commands expect
# the functionality implemented in the parse() method, so be
# careful with what you change.
#
# -------------------------------------------------------------

# from evennia.utils import utils
#
#
# class MuxCommand(Command):
#     """
#     This sets up the basis for a MUX command. The idea
#     is that most other Mux-related commands should just
#     inherit from this and don't have to implement much
#     parsing of their own unless they do something particularly
#     advanced.
#
#     Note that the class's __doc__ string (this text) is
#     used by Evennia to create the automatic help entry for
#     the command, so make sure to document consistently here.
#     """
#     def has_perm(self, srcobj):
#         """
#         This is called by the cmdhandler to determine
#         if srcobj is allowed to execute this command.
#         We just show it here for completeness - we
#         are satisfied using the default check in Command.
#         """
#         return super().has_perm(srcobj)
#
#     def at_pre_cmd(self):
#         """
#         This hook is called before self.parse() on all commands
#         """
#         pass
#
#     def at_post_cmd(self):
#         """
#         This hook is called after the command has finished executing
#         (after self.func()).
#         """
#         pass
#
#     def parse(self):
#         """
#         This method is called by the cmdhandler once the command name
#         has been identified. It creates a new set of member variables
#         that can be later accessed from self.func() (see below)
#
#         The following variables are available for our use when entering this
#         method (from the command definition, and assigned on the fly by the
#         cmdhandler):
#            self.key - the name of this command ('look')
#            self.aliases - the aliases of this cmd ('l')
#            self.permissions - permission string for this command
#            self.help_category - overall category of command
#
#            self.caller - the object calling this command
#            self.cmdstring - the actual command name used to call this
#                             (this allows you to know which alias was used,
#                              for example)
#            self.args - the raw input; everything following self.cmdstring.
#            self.cmdset - the cmdset from which this command was picked. Not
#                          often used (useful for commands like 'help' or to
#                          list all available commands etc)
#            self.obj - the object on which this command was defined. It is often
#                          the same as self.caller.
#
#         A MUX command has the following possible syntax:
#
#           name[ with several words][/switch[/switch..]] arg1[,arg2,...] [[=|,] arg[,..]]
#
#         The 'name[ with several words]' part is already dealt with by the
#         cmdhandler at this point, and stored in self.cmdname (we don't use
#         it here). The rest of the command is stored in self.args, which can
#         start with the switch indicator /.
#
#         This parser breaks self.args into its constituents and stores them in the
#         following variables:
#           self.switches = [list of /switches (without the /)]
#           self.raw = This is the raw argument input, including switches
#           self.args = This is re-defined to be everything *except* the switches
#           self.lhs = Everything to the left of = (lhs:'left-hand side'). If
#                      no = is found, this is identical to self.args.
#           self.rhs: Everything to the right of = (rhs:'right-hand side').
#                     If no '=' is found, this is None.
#           self.lhslist - [self.lhs split into a list by comma]
#           self.rhslist - [list of self.rhs split into a list by comma]
#           self.arglist = [list of space-separated args (stripped, including '=' if it exists)]
#
#           All args and list members are stripped of excess whitespace around the
#           strings, but case is preserved.
#         """
#         raw = self.args
#         args = raw.strip()
#
#         # split out switches
#         switches = []
#         if args and len(args) > 1 and args[0] == "/":
#             # we have a switch, or a set of switches. These end with a space.
#             switches = args[1:].split(None, 1)
#             if len(switches) > 1:
#                 switches, args = switches
#                 switches = switches.split('/')
#             else:
#                 args = ""
#                 switches = switches[0].split('/')
#         arglist = [arg.strip() for arg in args.split()]
#
#         # check for arg1, arg2, ... = argA, argB, ... constructs
#         lhs, rhs = args, None
#         lhslist, rhslist = [arg.strip() for arg in args.split(',')], []
#         if args and '=' in args:
#             lhs, rhs = [arg.strip() for arg in args.split('=', 1)]
#             lhslist = [arg.strip() for arg in lhs.split(',')]
#             rhslist = [arg.strip() for arg in rhs.split(',')]
#
#         # save to object properties:
#         self.raw = raw
#         self.switches = switches
#         self.args = args.strip()
#         self.arglist = arglist
#         self.lhs = lhs
#         self.lhslist = lhslist
#         self.rhs = rhs
#         self.rhslist = rhslist
#
#         # if the class has the account_caller property set on itself, we make
#         # sure that self.caller is always the account if possible. We also create
#         # a special property "character" for the puppeted object, if any. This
#         # is convenient for commands defined on the Account only.
#         if hasattr(self, "account_caller") and self.account_caller:
#             if utils.inherits_from(self.caller, "evennia.objects.objects.DefaultObject"):
#                 # caller is an Object/Character
#                 self.character = self.caller
#                 self.caller = self.caller.account
#             elif utils.inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount"):
#                 # caller was already an Account
#                 self.character = self.caller.get_puppet(self.session)
#             else:
#                 self.character = None

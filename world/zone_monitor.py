"""
Zone 25 Platform Monitor - shared utilities.

Provides item counting, danger level calculation, and echo/message text
used by the ItemMonitorScript, OutdoorRoom weather system, and Counter sign.

All threshold logic lives here. Nothing else duplicates it.
"""

from django.conf import settings
from evennia.objects.models import ObjectDB


# --- Danger Levels -----------------------------------------------------------

LEVEL_SAFE = "safe"
LEVEL_WARNING = "warning"
LEVEL_CRITICAL = "critical"
LEVEL_SINKING = "sinking"

# Thresholds as fractions of ZONE_ITEM_LIMIT
THRESHOLDS = {
    LEVEL_WARNING: 0.75,
    LEVEL_CRITICAL: 0.90,
    LEVEL_SINKING: 1.0,
}

# Typeclass paths excluded from the item count
EXCLUDED_TYPECLASSES = [
    "typeclasses.rooms.Room",
    "typeclasses.rooms.OutdoorRoom",
    "typeclasses.rooms.LaserRoom",
    "typeclasses.exits.Exit",
    "typeclasses.characters.Character",
    "typeclasses.objects.DisplayShelf",
    "typeclasses.npcs.SecurityRobot",
]


# --- Core Functions ----------------------------------------------------------


def get_item_count():
    """
    Return the weighted number of 'items' on the platform.
    Excludes rooms, exits, characters, and fixture objects (shelves, etc.).
    Materials count at fractional weight (default 1/3).
    Displayed items count at DISPLAY_WEIGHT_FRACTION (default 0.5).
    Masterpieces count at MASTERPIECE_WEIGHT_FRACTION (default 0.5).
    """
    from evennia.utils.search import search_object_attribute
    from world.materials import MATERIAL_WEIGHT_FRACTION

    DISPLAY_WEIGHT = getattr(settings, "DISPLAY_WEIGHT_FRACTION", 0.5)
    MASTERPIECE_WEIGHT = getattr(settings, "MASTERPIECE_WEIGHT_FRACTION", 0.5)

    total = ObjectDB.objects.all().count()
    excluded = ObjectDB.objects.filter(
        db_typeclass_path__in=EXCLUDED_TYPECLASSES
    ).count()
    raw_items = total - excluded

    # Materials are already counted in raw_items as 1 each.
    # Adjust them down to their fractional weight.
    material_objs = search_object_attribute(
        key="material", category=None, value=True
    )
    material_count = len(material_objs)

    weighted = raw_items - material_count + (material_count * MATERIAL_WEIGHT_FRACTION)

    # Displayed items (non-material) count at reduced weight.
    displayed_objs = search_object_attribute(
        key="displayed", category=None, value=True
    )
    display_only = [o for o in displayed_objs if not o.db.material]
    display_count = len(display_only)
    weighted = weighted - display_count + (display_count * DISPLAY_WEIGHT)

    # Masterpieces (non-displayed, non-material) count at reduced weight.
    masterpiece_objs = search_object_attribute(
        key="artwork", category=None, value="true"
    )
    masterpiece_only = [
        o for o in masterpiece_objs
        if not o.db.material and not o.db.displayed
    ]
    masterpiece_count = len(masterpiece_only)
    weighted = weighted - masterpiece_count + (masterpiece_count * MASTERPIECE_WEIGHT)

    # Player body weight -- each connected character adds fixed weight
    from typeclasses.characters import Character

    PLAYER_WEIGHT = getattr(settings, "PLAYER_BODY_WEIGHT", 5)
    player_count = Character.objects.filter(
        db_account__isnull=False
    ).count()
    weighted += player_count * PLAYER_WEIGHT

    return int(weighted)


def get_danger_level(count=None):
    """
    Return (level, count, limit) based on current item count.

    Args:
        count: optional pre-computed item count. If None, queries the DB.

    Returns:
        tuple: (level_key, count, limit)
    """
    if count is None:
        count = get_item_count()
    limit = getattr(settings, "ZONE_ITEM_LIMIT", 1000)
    ratio = count / max(limit, 1)

    if ratio >= THRESHOLDS[LEVEL_SINKING]:
        level = LEVEL_SINKING
    elif ratio >= THRESHOLDS[LEVEL_CRITICAL]:
        level = LEVEL_CRITICAL
    elif ratio >= THRESHOLDS[LEVEL_WARNING]:
        level = LEVEL_WARNING
    else:
        level = LEVEL_SAFE

    return (level, count, limit)


def get_item_monitor():
    """
    Return the ItemMonitorScript singleton, or None if not yet created.
    Used by OutdoorRoom to read the cached danger level without a DB query.
    """
    from evennia.scripts.models import ScriptDB

    try:
        return ScriptDB.objects.get(db_key="item_monitor")
    except ScriptDB.DoesNotExist:
        return None


def get_player_item_count(char):
    """
    Return the number of items attributable to *char*: inventory contents
    plus items on any DisplayShelf they have claimed.
    """
    from typeclasses.objects import DisplayShelf

    count = len(list(char.contents))
    for shelf in DisplayShelf.objects.all():
        if shelf.db.shelf_owner == char:
            shelf_items = [
                o for o in shelf.contents
                if not getattr(o, "destination", None)
            ]
            count += len(shelf_items)
    return count


def get_unowned_item_count():
    """
    Count items sitting in rooms (not in inventories or on shelves)
    that have a ``last_holder`` attribute -- i.e. stashed / abandoned items.
    """
    from evennia.utils.search import search_object_attribute

    stashed = search_object_attribute(key="last_holder", category=None)
    count = 0
    for obj in stashed:
        loc = obj.location
        if loc and loc.is_typeclass("typeclasses.rooms.Room", exact=False):
            count += 1
    return count


# --- Broadcast messages (for ItemMonitorScript) ------------------------------

BROADCAST_MESSAGES = {
    LEVEL_WARNING: [
        "|yCaution: The platform is carrying {count}/{limit} items. "
        "Consider visiting the KonMarie Temple.|n",
        "|yA structural groan echoes through the corridors. "
        "{count} items aboard -- the platform is getting heavy.|n",
    ],
    LEVEL_CRITICAL: [
        "|500WARNING: {count}/{limit} items on the platform! "
        "Structural integrity is compromised. Incinerate excess items!|n",
        "|500The floor trembles beneath your feet. {count} items and counting "
        "-- Zone 25 cannot take much more.|n",
    ],
    LEVEL_SINKING: [
        "|[500|555EMERGENCY: Zone 25 is OVER CAPACITY ({count}/{limit})! "
        "The platform is taking on water! INCINERATE NOW!|n",
        "|[500|555HULL BREACH IMMINENT. {count} items -- {over} OVER THE LIMIT. "
        "Get to the KonMarie Temple!|n",
    ],
}


# --- Ominous echoes (blended into OutdoorRoom weather) -----------------------

OMINOUS_ECHOES = {
    LEVEL_WARNING: [
        "The deck plates creak underfoot.",
        "A faint metallic groan rises from below.",
        "The gulls have gone quiet.",
        "The horizon tilts slightly, then rights itself.",
    ],
    LEVEL_CRITICAL: [
        "|yThe platform shudders. Water sloshes somewhere below.|n",
        "|yA deep, grinding vibration passes through the deck plates.|n",
        "|yThe railing is wet -- and the sea seems closer than before.|n",
        "|yRivets pop somewhere in the superstructure. The gulls are gone.|n",
    ],
    LEVEL_SINKING: [
        "|500The deck lurches. Seawater spills over the outer railing.|n",
        "|500A klaxon wails in the distance. The platform lists to port.|n",
        "|500Water is rising through the deck grates. This is not a drill.|n",
        "|500The horizon is wrong. The ocean is climbing the hull.|n",
    ],
}

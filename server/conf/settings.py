r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

import sys
from pathlib import Path

_SERVER_LIB = str(Path(__file__).resolve().parent.parent / "lib")
if _SERVER_LIB not in sys.path:
    sys.path.insert(0, _SERVER_LIB)

######################################################################
# Evennia base server config
######################################################################

SERVERNAME = "Sea of Objects"
GAME_SLOGAN = "v1.0"

# New characters start in the Welcome area
START_LOCATION = "#4"
DEFAULT_HOME = "#4"

######################################################################
# Zone 25 platform limits
######################################################################

ZONE_ITEM_LIMIT = 1000
DISPLAY_WEIGHT_FRACTION = 0.5
MASTERPIECE_WEIGHT_FRACTION = 0.5

######################################################################
# IRC bridge
######################################################################

IRC_ENABLED = True

######################################################################
# FuncParser (replaces old INLINEFUNC_ENABLED)
######################################################################

FUNCPARSER_PARSE_OUTGOING_MESSAGES_ENABLED = True

######################################################################
# Gametime settings
######################################################################

TIME_IGNORE_DOWNTIMES = True
TIME_FACTOR = 1.0
TIME_ZONE = "America/Chicago"
USE_TZ = True

######################################################################
# RP System - regex for multi-match separation (e.g. 1-tall, 2-tall)
######################################################################

SEARCH_MULTIMATCH_REGEX = r"(?P<number>[0-9]+)-(?P<name>[^-]*)(?P<args>.*)"
SEARCH_MULTIMATCH_TEMPLATE = " {number}-{name}{aliases}{info}\n"

######################################################################
# Economy settings
######################################################################

# Station ash pool
STATION_INITIAL_ASH_POOL = 500
STATION_MAX_ASH_POOL = 2000

# Shop pricing (buy = player pays, sell = player receives)
SHOP_BASE_PRICE = 5
SHOP_GARMENT_PRICE = 12
SHOP_MASTERPIECE_PRICE = 50
SHOP_FOOD_PRICE = 4
SHOP_BOOK_PRICE = 4
SHOP_CURSED_BUY_PRICE = 2
SHOP_CURSED_SELL_PRICE = 4
SHOP_SELL_FRACTION = 0.4

# Shop restocking
SHOP_RESTOCK_INTERVAL = 600  # seconds between restock checks (10 min)
SHOP_MAX_INVENTORY = 8
SHOP_RESTOCK_COUNT = 3

# Incinerator ash rewards
ASH_REWARD_NORMAL = 1
ASH_REWARD_ARTWORK = 3
ASH_REWARD_CURSED = 2   # reduced from 5 to curb farming incentive

# Itemator cost
ITEMATOR_COST = 1  # ash tokens per itemator/material womb use

# Shop item expiry
SHOP_ITEM_TTL = 3600  # seconds before unsold shop items expire (60 min)

# Station pool passive recharge
STATION_ASH_RECHARGE = 5  # ash added to station pool per monitor tick (3 min)

# Player weight
PLAYER_BODY_WEIGHT = 5  # weight units per connected character

# Hoarding enforcement
HOARDING_MINOR_THRESHOLD = 10   # items in inventory for minor offense
HOARDING_MAJOR_THRESHOLD = 20   # items in inventory for major offense
HOARDING_FINE_SCHEDULE = [5, 15, 0]  # ash fines: 1st, 2nd, 3rd (0 = escalate)
INVESTIGATION_TICKS = 5
INVESTIGATION_INTERVAL = 60     # seconds per tick
INVESTIGATION_SPEEDUP_PER_REPORT = 1  # ticks removed per additional reporter
EUTHANASIA_REWARD = 25          # ash tokens split among reporters
EUTHANASIA_DEBT = 50            # negative ash balance on respawn

# Cafetorium ration dispenser
RATION_DAILY_LIMIT = 3          # free rations per player per day

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")

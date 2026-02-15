"""
Zone 25 Economy - shared utilities.

Provides station ash pool management, item pricing, and shop inventory
generation. Used by shops, the Counter sign, and enforcement systems.
"""

import random

from django.conf import settings


# ---------------------------------------------------------------------------
# Station ash pool (stored on the ItemMonitorScript singleton)
# ---------------------------------------------------------------------------


def _get_pool_script():
    """Return the ItemMonitorScript singleton."""
    from world.zone_monitor import get_item_monitor

    return get_item_monitor()


def get_station_pool():
    """Return the station's current ash token reserve."""
    script = _get_pool_script()
    if script:
        return script.db.station_ash_pool or 0
    return 0


def debit_station_pool(amount):
    """
    Subtract *amount* from the station pool.

    Returns True on success, False if insufficient funds.
    """
    script = _get_pool_script()
    if not script:
        return False
    current = script.db.station_ash_pool or 0
    if current < amount:
        return False
    script.db.station_ash_pool = current - amount
    return True


def credit_station_pool(amount):
    """Add *amount* to the station pool (capped at STATION_MAX_ASH_POOL)."""
    script = _get_pool_script()
    if not script:
        return
    cap = getattr(settings, "STATION_MAX_ASH_POOL", 2000)
    current = script.db.station_ash_pool or 0
    script.db.station_ash_pool = min(current + amount, cap)


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------

# Expected baseline counts per category. When the platform has exactly
# this many of a type, the scarcity modifier is 1.0 (no change).
# Fewer → prices rise (up to 3x). More → prices fall (down to 0.25x).
SCARCITY_BASELINES = {
    "cursed": 5,
    "artwork": 10,
    "garment": 20,
    "food": 15,
    "book": 15,
    "base": 30,
}

SCARCITY_MIN = 0.25
SCARCITY_MAX = 3.0


def _get_item_category(obj):
    """Return the pricing category string for *obj*."""
    if obj.db.cursed:
        return "cursed"
    if obj.db.artwork:
        return "artwork"
    if "clothing" in obj.typeclass_path.lower():
        return "garment"
    key_lower = obj.key.lower()
    if "cheese" in key_lower or "ice cream" in key_lower or obj.db.edible:
        return "food"
    if "book" in key_lower or obj.db.readable_text:
        return "book"
    return "base"


def _count_category(category):
    """Count how many items of *category* exist on the platform."""
    from evennia.objects.models import ObjectDB
    from evennia.utils.search import search_object_attribute

    if category == "cursed":
        return len(search_object_attribute(key="cursed", category=None, value="true"))
    if category == "artwork":
        return len(search_object_attribute(key="artwork", category=None, value="true"))
    if category == "garment":
        return ObjectDB.objects.filter(
            db_typeclass_path__icontains="clothing"
        ).count()
    if category == "food":
        return len(search_object_attribute(key="edible", category=None, value=True))
    if category == "book":
        return len(search_object_attribute(key="readable_text", category=None))
    # base: everything else is hard to count precisely, use a rough estimate
    return max(1, SCARCITY_BASELINES["base"])


def _scarcity_multiplier(category):
    """
    Return a price multiplier based on how many items of *category*
    exist vs. the expected baseline.

    - At baseline count: 1.0x
    - At zero: SCARCITY_MAX (3.0x)
    - At 2x baseline: ~SCARCITY_MIN (0.25x)

    Uses inverse proportion: multiplier = baseline / count, clamped.
    """
    baseline = SCARCITY_BASELINES.get(category, 30)
    count = _count_category(category)
    if count <= 0:
        return SCARCITY_MAX
    raw = baseline / count
    return max(SCARCITY_MIN, min(SCARCITY_MAX, raw))


def _base_buy_price(obj):
    """Return the base (pre-scarcity) buy price for *obj*."""
    category = _get_item_category(obj)
    if category == "cursed":
        return getattr(settings, "SHOP_CURSED_BUY_PRICE", 2)
    if category == "artwork":
        return getattr(settings, "SHOP_MASTERPIECE_PRICE", 50)
    if category == "garment":
        return getattr(settings, "SHOP_GARMENT_PRICE", 12)
    if category == "food":
        return getattr(settings, "SHOP_FOOD_PRICE", 4)
    if category == "book":
        return getattr(settings, "SHOP_BOOK_PRICE", 4)
    return getattr(settings, "SHOP_BASE_PRICE", 5)


def get_buy_price(obj):
    """
    Price for a player to BUY an item from a shop.

    Base price is modified by scarcity: rare items cost more,
    abundant items cost less. Multiplier range: 0.25x to 3x.
    """
    base = _base_buy_price(obj)
    category = _get_item_category(obj)
    mult = _scarcity_multiplier(category)
    return max(1, int(base * mult))


# Which item categories each shop type will buy from players.
SHOP_ACCEPTED_CATEGORIES = {
    "boutique": {"artwork", "garment", "base"},
    "food": {"food", "base"},
    "general": {"base", "garment", "book", "artwork"},
}


def shop_accepts_item(shop_type, obj):
    """Return True if a shop of *shop_type* will buy *obj*."""
    accepted = SHOP_ACCEPTED_CATEGORIES.get(shop_type)
    if not accepted:
        return True  # unknown shop type accepts everything
    return _get_item_category(obj) in accepted


def get_sell_price(obj):
    """
    Price the station pays a player for an item.

    Cursed items have an inverted premium -- the station pays *more*
    to get them out of circulation. All prices are modified by scarcity.
    """
    category = _get_item_category(obj)
    if category == "cursed":
        base_sell = getattr(settings, "SHOP_CURSED_SELL_PRICE", 4)
        mult = _scarcity_multiplier(category)
        return max(1, int(base_sell * mult))
    buy = get_buy_price(obj)
    fraction = getattr(settings, "SHOP_SELL_FRACTION", 0.4)
    return max(1, int(buy * fraction))


# ---------------------------------------------------------------------------
# Shop inventory generation
# ---------------------------------------------------------------------------

# Weights for each shop type -> list of (generator_key, weight) tuples.
SHOP_TYPE_WEIGHTS = {
    "boutique": [
        ("art", 50),
        ("garment", 40),
        ("talisman", 10),
    ],
    "food": [
        ("cheese", 30),
        ("ice_cream", 30),
        ("candy", 30),
        ("talisman", 10),
    ],
    "general": [
        ("talisman", 30),
        ("garment", 25),
        ("scifi_book", 20),
        ("poem", 15),
        ("art", 10),
    ],
}


def _weighted_choice(weights):
    """Pick a generator key from a list of (key, weight) tuples."""
    keys = [k for k, _ in weights]
    values = [w for _, w in weights]
    return random.choices(keys, weights=values, k=1)[0]


def generate_shop_inventory(shop_type, count=3):
    """
    Generate *count* item prototypes suitable for spawning.

    Args:
        shop_type: "boutique", "food", or "general"
        count: how many prototypes to generate

    Returns:
        list of prototype dicts
    """
    from world.itemator_generator import GENERATORS

    weights = SHOP_TYPE_WEIGHTS.get(shop_type, SHOP_TYPE_WEIGHTS["general"])
    protos = []
    for _ in range(count):
        gen_key = _weighted_choice(weights)
        gen_func = GENERATORS.get(gen_key)
        if gen_func:
            proto = gen_func()
            protos.append(proto)
    return protos

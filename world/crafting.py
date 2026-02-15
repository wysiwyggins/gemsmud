"""
Crafting engine for Zone 25.

Combines two raw materials into a finished item. Each station has a
primary output type (e.g. textiles make garments, milk vats make cheese
and ice cream), with a small chance of a wild-card result.

Usage:
    from world.crafting import craft_item
    proto = craft_item(material_obj_1, material_obj_2)
"""

import random

from world.itemator_generator import GENERATORS, _random_text_color


# ---------------------------------------------------------------------------
# Station → output type mapping
# ---------------------------------------------------------------------------
# Each station has a weighted list of (generator_key, weight) pairs.
# The primary output is heavily favored, with small chances of surprises.

STATION_OUTPUTS = {
    "textile": [
        ("garment", 75),
        ("talisman", 15),
        ("art", 10),
    ],
    "glazier": [
        ("art", 70),
        ("talisman", 30),
    ],
    "wax": [
        ("talisman", 65),
        ("art", 25),
        ("poem", 10),
    ],
    "clay": [
        ("art", 70),
        ("talisman", 30),
    ],
    "milk": [
        ("cheese", 45),
        ("ice_cream", 45),
        ("talisman", 10),
    ],
    "candy": [
        ("candy", 80),
        ("talisman", 10),
        ("art", 10),
    ],
}

# Fallback for unknown stations or cross-station combos
DEFAULT_OUTPUTS = [
    ("talisman", 30),
    ("art", 20),
    ("garment", 20),
    ("scifi_book", 10),
    ("poem", 10),
    ("cheese", 5),
    ("ice_cream", 5),
]


def _pick_output_type(station1, station2):
    """
    Choose a generator key based on material stations.
    Same-station uses that station's table. Cross-station picks
    from either station's table at random, or the default.
    """
    if station1 == station2 and station1 in STATION_OUTPUTS:
        table = STATION_OUTPUTS[station1]
    elif station1 in STATION_OUTPUTS and station2 in STATION_OUTPUTS:
        table = random.choice([
            STATION_OUTPUTS[station1],
            STATION_OUTPUTS[station2],
        ])
    elif station1 in STATION_OUTPUTS:
        table = STATION_OUTPUTS[station1]
    elif station2 in STATION_OUTPUTS:
        table = STATION_OUTPUTS[station2]
    else:
        table = DEFAULT_OUTPUTS

    keys, weights = zip(*table)
    return random.choices(keys, weights=weights, k=1)[0]


def craft_item(mat1, mat2):
    """
    Combine two material objects into a finished item proto.

    Args:
        mat1: An Object with db.material == True
        mat2: An Object with db.material == True

    Returns:
        dict: A prototype dictionary suitable for spawn().
    """
    # Gather flavor words from both materials
    flavor1 = list(mat1.db.flavor_words or [])
    flavor2 = list(mat2.db.flavor_words or [])
    all_flavors = flavor1 + flavor2

    # Same-station bonus: slightly higher masterpiece chance
    station1 = mat1.db.material_station
    station2 = mat2.db.material_station
    same_station = (station1 == station2)

    # Pick output type based on stations
    gen_key = _pick_output_type(station1, station2)

    # Generate the base proto
    generator = GENERATORS[gen_key]
    proto = generator()

    # Inject material flavor into the description
    proto["desc"] = _inject_flavor(proto["desc"], all_flavors, mat1, mat2)

    # Same-station masterpiece bonus for artwork
    if same_station and gen_key == "art" and not proto.get("cursed"):
        if not _is_masterpiece_desc(proto["desc"]):
            if random.random() < 0.5:
                proto = _force_masterpiece(proto, all_flavors, mat1, mat2)

    return proto


def _inject_flavor(desc, flavor_words, mat1, mat2):
    """
    Weave material flavor words into an item description.

    Appends a crafting provenance line that names the materials used,
    and sprinkles a flavor adjective into the existing description.
    """
    if not flavor_words:
        return desc

    # Pick one flavor word from each material to highlight
    word1 = random.choice(list(mat1.db.flavor_words or ["unusual"]))
    word2 = random.choice(list(mat2.db.flavor_words or ["unusual"]))

    # Add a provenance line
    provenance = (
        f" Crafted from {word1} {mat1.key} and {word2} {mat2.key}."
    )

    return desc + provenance


def _is_masterpiece_desc(desc):
    """Check if a description looks like a masterpiece (has 'masterful')."""
    return "masterful" in desc.lower()


def _force_masterpiece(proto, all_flavors, mat1, mat2):
    """
    Re-generate art with a guaranteed masterpiece outcome.
    """
    from world.itemator_generator import (
        _pick, _add_article, _random_text_color,
    )

    color = _pick("colors.txt")
    substance = _pick("substances.txt")
    adjective = _pick("adjectives.txt")
    artwork = _pick("artworks.txt")
    title = _pick("artTitles.txt").title()
    title_two = _pick("artTitles2.txt").title()
    skill = _pick("skills.txt")
    verb = _pick("artSpeakVerbs.txt")
    theme = _pick("epicThemes.txt")
    textcolor = _random_text_color()
    an_adj = _add_article(adjective)
    key = f"{title} {title_two}"

    desc = (
        f"{textcolor}'{key}'|n:\n"
        f"{an_adj} piece of {artwork} created from {color} {substance}. "
        f"It's a masterful work of {skill} as it {verb} {theme}."
    )
    desc = _inject_flavor(desc, all_flavors, mat1, mat2)

    return {
        "key": key,
        "typeclass": "typeclasses.objects.Object",
        "desc": desc,
        "artwork": "true",
    }

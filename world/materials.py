"""
Material definitions for the Industrial Park crafting system.

Each workshop station produces a set of raw materials. Materials are
spawned as regular Objects with db attributes marking them as materials
and carrying flavor words that get woven into crafted item descriptions.

Materials count at fractional weight (default 1/3) toward the platform
sinking limit.
"""

# Default weight fraction for materials (1/3 of a regular item)
MATERIAL_WEIGHT_FRACTION = 0.33

# ---------------------------------------------------------------------------
# Material registry
# ---------------------------------------------------------------------------
# Each entry: {
#   "name": display name / object key,
#   "desc": short description when spawned,
#   "category": broad material type,
#   "flavor_words": list of words/phrases injected into crafted descs,
# }
#
# Keyed by station name (matches MaterialWomb's db.station attribute).
# ---------------------------------------------------------------------------

STATIONS = {
    "textile": {
        "label": "Textile megaspools",
        "materials": [
            {
                "name": "silk thread",
                "desc": "A spool of luminous silk thread, fine as spider web.",
                "category": "textile",
                "flavor_words": ["silken", "gossamer", "lustrous thread"],
            },
            {
                "name": "raw cotton",
                "desc": "A dense bale of unbleached raw cotton.",
                "category": "textile",
                "flavor_words": ["cotton", "woven", "soft-spun"],
            },
            {
                "name": "synthetic fiber",
                "desc": "A coil of iridescent synthetic fiber, slightly warm to the touch.",
                "category": "textile",
                "flavor_words": ["synthetic", "shimmering", "polymer-woven"],
            },
            {
                "name": "iridescent yarn",
                "desc": "A skein of yarn that shifts color as it catches the light.",
                "category": "textile",
                "flavor_words": ["iridescent", "color-shifting", "prismatic yarn"],
            },
        ],
    },
    "glazier": {
        "label": "Glazier workshop",
        "materials": [
            {
                "name": "blown glass",
                "desc": "A delicate globe of hand-blown glass, still warm.",
                "category": "mineral",
                "flavor_words": ["blown glass", "translucent", "vitreous"],
            },
            {
                "name": "stained pane",
                "desc": "A small pane of deeply colored stained glass.",
                "category": "mineral",
                "flavor_words": ["stained glass", "jewel-toned", "cathedral-bright"],
            },
            {
                "name": "glass bead",
                "desc": "A handful of tiny glass beads in assorted colors.",
                "category": "mineral",
                "flavor_words": ["beaded", "glass-studded", "bead-encrusted"],
            },
            {
                "name": "crystal rod",
                "desc": "A smooth rod of clear crystal, cold to the touch.",
                "category": "mineral",
                "flavor_words": ["crystal", "clear-spun", "rod-shaped"],
            },
            {
                "name": "fiber optic extrusion",
                "desc": "a flexible length of thin glass thread.",
                "category": "mineral",
                "flavor_words": ["fiber optic"],
            },
            
        ],
    },
    "wax": {
        "label": "Wax extruders",
        "materials": [
            {
                "name": "beeswax block",
                "desc": "A golden block of beeswax, faintly fragrant.",
                "category": "organic",
                "flavor_words": ["beeswax", "honey-golden", "wax-sealed"],
            },
            {
                "name": "paraffin sheet",
                "desc": "A translucent sheet of smooth paraffin wax.",
                "category": "chemical",
                "flavor_words": ["paraffin", "waxy", "translucent"],
            },
            {
                "name": "scented wax",
                "desc": "A cake of wax infused with an unidentifiable but pleasant scent.",
                "category": "organic",
                "flavor_words": ["scented", "aromatic", "perfumed wax"],
            },
            {
                "name": "resin pellet",
                "desc": "A handful of amber resin pellets, hard as stone.",
                "category": "chemical",
                "flavor_words": ["resin-coated", "amber", "lacquered"],
            },
        ],
    },
    "clay": {
        "label": "Polyclay intubators",
        "materials": [
            {
                "name": "polyclay slab",
                "desc": "A slab of polyclay in a marbled pattern of earth tones.",
                "category": "mineral",
                "flavor_words": ["polyclay", "marbled", "earth-toned"],
            },
            {
                "name": "terracotta lump",
                "desc": "A warm lump of terracotta clay, ready to be shaped.",
                "category": "mineral",
                "flavor_words": ["terracotta", "clay-fired", "earthen"],
            },
            {
                "name": "porcelain slip",
                "desc": "A sealed vessel of liquid porcelain, bone white.",
                "category": "mineral",
                "flavor_words": ["porcelain", "bone-white", "ceramic"],
            },
            {
                "name": "ceramic dust",
                "desc": "A pouch of fine ceramic dust that glitters faintly.",
                "category": "mineral",
                "flavor_words": ["ceramic", "dust-glazed", "kiln-born"],
            },
        ],
    },
    "milk": {
        "label": "Milk vats",
        "materials": [
            {
                "name": "protein curd",
                "desc": "A dense block of protein curd, slightly rubbery.",
                "category": "organic",
                "flavor_words": ["protein-rich", "curd-formed", "bio-dense"],
            },
            {
                "name": "bioplastic film",
                "desc": "A flexible sheet of bioplastic with a milky sheen.",
                "category": "chemical",
                "flavor_words": ["bioplastic", "milky", "bio-formed"],
            },
            {
                "name": "casein powder",
                "desc": "A bag of fine white casein powder.",
                "category": "organic",
                "flavor_words": ["casein", "powdered", "milk-derived"],
            },
            {
                "name": "fermented culture",
                "desc": "A sealed jar of bubbling fermented culture. It smells... alive.",
                "category": "organic",
                "flavor_words": ["fermented", "living", "culture-grown"],
            },
        ],
    },
    "candy": {
        "label": "Confectionary tanks",
        "materials": [
            {
                "name": "sugar glass",
                "desc": "A pane of sugar glass, perfectly transparent and brittle.",
                "category": "edible",
                "flavor_words": ["sugar glass", "crystalline", "candy-bright"],
            },
            {
                "name": "caramel strand",
                "desc": "A long strand of spun caramel, golden and sticky.",
                "category": "edible",
                "flavor_words": ["caramel", "golden-spun", "toffee-laced"],
            },
            {
                "name": "cocoa butter",
                "desc": "A smooth disk of cocoa butter with a rich chocolate scent.",
                "category": "edible",
                "flavor_words": ["cocoa-infused", "chocolate", "rich"],
            },
            {
                "name": "candy lacquer",
                "desc": "A tin of glossy candy lacquer in an alarming shade of red.",
                "category": "edible",
                "flavor_words": ["lacquered", "candy-coated", "glossy"],
            },
        ],
    },
}


def get_station_materials(station_key):
    """Return the list of material dicts for a station, or empty list."""
    station = STATIONS.get(station_key)
    if station:
        return station["materials"]
    return []


def get_all_station_keys():
    """Return all station key strings."""
    return list(STATIONS.keys())

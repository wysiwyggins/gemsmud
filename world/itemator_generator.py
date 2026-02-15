"""
Itemator — procedural item generator for Zone 25.

Ported from the old GEMS codebase (typeclasses/itemator/itemator.py).
Generates talismans, artwork, garments, sci-fi books, poems,
cheeses, and ice creams.

Usage:
    from world.itemator_generator import generate_item_proto
    proto = generate_item_proto()
    # proto is a dict suitable for evennia.prototypes.spawner.spawn()
"""

import random
from pathlib import Path

try:
    import markovify
except ImportError:
    markovify = None

# ---------------------------------------------------------------------------
# Word list cache
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).parent / "itemator_data"
_cache = {}


def _read_word_list(filename):
    """Read a word list file, cache it, return list of stripped lines."""
    if filename not in _cache:
        filepath = _DATA_DIR / filename
        with open(filepath, "r", encoding="utf-8") as fh:
            _cache[filename] = [
                line.strip() for line in fh if line.strip()
            ]
    return _cache[filename]


def _pick(filename):
    """Return a random entry from a word list file."""
    return random.choice(_read_word_list(filename))


# ---------------------------------------------------------------------------
# Markov model cache
# ---------------------------------------------------------------------------

_model_cache = {}


def _get_markov_model(filename):
    """Read a corpus file and return a compiled markovify model, cached.
    Returns None if markovify is not installed."""
    if markovify is None:
        return None
    if filename not in _model_cache:
        filepath = _DATA_DIR / filename
        with open(filepath, "r", encoding="utf-8") as fh:
            text = fh.read()
        model = markovify.NewlineText(text)
        _model_cache[filename] = model.compile()
    return _model_cache[filename]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _add_article(word):
    """Prefix a word with 'A' or 'An' (skip if plural)."""
    if not word:
        return "One " + word
    if word[-1] == "s":
        return word  # plural, no article
    if word[0].lower() in "aeiou":
        return "An " + word
    return "A " + word


def _random_text_color():
    """Return a random Evennia xterm256 color tag like |354."""
    r = random.randint(0, 5)
    g = random.randint(0, 5)
    b = random.randint(0, 5)
    return "|" + str(r) + str(g) + str(b)


# ---------------------------------------------------------------------------
# Item generators
# ---------------------------------------------------------------------------


def _generate_talisman():
    color = _pick("colors.txt")
    substance = _pick("substances.txt")
    adjective = _pick("adjectives.txt")
    name = _pick("talismans.txt")
    an_adj = _add_article(adjective)
    desc = (
        f"{an_adj} {name} made of {color} {substance}."
    )
    return {
        "key": name,
        "typeclass": "typeclasses.objects.Object",
        "desc": desc,
    }


def _generate_art():
    roll = random.randint(0, 20)
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

    if roll >= 19:
        # Cursed artwork (roll 19-20)
        desc = (
            f"|500'{key}'|n:\n"
            f" |401 An unspeakable anathema |n {artwork} forged in "
            f"{color} {substance}. It embodies profane {skill} as it "
            f"{verb} {theme}."
        )
        return {
            "key": key,
            "typeclass": "typeclasses.objects.Object",
            "desc": desc,
            "artwork": "true",
            "cursed": "true",
        }
    elif roll <= 10:
        # Masterpiece (roll 0-10)
        desc = (
            f"{textcolor}'{key}'|n:\n"
            f"{an_adj} piece of {artwork} created from {color} {substance}. "
            f"It's a masterful work of {skill} as it {verb} {theme}."
        )
        return {
            "key": key,
            "typeclass": "typeclasses.objects.Object",
            "desc": desc,
            "artwork": "true",
        }
    else:
        # Normal artwork (roll 11-18)
        desc = (
            f"{textcolor}'{key}'|n:\n"
            f"{an_adj} example of {artwork} rendered in {color} {substance}. "
            f"{title} {title_two} displays considerable {skill} as it "
            f"{verb} {theme}."
        )
        return {
            "key": key,
            "typeclass": "typeclasses.objects.Object",
            "desc": desc,
            "artwork": "true",
        }


def _generate_garment():
    color = _pick("colors.txt")
    clothing_item = _pick("clothes.txt")
    color_desc = _add_article(color)
    desc = f"{color_desc} {clothing_item}"
    return {
        "key": clothing_item,
        "typeclass": "evennia.contrib.game_systems.clothing.clothing.ContribClothing",
        "desc": desc,
    }


def _generate_scifi_book():
    adjective = _pick("scifiwords.txt")
    book_name = _pick("talismans.txt")
    color = _pick("colors.txt")
    textcolor = _random_text_color()
    model = _get_markov_model("scifi_book_corpus.txt")

    title = f"The {adjective} {book_name}".title()
    book_text = f"\n{textcolor}{title}|n\n\n"
    if model:
        for _ in range(60):
            try:
                sentence = model.make_sentence(tries=100)
                if sentence:
                    book_text += sentence + "\n"
                else:
                    book_text += "ROCKETS! ROCKETS! ROCKETS!\n"
            except TypeError:
                book_text += "ROCKETS! ROCKETS! ROCKETS!\n"
    else:
        book_text += "[ The pages are blank. The ink has not yet been invented. ]\n"

    return {
        "key": f"{color} book",
        "typeclass": "typeclasses.objects.Readable",
        "desc": "A book of science fiction. You can |555read|n it if you like.",
        "readable_text": book_text,
    }


def _generate_poem():
    model = _get_markov_model("poetry_corpus.txt")
    thing = _pick("artTitles2.txt")
    textcolor = _random_text_color()

    if not model:
        poem_name = f"Ode To {thing}".title()
        poem_text = (
            f"\n{textcolor}{poem_name}|n\n"
            "[ The pages are blank. The muse has not yet arrived. ]\n"
        )
        return {
            "key": poem_name,
            "typeclass": "typeclasses.objects.Readable",
            "desc": "A chapbook of poetry. You can |555read|n it if you like.",
            "readable_text": poem_text,
        }

    # Generate poem title
    try:
        poem_name = model.make_short_sentence(30)
        if poem_name:
            poem_name = poem_name.title()
        else:
            poem_name = "Untitled"
    except TypeError:
        poem_name = "Untitled"

    poem_text = f"\n{textcolor}{poem_name}|n\n"
    for _ in range(5):
        roll = random.randint(0, 5)
        try:
            if roll == 0:
                s1 = model.make_sentence(tries=100) or ""
                s2 = model.make_short_sentence(120) or ""
                poem_text += f"{s1}\n\t\t{s2}\n"
            elif roll == 2:
                s = model.make_sentence(tries=100) or ""
                poem_text += f"\t{poem_name} {s}\n\n"
            elif roll == 3:
                s = model.make_short_sentence(80) or ""
                poem_text += f"\t\t{s}, the {thing}.\n"
            elif roll == 4:
                for __ in range(4):
                    s = model.make_sentence(tries=100) or ""
                    poem_text += f"{s}\n"
            else:
                s = model.make_short_sentence(120) or ""
                poem_text += f"\t\t{s}\n"
        except TypeError:
            poem_text += "\n"

    # Optional closing line
    if random.randint(0, 3) == 1:
        try:
            s = model.make_sentence(tries=100) or ""
            poem_text += f"\n\t\t{textcolor}{s} {poem_name}.|n"
        except TypeError:
            pass

    return {
        "key": poem_name,
        "typeclass": "typeclasses.objects.Readable",
        "desc": "A chapbook of poetry. You can |555read|n it if you like.",
        "readable_text": poem_text,
    }


# ---------------------------------------------------------------------------
# Character-level Markov chain (for generating placename-style words)
# ---------------------------------------------------------------------------

_char_model_cache = {}


def _get_char_markov(filename, order=3):
    """
    Build a character-level Markov model from a list of words (one per line).
    Returns a dict mapping character n-grams to lists of next characters.
    """
    cache_key = (filename, order)
    if cache_key in _char_model_cache:
        return _char_model_cache[cache_key]

    words = _read_word_list(filename)
    model = {}
    for word in words:
        padded = "^" * order + word.lower() + "$"
        for i in range(len(padded) - order):
            gram = padded[i:i + order]
            next_char = padded[i + order]
            model.setdefault(gram, []).append(next_char)

    _char_model_cache[cache_key] = model
    return model


def _generate_markov_word(filename, order=3, min_len=4, max_len=12):
    """
    Generate a single word using a character-level Markov chain trained
    on the given word list. Returns a capitalized word.
    """
    model = _get_char_markov(filename, order)
    source_words = {w.lower() for w in _read_word_list(filename)}

    for _attempt in range(50):
        state = "^" * order
        result = ""
        for _ in range(max_len + 5):
            choices = model.get(state)
            if not choices:
                break
            ch = random.choice(choices)
            if ch == "$":
                break
            result += ch
            state = state[1:] + ch

        if min_len <= len(result) <= max_len and result not in source_words:
            return result.capitalize()

    # Fallback: return a real name from the corpus
    return random.choice(_read_word_list(filename)).capitalize()


# ---------------------------------------------------------------------------
# Food generators (cheese, ice cream)
# ---------------------------------------------------------------------------


def _generate_cheese():
    name = _generate_markov_word("cheese_names_corpus.txt")
    texture = _pick("cheese_textures.txt")
    flavor = _pick("cheese_flavors.txt")
    color = random.choice([
        "pale ivory", "golden yellow", "deep amber", "stark white",
        "mottled orange", "straw-colored", "creamy white", "ash-grey",
    ])
    age = random.choice([
        "young", "aged", "cave-aged", "cellar-ripened",
        "fresh", "well-aged", "briefly aged", "long-aged",
    ])

    desc = (
        f"A wheel of {age} {name} cheese, {color} in hue. "
        f"The paste is {texture}. "
        f"It tastes {flavor}."
    )

    return {
        "key": f"{name} cheese",
        "typeclass": "typeclasses.objects.EdibleObject",
        "desc": desc,
        "edible": True,
        "flavor_text": f"It tastes {flavor}. Delicious.",
    }


def _generate_ice_cream():
    flavor1 = _pick("icecream_flavors.txt")
    style = _pick("icecream_styles.txt")
    color = _pick("colors.txt")
    textcolor = _random_text_color()

    # 40% chance of a second flavor swirl
    if random.random() < 0.4:
        flavor2 = _pick("icecream_flavors.txt")
        while flavor2 == flavor1:
            flavor2 = _pick("icecream_flavors.txt")
        key = f"{flavor1} and {flavor2} {style}"
        desc = (
            f"{textcolor}A generous scoop of {flavor1} and {flavor2} "
            f"{style}|n, swirled together in a {color} bowl. "
            f"It's already starting to melt."
        )
    else:
        key = f"{flavor1} {style}"
        desc = (
            f"{textcolor}A generous scoop of {flavor1} {style}|n "
            f"in a {color} bowl. It's already starting to melt."
        )

    return {
        "key": key,
        "typeclass": "typeclasses.objects.EdibleObject",
        "desc": desc,
        "edible": True,
        "flavor_text": f"Cold and sweet. The {flavor1} lingers on your tongue.",
    }


def _generate_candy():
    flavor = _pick("icecream_flavors.txt")
    color = _pick("colors.txt")
    textcolor = _random_text_color()

    form = random.choice([
        "hard candy", "taffy", "lollipop", "gummy", "bonbon",
        "caramel chew", "toffee", "jawbreaker", "drop", "candy bar",
        "rock candy", "pastille", "nougat", "fudge", "truffle",
        "candy floss", "brittle", "praline", "dragee", "lozenge",
    ])

    if random.random() < 0.3:
        flavor2 = _pick("icecream_flavors.txt")
        while flavor2 == flavor:
            flavor2 = _pick("icecream_flavors.txt")
        key = f"{flavor} and {flavor2} {form}"
        desc = (
            f"{textcolor}A {flavor} and {flavor2} {form}|n, "
            f"wrapped in {color} paper. It smells intensely sweet."
        )
        flavor_text = (
            f"A burst of {flavor} followed by {flavor2}. "
            f"Your teeth ache pleasantly."
        )
    else:
        key = f"{flavor} {form}"
        desc = (
            f"{textcolor}A {flavor} {form}|n "
            f"in a {color} wrapper. It glistens under the light."
        )
        flavor_text = (
            f"Sweet {flavor} dissolves on your tongue. "
            f"Your fillings tingle."
        )

    return {
        "key": key,
        "typeclass": "typeclasses.objects.EdibleObject",
        "desc": desc,
        "edible": True,
        "flavor_text": flavor_text,
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Generator registry (used by crafting system)
# ---------------------------------------------------------------------------

GENERATORS = {
    "talisman": _generate_talisman,
    "art": _generate_art,
    "garment": _generate_garment,
    "scifi_book": _generate_scifi_book,
    "poem": _generate_poem,
    "cheese": _generate_cheese,
    "ice_cream": _generate_ice_cream,
    "candy": _generate_candy,
}


def generate_item_proto():
    """
    Generate a random item prototype dict, suitable for spawn().

    Returns:
        dict: A prototype dictionary with at least 'key', 'typeclass',
              and 'desc'. May also have 'readable_text', 'artwork',
              'cursed', etc.
    """
    item_type = random.randint(0, 7)
    if item_type <= 2:
        return _generate_talisman()
    elif item_type == 3:
        return _generate_art()
    elif item_type == 4:
        return _generate_scifi_book()
    elif item_type == 5:
        return _generate_poem()
    else:
        return _generate_garment()

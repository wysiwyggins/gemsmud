"""
File-based help entries for Sea of Objects.

These complement command-based help and help entries added in the database
using the `sethelp` command in-game.

Control where Evennia reads these entries with `settings.FILE_HELP_ENTRY_MODULES`,
which is a list of python-paths to modules to read.

A module like this should hold a global `HELP_ENTRY_DICTS` list, containing
dicts that each represent a help entry. If no `HELP_ENTRY_DICTS` variable is
given, all top-level variables that are dicts in the module are read as help
entries.

Each dict is on the form
::

    {'key': <str>,
     'text': <str>}``     # the actual help text. Can contain # subtopic sections
     'category': <str>,   # optional, otherwise settings.DEFAULT_HELP_CATEGORY
     'aliases': <list>,   # optional
     'locks': <str>       # optional, 'view' controls seeing in help index, 'read'
                          #           if the entry can be read. If 'view' is unset,
                          #           'read' is used for the index. If unset, everyone
                          #           can read/view the entry.

"""

HELP_ENTRY_DICTS = [
    # ------------------------------------------------------------------
    # New Players
    # ------------------------------------------------------------------
    {
        "key": "getting started",
        "aliases": ["newbie", "new", "start", "beginner"],
        "category": "New Players",
        "text": """
            Welcome to Sea of Objects.

            You are on Zone 25, a floating ocean platform. In this post-scarcity
            world, almost anything can be fabricated on demand -- but the platform
            has a strict weight limit. If too many objects accumulate, the platform
            sinks. Everyone aboard must collectively decide what is worth keeping.

            # First steps

            Explore the platform. Key locations:

              Welcome area  - Central hub, start here
              KonMarie Temple - Incinerator for recycling items into ash
              Industrial Park - Workshops for crafting (via the Veloway)
              Cafetorium    - Free daily rations (no ash required)
              Fashion District - Trading post for buying and selling
              Gallery       - Boutique shop for art and garments
              Gourmand Shop - Food stall for cheese, ice cream, and candy

            # Earning ash

            Ash tokens are the station's currency. You earn ash by burning items
            in the incinerator at the KonMarie Temple:
              - Normal items: 1 ash
              - Artwork/masterpieces: 3 ash
              - Cursed items: 2 ash

            The Cafetorium ration dispenser gives 3 free rations per day -- burn
            them at the temple to start building your ash supply.

            # Spending ash

            Use ash to operate itemators (1 ash each) or buy from shops.

            # Useful commands

              inventory (or inv, i) - See what you're carrying
              ash                   - Check your ash balance
              score                 - Personal status summary
              look <object>         - Examine something
              get <object>          - Pick something up
              gift <item> to <player> - Offer an item to someone

            Type |whelp|n to see all available help topics.
        """,
    },
    # ------------------------------------------------------------------
    # Economy
    # ------------------------------------------------------------------
    {
        "key": "ash tokens",
        "aliases": ["tokens", "economy", "currency", "money"],
        "category": "Economy",
        "text": """
            Ash tokens are Zone 25's currency, representing reclaimed feedstock
            that the station's fabrication systems can reuse.

            # Earning ash

            Burn items in the incinerator at the KonMarie Temple:
              - Normal items: 1 ash
              - Artwork or masterpieces: 3 ash
              - Cursed items: 2 ash

            You can also earn ash by reporting hoarders (reporters split a
            25 ash reward if enforcement completes).

            # Spending ash

              - Itemators: 1 ash per use
              - Shops: prices vary by item type and scarcity

            # Station ash reserve

            The station maintains a communal feedstock pool (starts at 500,
            caps at 2000). Shops draw from this pool to buy your items.
            The pool recharges slowly from ocean filtration and waste
            processing. Hoarding fines are recycled back into the pool.

            # Commands

              ash - Check your current balance
              burn <item> - Burn an item at the incinerator
              score - See your full status including ash
        """,
    },
    {
        "key": "shops",
        "aliases": ["buy", "sell", "browse", "trading", "store"],
        "category": "Economy",
        "text": """
            Three shops sell and buy items on Zone 25:

              Trading post  (Fashion District) - General goods: talismans,
                                                 garments, books
              Food stall    (Gourmand Shop)    - Cheese, ice cream, candy
              Boutique      (Gallery)          - Art, haute couture garments

            # Commands

            These commands are available when you are in the same room as a
            shop counter:

              browse  - Open the shop menu to see items for sale
              buy     - Same as browse (opens the shop menu)
              sell    - Open the sell menu to sell items from your inventory

            # Pricing

            Prices adjust based on scarcity. If there are few garments in
            the world, garments cost more. If there are many, they're cheap.
            Sell prices are roughly 40% of buy prices.

            # Restocking

            Shops restock automatically every 10 minutes. Unsold items
            expire after 60 minutes to keep inventory fresh.
        """,
    },
    # ------------------------------------------------------------------
    # Game Systems
    # ------------------------------------------------------------------
    {
        "key": "platform weight",
        "aliases": ["weight", "sinking", "capacity", "danger", "limit"],
        "category": "Game Systems",
        "text": """
            Zone 25 has a maximum capacity of 1000 weighted item-units. If
            the total exceeds this, the platform begins to sink.

            # Weight categories

            Not all objects weigh the same:

              Regular items:           1.0 units each
              Raw materials:           0.33 units each
              Items on display shelves: 0.5 units each
              Masterpiece artwork:     0.5 units each
              Connected player bodies: 5.0 units each

            These stack: a masterpiece on a display shelf counts as 0.25.

            # Danger levels

              Safe (0-75%):     Normal operation, pleasant weather
              Warning (75-90%): Structural creaks, public broadcasts
              Critical (90-100%): Severe warnings, tremors
              Sinking (100%+):  Emergency! Itemators shut down,
                                water imagery, klaxons

            # What to do

            Burn unneeded items at the KonMarie Temple incinerator. Eat
            edible items (cheese, ice cream, rations). Report hoarders
            if someone is carrying too many items.

            The counter signs at the Dock and Inner courtyard show the
            current item count and danger level. Use |wread sign|n to check.
        """,
    },
    {
        "key": "crafting",
        "aliases": ["combine", "workbench", "materials", "workshop"],
        "category": "Game Systems",
        "text": """
            Six workshops in the Industrial Park let you craft items from
            raw materials.

            # How it works

            1. Use a material womb (|wuse <machine>|n) to produce a raw material
               (costs 1 ash). Each workshop produces station-specific materials.
            2. Collect two materials.
            3. Use a workbench: |wcombine <material1> and <material2>|n

            The workbench consumes both materials and produces a finished item.
            The materials' flavor words influence the description of the result.

            # Workshops

              Textile megaspools - Silk, cotton, synthetic fiber, yarn
                                   -> Mostly garments
              Glazier            - Glass, crystal, stained panes
                                   -> Mostly artwork
              Wax extruders      - Beeswax, paraffin, resin, scented wax
                                   -> Mostly talismans
              Polyclay intubators - Clay, terracotta, porcelain, ceramic
                                   -> Mostly artwork
              "Milk" vats        - Protein curd, bioplastic, casein
                                   -> Cheese and ice cream
              Confectionary tanks - Sugar glass, caramel, cocoa butter
                                   -> Candy

            # Masterpiece bonus

            Combining two materials from the same workshop station gives a
            50% chance of producing a masterpiece (if the result is artwork).
            Masterpieces are announced server-wide.
        """,
    },
    {
        "key": "itemators",
        "aliases": ["womb", "object womb", "itemator", "fabricate"],
        "category": "Game Systems",
        "text": """
            Itemators (also called object wombs) are devices scattered across
            Zone 25 that fabricate random items from the station's feedstock.

            # Usage

              use <itemator>

            Each use costs 1 ash token.

            # What they produce

            Itemators generate one of seven item types at random:

              Talismans  - Decorative objects with color, substance, adjective
              Artwork    - Paintings, sculptures (may be masterpieces or cursed)
              Garments   - Wearable clothing items
              Sci-fi books - Procedurally generated novels
              Poetry     - Generated verse
              Cheese     - Edible, with unique name and flavor
              Ice cream  - Edible, sometimes dual-flavor swirl

            # Restrictions

            Itemators shut down when the platform reaches sinking capacity.
            They will refuse to fabricate until the weight is reduced.

            # Locations

            Itemators can be found in several rooms including the Welcome area,
            Library, Glazier, Confectionary tanks, and others.
        """,
    },
    {
        "key": "display shelves",
        "aliases": ["shelves", "display", "claim", "shelf"],
        "category": "Game Systems",
        "text": """
            Display shelves are fixtures where you can showcase items. Items
            on shelves count at reduced weight (0.5) toward the platform total.

            # Commands

              claim              - Claim an unclaimed shelf as yours
              unclaim            - Release your claim
              display <item>     - Place an item from your inventory on the shelf
              retrieve <item>    - Take an item back from the shelf

            # Rules

              - You must claim a shelf before displaying items on it.
              - Each shelf holds up to 5 items.
              - Only the shelf owner can display or retrieve items.
              - Items on your claimed shelf count toward your hoarding total
                (same as inventory items) for enforcement purposes.
              - Unclaiming a shelf leaves the items in place but they no
                longer count toward your personal total.
        """,
    },
    {
        "key": "cursed items",
        "aliases": ["cursed", "curse", "curses"],
        "category": "Game Systems",
        "text": """
            There is a small chance that artwork generated by an itemator
            will be cursed. Cursed items have dark, unsettling descriptions.

            # Effects

            While carrying cursed items:
              - Every 5 minutes, you receive uncomfortable atmospheric messages.
              - With 2 or more cursed items, there is a 20% chance per tick
                that you involuntarily drop a random non-worn item.

            Curse effects stop automatically when you no longer carry any
            cursed items.

            # Getting rid of them

            Burn cursed items in the incinerator at the KonMarie Temple.
            Cursed items yield 2 ash when burned. You can also gift them
            to other players or sell them at shops.
        """,
    },
    {
        "key": "incinerator",
        "aliases": ["burn", "incinerate", "konmarie", "temple"],
        "category": "Game Systems",
        "text": """
            The incinerator in the KonMarie Temple breaks objects down into
            reclaimed feedstock, awarding you ash tokens.

            # Commands

              burn <item>
              incinerate <item>
              put <item> in incinerator

            You must be carrying the item and standing in the temple.

            # Ash rewards

              Normal items:           1 ash
              Artwork / masterpieces: 3 ash
              Cursed items:           2 ash

            Burning items reduces the platform's total weight, helping
            prevent sinking.
        """,
    },
    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------
    {
        "key": "hoarding",
        "aliases": ["report", "enforcement", "hoarder", "investigation"],
        "category": "Rules",
        "text": """
            Players can report others for carrying too many items. Your
            item total includes both inventory and items on your claimed
            display shelves.

            # Thresholds

              Minor hoarding (10-19 items):
                1st offense: 5 ash fine
                2nd offense: 15 ash fine
                3rd offense: Formal investigation

              Major hoarding (20+ items):
                Immediate formal investigation

            # Investigations

            When a formal investigation begins, the server broadcasts
            escalating warnings over 5 minutes. Additional reports from
            other players speed up the investigation.

            On completion, a SecurityRobot is deployed. It escorts the
            offender to the KonMarie Temple where:
              - All possessions are destroyed
              - A 50 ash debt is applied
              - The offender respawns at the Welcome area

            Reporters split a 25 ash reward.

            # Command

              report <player> - Report a player for hoarding
        """,
    },
    # ------------------------------------------------------------------
    # Social
    # ------------------------------------------------------------------
    {
        "key": "gifting",
        "aliases": ["gift", "accept", "reject", "give"],
        "category": "Social",
        "text": """
            You can offer items to other players as gifts.

            # Commands

              gift <item> to <player> - Offer an item
              accept                  - Accept a pending gift
              reject                  - Decline a pending gift

            # How it works

            When you gift an item, the recipient is notified and can
            accept or reject. If they don't respond within 60 seconds,
            the gift is automatically accepted.

            Only one gift can be pending per recipient at a time. The
            item is held in limbo while the offer is pending.

            Everyone in the room sees the gift exchange.
        """,
    },
    # ------------------------------------------------------------------
    # Roleplay
    # ------------------------------------------------------------------
    {
        "key": "rp commands",
        "aliases": ["rp", "roleplay", "sdesc", "pose", "emote", "recog"],
        "category": "Roleplay",
        "text": """
            Sea of Objects uses a roleplay-aware system. Characters are
            identified by short descriptions (sdescs) rather than account
            names.

            # Short descriptions

              sdesc <description>
                Set your short description (what others see when they look
                at you). Example: sdesc a wiry woman with ink-stained hands

            # Poses

              pose <action>
                Set a pose that appears after your sdesc when others look
                at the room. Example: pose is leaning against the railing

            # Emotes

              emote <text>
                Perform an emote visible to the room. Use /me references
                and target others with their sdesc.

            # Recognition

              recog <character> as <name>
                Give a personal nickname to another character. Only you see
                this name. Example: recog tall stranger as Marcus

            # Looking at others

              look <character>
                Examine a character by their sdesc or your recog for them.
        """,
    },
    {
        "key": "clothing",
        "aliases": ["wear", "remove", "clothes", "outfit"],
        "category": "Roleplay",
        "text": """
            Garments from itemators, shops, or crafting can be worn.
            Worn clothing appears in your character description when
            others look at you.

            # Commands

              wear <garment>
                Put on a garment from your inventory.

              remove <garment>
                Take off a worn garment (returns to inventory).

            Worn items still count toward your inventory total for
            hoarding purposes. They are not dropped by curse effects.
        """,
    },
    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    {
        "key": "map",
        "aliases": ["areas", "zones", "navigation", "rooms"],
        "category": "Navigation",
        "text": """
            Zone 25 layout:

            Dock --> Welcome area (central hub)
                       |
                       +-- Stairwell --> Outer courtyard
                       |                   |
                       |                   +-- Tennis courts
                       |                   +-- Community garden
                       |                   +-- Pool
                       |                   +-- Eastern complex (apartments)
                       |                   +-- Western complex (apartments)
                       |                   +-- Inner courtyard
                       |                         +-- Cafetorium
                       |                         +-- Library
                       |                         +-- Pet shelter
                       |                         +-- Fashion District
                       |                               +-- Gourmand Shop
                       |
                       +-- KonMarie Temple (incinerator)
                       |
                       +-- Veloway --> Industrial Park
                       |                +-- Textile megaspools
                       |                +-- Glazier
                       |                +-- Wax extruders
                       |                +-- Polyclay intubators
                       |                +-- "Milk" vats
                       |                +-- Confectionary tanks
                       |                +-- Laser (communication array)
                       |
                       +-- Gallery (boutique)

            Sublevels accessible from Western complex stairwell.
        """,
    },
    # ------------------------------------------------------------------
    # Developer (keep existing)
    # ------------------------------------------------------------------
    {
        "key": "evennia",
        "aliases": ["ev"],
        "category": "Admin",
        "locks": "read:perm(Developer)",
        "text": """
            Evennia is a MU-game server and framework written in Python. You can read more
            on https://www.evennia.com.

            # subtopics

            ## Installation

            You'll find installation instructions on https://www.evennia.com.

            ## Community

            There are many ways to get help and communicate with other devs!

            ### Discussions

            The Discussions forum is found at https://github.com/evennia/evennia/discussions.

            ### Discord

            There is also a discord channel for chatting - connect using the
            following link: https://discord.gg/AJJpcRUhtF

        """,
    },
]

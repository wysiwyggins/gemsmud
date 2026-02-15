# Sea of Objects

A MUSH built on [Evennia](https://www.evennia.com/) set on a luxury seasteading platform called Zone 25. The world is post-scarcity -- almost anything can be fabricated on demand through automated manufacturing systems -- but the platform has a strict weight limit. Inhabitants must collectively manage how many objects exist in the world, or the platform sinks into the ocean.

There are no hard per-player item limits. Social pressure, visible inventory tracking, and shared consequences are the enforcement mechanism. The game explores what happens when a community has to decide together what is worth keeping.

## Setup

Requires Python 3.11+ and Evennia.

```bash
pip install evennia
pip install markovify          # procedural text generation
pip install twisted[tls]       # IRC bridge (optional)
pip install pyopenssl          # IRC over SSL (optional)

evennia migrate
evennia start
```

Connect via MUD client on `192.168.86.24:4000` or web client at `http://192.168.86.24:4001`.

## Architecture

```
sea_of_objects/
  typeclasses/          # Game entity definitions
    objects.py          # Object, Mirror, Readable, Counter, Incinerator,
                        #   Itemator, MaterialWomb, Workbench, DisplayShelf
    rooms.py            # Room, OutdoorRoom, LaserRoom
    characters.py       # Character (RP + clothing + curse hooks)
    scripts.py          # CurseEffectScript, ItemMonitorScript
    channels.py         # Channel, LaserChannel (IRC bridge)
    exits.py            # Exit
    accounts.py         # Account, Guest
  commands/
    command.py          # CmdGift, CmdAsh, CmdAutoMultimatch
    default_cmdsets.py  # CharacterCmdSet assembly
  world/
    zone_monitor.py     # Item counting, danger levels, broadcast messages
    crafting.py         # Two-material combination engine
    materials.py        # 6 workshop stations, 24 materials, flavor words
    itemator_generator.py  # Procedural item generation (7 item types)
    itemator_data/      # 19 word list and corpus files
    WORLD_BIBLE.md      # Complete world reference (rooms, topology, lore)
  server/conf/
    settings.py         # Game configuration
    at_server_startstop.py  # Startup hooks (scripts, channels)
```

## Game Systems

### Platform Capacity

The core mechanic. All objects in the world are counted toward `ZONE_ITEM_LIMIT` (default 1000), with weighted categories:

| Category | Weight | Example |
|----------|--------|---------|
| Regular items | 1.0 | A talisman, a garment |
| Raw materials | 0.33 | Silk thread, blown glass |
| Displayed items | 0.5 | Items on a DisplayShelf |
| Masterpieces | 0.5 | Artwork flagged as masterpiece |
| Displayed masterpiece | 0.25 | Stacks both reductions |

Danger levels escalate as capacity fills: **safe** (0-75%) -> **warning** (75-90%) -> **critical** (90-100%) -> **sinking** (100%+). At each level, weather echoes shift from pleasant to ominous, broadcasts warn all players, and at sinking capacity, item generation is disabled.

Monitored by `ItemMonitorScript`, a global singleton that ticks every 3 minutes.

### Itemators (Object Wombs)

Devices scattered across the world that generate random items when a player uses them. 7 procedural generators produce:

- **Talismans** -- color + substance + adjective combinations
- **Artwork** -- tiered quality (masterpiece/normal/cursed) with d20 roll
- **Garments** -- wearable clothing items
- **Sci-fi books** -- Markov-chain-generated novels
- **Poetry** -- Markov-chain-generated verse
- **Cheese** -- Markov-chain names + texture + flavor
- **Ice cream** -- 40% chance of dual-flavor swirl

### Crafting

Six workshops in the Industrial Park each have a **MaterialWomb** (produces raw materials) and a **Workbench** (combines two materials). Stations: textile, glazier, wax, clay, milk, candy. Each station's output is weighted toward certain item types. Same-station material combos have a 50% masterpiece bonus.

### Display Shelves

Room fixtures where players showcase items. Configurable capacity (default 5). Items on shelves count at 0.5 weight toward the platform limit. Commands: `display <item>`, `retrieve <item>`.

### Ash Tokens

Non-physical currency earned by incinerating items at the KonMarie Temple:

| Item type | Ash earned |
|-----------|------------|
| Regular | 1 |
| Artwork/masterpiece | 3 |
| Cursed | 2 |

Checked with the `ash` command. Shown on Counter signs alongside player inventories.

### Cursed Items

Artwork generation has a small chance of producing cursed items. When a player picks up a cursed item, a `CurseEffectScript` attaches to them:

- Sends atmospheric discomfort messages every 5 minutes
- With 2+ cursed items, 20% chance per tick of dropping a random non-worn item
- Auto-removes when no cursed items remain

A small ash bonus (2 tokens) rewards disposing of them, but not enough to make farming worthwhile.

### Counter Signs

Dynamic signs (the `Counter` typeclass) that rebuild their text on every look. They display:

- Total platform item count and danger level
- Per-player inventory with item counts and ash balances
- Heaviest and lightest citizens
- All masterpieces with current holder info
- All displayed items by shelf location
- Cursed objects

### Masterpiece Broadcasts

When a masterpiece is created via any Itemator or Workbench, a server-wide announcement names the item and its location -- but not the creator. This drives social interaction: players race to find, claim, trade, or gift masterpieces.

### IRC Bridge (Laser Room)

The Laser room uses a custom `LaserRoom` typeclass with a `LaserChannel` that bridges to IRC (configured for Libera.Chat). Messages are only distributed to characters physically present in the room.

- `transmit <message>` -- send to IRC
- `tune` / `tune out` -- manage subscription
- Characters auto-subscribe on room entry

Setup: `@irc2chan/ssl laser_irc = irc.libera.chat 6697 #channel-name bot-name`

### RP System

Evennia contribs provide: character poses, short descriptions (sdescs), recognition system (recogs), wearable clothing with layering, extended rooms with time-of-day and seasonal descriptions, room details.

## Admin Reference

### Creating objects

```
@create/drop display shelf:typeclasses.objects.DisplayShelf
@set display shelf/shelf_capacity = 8

@create/drop my itemator:typeclasses.objects.Itemator
```

### Changing room typeclasses

```
@typeclass here = typeclasses.rooms.OutdoorRoom
@typeclass laser = typeclasses.rooms.LaserRoom
```

### Checking platform state

```
@py from world.zone_monitor import get_danger_level; print(get_danger_level())
@find/type typeclasses.objects.DisplayShelf
```

### IRC setup

```
@irc2chan/ssl laser_irc = irc.libera.chat 6697 #sea-of-objects laser-radio
@ircstatus
```

## For Players

Connect to `localhost:4000` with any MUD client, or use the web client at `http://localhost:4001`.

**First steps:** Look around. Walk through exits. Find an Itemator and `use` it. Visit the KonMarie Temple to `burn` things you don't want. Check the Counter sign to see how the platform is doing. Explore the Industrial Park to try crafting.

**Key commands:**

- `use <itemator>` -- generate an item
- `combine <material> and <material>` -- craft at a workbench
- `display <item>` / `retrieve <item>` -- manage display shelves
- `burn <item>` -- incinerate at the KonMarie Temple
- `gift <item> to <player>` -- give someone an item
- `ash` -- check your ash token balance
- `transmit <message>` -- send via the Laser array (in Laser room)
- `read <object>` -- read a book or sign
- Standard: `look`, `get`, `drop`, `inventory`, `say`, `pose`

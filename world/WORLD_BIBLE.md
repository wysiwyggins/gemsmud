# Sea of Objects — World Bible

Compact reference for the game world. Distilled from the original GEMS export data.

## Setting

Sea of Objects (formerly GEMS/Jackpot) is set on a **Luxury Seasteading Utopia (LSU)** -- a floating ocean community called Zone 25. In a post-scarcity world where almost anything can be fabricated on demand, inhabitants must strictly limit how many things they own or the platform sinks under the weight.

The architecture is pastel-enameled steel, synthetic grass, transparent aluminum skylights, and stacked living blocks built atop dark industrial ziggurats. Think retro-futurism crossed with Marie Kondo.

## Zone Structure

```
Limbo (entry/splash)
  |
Dock --> Welcome area (central hub)
           |
           +-- Stairwell --> Outer courtyard (recreation hub)
           |                   |
           |                   +-- Tennis courts
           |                   +-- Community garden
           |                   +-- Pool
           |                   +-- Eastern complex (apartments 101-103, mimex)
           |                   +-- Western complex (apartments 201-203, mimex)
           |                   +-- Inner courtyard
           |                         +-- Cafetorium
           |                         +-- Library
           |                         +-- Pet shelter
           |                         +-- Fashion District
           |                               +-- Gourmand Shop
           |
           +-- KonMarie Temple (incinerator/ritual)
           |
           +-- Veloway --> Western Veloway --> Industrial Park
           |                                    +-- Textile megaspools
           |                                    +-- Laser (IRC bridge)
           |                                    +-- Glazier
           |                                    +-- Wax extruders
           |                                    +-- Polyclay intubators
           |                                    +-- "Milk" vats
           |                                    +-- Confectionary tanks
           |
           +-- Gallery
```

Sublevels accessible from Western complex stairwell: room 000, crawlspace.

## Room List

### Entry

| Room | Description |
|------|-------------|
| Limbo | Welcome splash screen with ASCII art and game intro |
| Dock | Unstaffed docks, cold ocean, your boat is anchored here |
| Welcome area | Open deck overlooking the superstructure -- central hub |

### Recreation & Community

| Room | Description |
|------|-------------|
| Stairwell | Pastel-enameled steel stairway |
| Outer courtyard | Large outdoor space with synthetic grass |
| Tennis courts | Abandoned -- "no one ever seems to be playing" |
| Community garden | Herbs, vegetables, synthesized plants, popsicle stick markers |
| Pool | Outdoor, smells of chlorine, sunset turns water purple |
| Inner courtyard | Smaller space with waxy tropical plants, rock garden, statue |
| Cafetorium | Community dining facility with buffet service |
| Library | Mostly empty shelves, deactivated mimex machines, mutoscope |
| Pet shelter | Animals in kennels and cages |
| Gallery | "Formless void" art space, objects suspended in illuminated darkness. Contains boutique counter. |
| Fashion District | Narrow promenade of repurposed shipping containers off the inner courtyard. Contains trading post. |
| Gourmand Shop | Cozy storefront off the Fashion District with refrigerated display case. Contains food stall. |

### Residential -- Eastern Complex

| Room | Description |
|------|-------------|
| Eastern complex | Hallway with apartments, someone dropped a sock |
| room101 | One-bedroom apartment, contains wardrobe |
| room102 | Studio -- well-made bed, folded laundry, framed photo of a terrier |
| apartment 103 | Contains mimex terminal entry |
| Shared bathroom | Communal facilities |

### Residential -- Western Complex

| Room | Description |
|------|-------------|
| Western complex | Hallway with resident art on display |
| room201 | "Whoever lives here must be pretty boring" |
| room202 | Half dusty, half clean and well-used |
| 203 | Contains mimex terminal entry |
| Shared bathroom | Communal facilities |
| Stairwell (lower) | Access to sublevels |

### Industrial Park

| Room | Description |
|------|-------------|
| Veloway | Segmented asphalt strip with bike and cargo tuk-tuk lanes |
| Western veloway | Extension of transportation loop |
| Industrial park | Central manufacturing hub connecting all workshops |
| Textile megaspools | Robotic weaving of itemated substances into textiles |
| Laser | Communication array for inter-LSU contact, Tesla death-ray (still in packaging) |
| Glazier | Transparent aluminum forging, glass and acrylic production |
| Wax extruders | Metal orifices extruding wax, robotic squeegee-spades |
| Polyclay intubators | Giant pipes in narrow industrial space |
| "Milk" vats | 20-foot tall vats of artificial milks, cloying odor |
| Confectionary tanks | Protein sludges and sugar analogues, electronic synthose smell |

### Ceremonial

| Room | Description |
|------|-------------|
| KonMarie Temple | Wood and stone structure, central incinerator, smells of woodsmoke and lemons |

### Virtual/Mimex Zones

| Room | Description |
|------|-------------|
| Mimex (apt 103) | Virtual terminal screen |
| Journal | Lore-locked by "prevention of parahistory working group" |
| Jamais Vu | ASCII art detective adventure game |
| The past | Story room -- playing games at a wealthy person's party |
| The future | Dusty limestone cave with moon imagery |
| Bathroom stall | Nightmare scenario room |
| Walkthrough | Game guide content |
| Mimex (apt 203) | Creative/gaming library terminal |
| Choose Your Own Experiment | Interactive fiction |
| RPG(ish) Plays | Tabletop RPG content |
| Fiasco Playsets | Fiasco game content |
| Ren'Py Light Novels | Visual novel content |
| Gaming Writing | Game writing collection |
| Twine Collabs | Collaborative Twine projects |
| Collective Experiments | Experimental collaborative works |

### Sublevels

| Room | Description |
|------|-------------|
| 000 | Dark sublevel with electrical buzzing |
| Crawlspace | Waist-deep dusty space with warm pipes |

## Permanent Fixtures

### Itemators (Object Wombs) -- 9 total

Procedural item generation devices scattered across the world. Players `use` them to create random items.

Located in: Limbo, Glazier, Confectionary tanks, Library, The future, and several other rooms.

### Workshop Equipment (6 stations)

Each workshop has a **MaterialWomb** (produces raw materials) and a **Workbench** (combines two materials):

| Station | Room | MaterialWomb name | Workbench |
|---------|------|-------------------|-----------|
| textile | Textile megaspools | material extruder | textile workbench |
| glazier | Glazier | glass furnace | glazier workbench |
| wax | Wax extruders | wax extruder | wax workbench |
| clay | Polyclay intubators | clay intubator | clay workbench |
| milk | "Milk" vats | bio-vat | milk workbench |
| candy | Confectionary tanks | confection dispenser | candy workbench |

### Shops

Deployed via one-time deploy scripts (now deleted).

| Shop | Type | Location | Description |
|------|------|----------|-------------|
| trading post | GeneralStoreCounter | Fashion District | Sells general goods -- talismans, garments, books |
| food stall | FoodMarketCounter | Gourmand Shop | Sells cheese, ice cream, and other edible items |
| boutique counter | BoutiqueCounter | Gallery | Sells haute couture garments and masterpiece artwork |

The **Fashion District** connects to the Inner courtyard; the **Gourmand Shop** connects to the Fashion District.

### Display Shelves

Players `claim` a shelf to take ownership, then `display`/`retrieve` items. Items on a claimed shelf count toward the owner's item total for hoarding enforcement (same as inventory). `unclaim` releases ownership. Items on shelves count at reduced weight (0.5) toward the platform total.

### Other Fixtures

| Object | Location | Description |
|--------|----------|-------------|
| Incinerator | KonMarie Temple | Dark metal box for item disposal/ritual, radiates warmth and gratitude |
| Counter signs (x2) | Dock, Inner courtyard | Dynamic signs showing platform status, economy stats, citizen inventories, masterpieces, displayed items |
| Mutoscope | Library | Giant revolving wheel of paper cards creating illusion of moving images |
| Boat | Dock | The vessel you arrived in |
| Mirror | (various) | Prompts looker to set their character description |

### Unique Objects

| Object | Description |
|--------|-------------|
| Egg | "A sacred thing" -- mysterious object |

### Books

11 procedurally generated sci-fi books (colored covers) plus 2 unique chapbooks: "Yes Is A Deeper Season" and "Both Is The Most Great"

## Lore Notes

- **KonMarie Temple**: Ceremonial space devoted to "parting with things" -- a Marie Kondo-inspired ritual of mindful discarding. The incinerator is sacred, but also functional: it breaks objects down into reclaimed feedstock that the station's fabrication systems can reuse. Also serves as the endpoint for enforcement actions -- offenders are escorted here for euthanasia and cremation.
- **Material Cycle**: The station runs on a closed material loop. The incinerator and recycling systems break objects down into reusable feedstock. Itemators (object wombs) consume this feedstock to fabricate new things. Ash tokens are an abstraction of this process -- a claim on the communal feedstock supply. The station also recovers material passively from ocean intake, biological waste processing, and industrial runoff, which slowly replenishes the supply. The pool cap (2000) represents physical storage limits for processed feedstock.
- **Ash Economy**: Ash tokens are earned by incinerating items (1 normal, 3 artwork, 2 cursed) or as enforcement rewards. Shops buy items low and sell high, drawing from the station feedstock pool (starts at 500, caps at 2000). The pool recharges slowly from background recovery systems (ocean filtration, waste processing, industrial byproducts). Hoarding fines are recycled into the pool. Shop items expire after 60 minutes to keep stock fresh. The cafetorium serves free food and is not part of the economy.
- **Hoarding Enforcement**: Citizens can `report` hoarders. Minor offenses (10-19 items) incur escalating fines (5, 15 ash, then formal investigation) -- fines are recycled into the station ash pool. Major hoarding (20+ items) or third strike triggers an InvestigationScript with server-wide broadcasts. On completion, a SecurityRobot (chrome enforcement unit, LED scrolling "COMPLIANCE IS COMMUNITY") escorts the offender to the KonMarie Temple. All possessions are destroyed, a 50 ash debt is applied, and the offender respawns at the Welcome area. Reporters split a 25 ash reward. Items on claimed display shelves count toward a player's hoarding total.
- **Gifting**: `gift <item> to <player>` offers an item as a gift. The recipient can `accept` or `reject` the gift. If no response within 60 seconds, the gift is accepted automatically. Room-visible emotes announce gifts to bystanders.
- **Edible Items**: Cheese and ice cream from itemators are edible. Eating them destroys the item, reducing platform weight.
- **Laser/Archimedes Array**: Inter-LSU communication system. Houses a mandatory emergency Tesla death-ray that has never been deployed (still in foam packaging). Mostly big and empty, footsteps echo.
- **Mimex Systems**: Virtual terminal screens in apartments providing access to embedded games, creative writing collections, and documentation.
- **The Eggs**: Recurring mysterious objects. One is described as "sacred," another as crystalline epidote. Their purpose is unclear.
- **Rufus**: A fancy melon with a moustache. Answers to his name.
- **Atmosphere**: Mix of well-maintained and neglected spaces. Tennis courts nobody uses. Dust in half an apartment. An underlying quietness despite the utopian setting.

## Statistics

- 57 rooms (46 standard + 11 hybrid/dynamic) -- includes Fashion District, Gourmand Shop
- 122 exits (67 with aliases) -- includes Fashion District <-> Inner courtyard, Gourmand Shop <-> Fashion District
- ~40 historical player characters
- 6 manufacturing workshops
- 9 itemators
- 3 shops (food stall, trading post, boutique counter)

## Deploy Scripts

One-time deploy scripts were used to place workshops, shops, and initialize the economy. They have been run and deleted. World objects now persist in the database across server reloads.

"""
Shop fixtures for the Zone 25 economy.

ShopCounter objects are placed in rooms (like Incinerators or Workbenches).
They provide browse/buy/sell commands via an EvMenu and direct commands.
Items for sale are stored as contents of the ShopCounter with db.for_sale=True.
"""

from django.conf import settings as conf

from evennia import Command, CmdSet
from evennia.objects.objects import DefaultObject
from evennia.utils.evmenu import EvMenu

from .objects import ObjectParent


# ---------------------------------------------------------------------------
# EvMenu node functions
# ---------------------------------------------------------------------------


def node_shopfront(caller, raw_string, **kwargs):
    """Main shop menu: list items for sale, option to sell."""
    shop = caller.ndb._shop_obj
    if not shop:
        return "The shop seems to be closed.", []

    from world.economy import get_station_pool, get_buy_price, get_sell_price

    pool = get_station_pool()
    stock = shop.get_stock()
    shop_name = shop.db.shop_name or "the shop"

    text = (
        f"|355Welcome to {shop_name}.|n\n"
        f"|555Station ash reserve: {pool}|n\n\n"
    )

    if not stock:
        text += "The shelves are bare. Check back later.\n"
    else:
        text += "|wItems for sale:|n\n"
        for i, item in enumerate(stock, 1):
            price = get_buy_price(item)
            text += f"  |555{i}|n. {item.key} -- |y{price} ash|n\n"

    text += (
        "\nYour ash balance: |y{ash}|n"
    ).format(ash=caller.db.ash_tokens or 0)

    options = []
    for i, item in enumerate(stock):
        price = get_buy_price(item)
        options.append({
            "desc": f"Buy {item.key} ({price} ash)",
            "goto": ("node_buy_confirm", {"item_id": item.id, "price": price}),
        })

    options.append({
        "key": "s",
        "desc": "Sell an item from your inventory",
        "goto": "node_sell_list",
    })
    options.append({
        "key": "q",
        "desc": "Leave",
        "goto": "node_leave",
    })

    return text, options


def node_buy_confirm(caller, raw_string, **kwargs):
    """Confirm purchase of a specific item."""
    from world.economy import get_buy_price, credit_station_pool
    from evennia.utils.search import search_object

    item_id = kwargs.get("item_id")
    price = kwargs.get("price", 0)

    results = search_object(f"#{item_id}")
    if not results:
        return "That item is no longer available.", [
            {"key": "b", "desc": "Back to shop", "goto": "node_shopfront"},
        ]
    item = results[0]

    ash = caller.db.ash_tokens or 0
    text = (
        f"Buy |w{item.key}|n for |y{price} ash|n?\n"
        f"Your balance: |y{ash} ash|n"
    )

    if ash < price:
        text += "\n|500You can't afford this.|n"
        return text, [
            {"key": "b", "desc": "Back to shop", "goto": "node_shopfront"},
        ]

    options = [
        {
            "key": "y",
            "desc": "Yes, buy it",
            "goto": ("_do_buy", {"item_id": item_id, "price": price}),
        },
        {
            "key": "n",
            "desc": "No, go back",
            "goto": "node_shopfront",
        },
    ]
    return text, options


def _do_buy(caller, raw_string, **kwargs):
    """Execute the purchase."""
    from world.economy import credit_station_pool
    from evennia.utils.search import search_object

    item_id = kwargs.get("item_id")
    price = kwargs.get("price", 0)

    results = search_object(f"#{item_id}")
    if not results:
        caller.msg("|500That item vanished before you could buy it.|n")
        return "node_shopfront"

    item = results[0]
    ash = caller.db.ash_tokens or 0
    if ash < price:
        caller.msg("|500You can't afford that.|n")
        return "node_shopfront"

    # Execute transaction
    caller.db.ash_tokens = ash - price
    credit_station_pool(price)

    if item.db.for_sale:
        del item.db.for_sale
    item.move_to(caller, quiet=True)

    caller.msg(
        f"|355You purchase {item.key} for {price} ash. "
        f"Remaining balance: {caller.db.ash_tokens} ash.|n"
    )
    caller.location.msg_contents(
        f"$You() $conj(purchase) something from the shop.",
        from_obj=caller,
        exclude=[caller],
    )

    return "node_shopfront"


def node_sell_list(caller, raw_string, **kwargs):
    """List caller's inventory with sell prices (filtered by shop type)."""
    from world.economy import get_sell_price, get_station_pool, shop_accepts_item

    shop = caller.ndb._shop_obj
    shop_type = shop.db.shop_type if shop else "general"
    pool = get_station_pool()
    items = [
        obj for obj in caller.contents
        if not getattr(obj.db, "worn", False)
        and shop_accepts_item(shop_type, obj)
    ]

    if not items:
        return "You have nothing this shop wants to buy.", [
            {"key": "b", "desc": "Back to shop", "goto": "node_shopfront"},
        ]

    text = "|wItems this shop will buy:|n\n"
    for i, item in enumerate(items, 1):
        price = get_sell_price(item)
        text += f"  |555{i}|n. {item.key} -- |y{price} ash|n\n"

    text += f"\n|555Station can pay up to: {pool} ash|n"

    options = []
    for i, item in enumerate(items):
        price = get_sell_price(item)
        options.append({
            "desc": f"Sell {item.key} ({price} ash)",
            "goto": ("node_sell_confirm", {"item_id": item.id, "price": price}),
        })

    options.append({
        "key": "b",
        "desc": "Back to shop",
        "goto": "node_shopfront",
    })

    return text, options


def node_sell_confirm(caller, raw_string, **kwargs):
    """Confirm selling a specific item."""
    from world.economy import get_sell_price, get_station_pool
    from evennia.utils.search import search_object

    item_id = kwargs.get("item_id")
    price = kwargs.get("price", 0)
    pool = get_station_pool()

    results = search_object(f"#{item_id}")
    if not results:
        return "That item is gone.", [
            {"key": "b", "desc": "Back to shop", "goto": "node_shopfront"},
        ]
    item = results[0]

    text = f"Sell |w{item.key}|n for |y{price} ash|n?"

    if pool < price:
        text += "\n|500The station coffers are too low to buy this.|n"
        return text, [
            {"key": "b", "desc": "Back to shop", "goto": "node_shopfront"},
        ]

    options = [
        {
            "key": "y",
            "desc": "Yes, sell it",
            "goto": ("_do_sell", {"item_id": item_id, "price": price}),
        },
        {
            "key": "n",
            "desc": "No, go back",
            "goto": "node_sell_list",
        },
    ]
    return text, options


def _do_sell(caller, raw_string, **kwargs):
    """Execute the sale."""
    from world.economy import debit_station_pool
    from evennia.utils.search import search_object

    item_id = kwargs.get("item_id")
    price = kwargs.get("price", 0)

    results = search_object(f"#{item_id}")
    if not results:
        caller.msg("|500That item is gone.|n")
        return "node_shopfront"

    item = results[0]

    if not debit_station_pool(price):
        caller.msg("|500The station coffers are empty.|n")
        return "node_shopfront"

    # Pay the player
    ash = caller.db.ash_tokens or 0
    caller.db.ash_tokens = ash + price

    # Move item to the shop counter and mark for resale
    import time

    shop = caller.ndb._shop_obj
    if shop:
        item.db.for_sale = True
        item.db.shop_listed_at = time.time()
        item.move_to(shop, quiet=True)
    else:
        # No shop reference -- just delete the item
        item.delete()

    caller.msg(
        f"|355You sell {item.key} for {price} ash. "
        f"New balance: {caller.db.ash_tokens} ash.|n"
    )
    caller.location.msg_contents(
        f"$You() $conj(sell) something to the shop.",
        from_obj=caller,
        exclude=[caller],
    )

    return "node_shopfront"


def node_leave(caller, raw_string, **kwargs):
    """Exit the shop menu."""
    caller.msg("You step away from the counter.")
    if caller.ndb._shop_obj:
        del caller.ndb._shop_obj
    return None, None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


class CmdBrowse(Command):
    """
    Browse the shop's wares via an interactive menu.

    Usage:
      browse
      shop
    """

    key = "browse"
    aliases = ["shop"]
    locks = "cmd:all()"

    def func(self):
        shop = self.obj
        self.caller.ndb._shop_obj = shop
        EvMenu(
            self.caller,
            "typeclasses.shops",
            startnode="node_shopfront",
            cmd_on_exit=None,
        )


class CmdBuy(Command):
    """
    Buy an item directly from the shop.

    Usage:
      buy <item>
    """

    key = "buy"
    locks = "cmd:all()"

    def func(self):
        from world.economy import get_buy_price, credit_station_pool

        if not self.args:
            self.caller.msg("Buy what? Use |555browse|n to see the stock.")
            return

        shop = self.obj
        stock = shop.get_stock()
        if not stock:
            self.caller.msg("The shop has nothing for sale right now.")
            return

        target = self.args.strip()
        item = None
        for obj in stock:
            if obj.key.lower() == target.lower() or target.lower() in obj.key.lower():
                item = obj
                break

        if not item:
            self.caller.msg(f"The shop doesn't have '{target}' for sale.")
            return

        price = get_buy_price(item)
        ash = self.caller.db.ash_tokens or 0

        if ash < price:
            self.caller.msg(
                f"{item.key} costs {price} ash but you only have {ash}."
            )
            return

        # Execute purchase
        self.caller.db.ash_tokens = ash - price
        credit_station_pool(price)
        if item.db.for_sale:
            del item.db.for_sale
        item.move_to(self.caller, quiet=True)

        self.caller.msg(
            f"|355You purchase {item.key} for {price} ash. "
            f"Remaining: {self.caller.db.ash_tokens} ash.|n"
        )
        self.caller.location.msg_contents(
            f"$You() $conj(purchase) {item.key} from the shop.",
            from_obj=self.caller,
            exclude=[self.caller],
        )


class CmdSell(Command):
    """
    Sell an item from your inventory to the shop.

    Usage:
      sell <item>
    """

    key = "sell"
    locks = "cmd:all()"

    def func(self):
        from world.economy import get_sell_price, debit_station_pool, shop_accepts_item

        if not self.args:
            self.caller.msg("Sell what?")
            return

        item = self.caller.search(self.args.strip(), location=self.caller)
        if not item:
            return

        shop = self.obj
        if not shop_accepts_item(shop.db.shop_type, item):
            self.caller.msg(
                f"This shop doesn't deal in that kind of item."
            )
            return

        price = get_sell_price(item)

        if not debit_station_pool(price):
            self.caller.msg(
                "|500The station coffers are empty -- it can't afford "
                "to buy anything right now.|n"
            )
            return

        ash = self.caller.db.ash_tokens or 0
        self.caller.db.ash_tokens = ash + price

        # Move item to the shop counter for resale
        import time

        shop = self.obj
        item.db.for_sale = True
        item.db.shop_listed_at = time.time()
        item.move_to(shop, quiet=True)

        self.caller.msg(
            f"|355You sell {item.key} for {price} ash. "
            f"New balance: {self.caller.db.ash_tokens} ash.|n"
        )
        self.caller.location.msg_contents(
            f"$You() $conj(sell) {item.key} to the shop.",
            from_obj=self.caller,
            exclude=[self.caller],
        )


class CmdSetShop(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdBrowse())
        self.add(CmdBuy())
        self.add(CmdSell())


# ---------------------------------------------------------------------------
# Shop counter typeclasses
# ---------------------------------------------------------------------------


class ShopCounter(ObjectParent, DefaultObject):
    """
    A shop fixture placed in a room. Provides browse/buy/sell commands.
    Items for sale are stored as contents of the ShopCounter.

    db attributes:
        shop_type: "boutique", "food", or "general"
        shop_name: display name for the shop
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.shop_type = "general"
        self.db.shop_name = "the shop"
        self.cmdset.add_default(CmdSetShop, permanent=True)

    def get_stock(self):
        """Return list of objects currently for sale."""
        return [
            obj for obj in self.contents
            if obj.db.for_sale
            and not getattr(obj, "destination", None)
        ]

    def restock(self):
        """Generate new items up to SHOP_MAX_INVENTORY. Expires stale items first."""
        import time
        from world.economy import generate_shop_inventory
        from evennia.prototypes.spawner import spawn

        # Expire stale items before restocking
        ttl = getattr(conf, "SHOP_ITEM_TTL", 3600)
        now = time.time()
        for obj in list(self.contents):
            if obj.db.for_sale and obj.db.shop_listed_at:
                if now - obj.db.shop_listed_at > ttl:
                    obj.delete()

        max_inv = getattr(conf, "SHOP_MAX_INVENTORY", 8)
        current = self.get_stock()
        if len(current) >= max_inv:
            return

        count = getattr(conf, "SHOP_RESTOCK_COUNT", 3)
        needed = min(count, max_inv - len(current))
        if needed <= 0:
            return

        protos = generate_shop_inventory(self.db.shop_type, needed)
        for proto in protos:
            new_obj = spawn(proto)[0]
            new_obj.location = self

            # Set db attributes from proto
            for attr in ("artwork", "cursed", "readable_text", "edible",
                         "flavor_text", "flavor_words", "weight_fraction"):
                val = proto.get(attr)
                if val is not None:
                    setattr(new_obj.db, attr, val)

            new_obj.db.for_sale = True
            new_obj.db.shop_item = True
            new_obj.db.shop_listed_at = now

    def return_appearance(self, looker, **kwargs):
        from world.economy import get_buy_price

        appearance = super().return_appearance(looker, **kwargs)
        stock = self.get_stock()
        if stock:
            item_list = "\n".join(
                f"  {item.key} -- |y{get_buy_price(item)} ash|n"
                for item in stock
            )
            stock_text = f"\n|wFor sale:|n\n{item_list}"
        else:
            stock_text = "\nThe shelves are bare."
        hint = (
            "\n|555browse|n to shop, |555buy <item>|n, "
            "or |555sell <item>|n."
        )
        return (appearance or "") + stock_text + hint


class BoutiqueCounter(ShopCounter):
    """Art and haute couture shop. High-end goods."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.shop_type = "boutique"
        self.db.shop_name = "the Gallery Boutique"


class FoodMarketCounter(ShopCounter):
    """Specialty food shop: cheese, ice cream, delicacies."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.shop_type = "food"
        self.db.shop_name = "the Specialty Food Market"


class GeneralStoreCounter(ShopCounter):
    """General goods: talismans, garments, books, poems."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.shop_type = "general"
        self.db.shop_name = "the Trading Post"

# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Items and weapon templates.

This module defines simple data containers for `Weapon` and `Item` and
helpers used by the game and persistence layer. Loot generation was
migrated to `game/loot.py`; this module focuses on templates,
serialization (`to_dict`/`from_dict`) and small pricing helpers used
by the merchant and sell logic.
"""

from dataclasses import dataclass
from .utils import rnd
import random

@dataclass
class Weapon:
    name: str
    level_req: int
    damage_range: tuple
    rarity: float = 1.0
    class_req: str = None
    # starter/bound weapons cannot be sold or lost on death
    starter: bool = False
    bound: bool = False

    def dmg(self):
        """Return a random damage value in this weapon's damage range.

        Uses `rnd(a, b)` wrapper which maps to `random.randint(a, b)` so
        unit tests can control randomness by seeding `random`.
        """
        return rnd(self.damage_range[0], self.damage_range[1])

    def __repr__(self):
        return f"{self.name} (Lv{self.level_req}) [{self.damage_range[0]}-{self.damage_range[1]} dmg]"

    def to_dict(self):
        return {
            'name': self.name,
            'level_req': self.level_req,
            'damage_range': list(self.damage_range),
            'rarity': self.rarity,
            'class_req': self.class_req,
            'starter': self.starter,
            'bound': self.bound,
        }

    @staticmethod
    def from_dict(d):
        if not d:
            return None
        return Weapon(d['name'], int(d['level_req']), tuple(d['damage_range']), float(d.get('rarity',1.0)), d.get('class_req'), starter=bool(d.get('starter',False)), bound=bool(d.get('bound',False)))

@dataclass
class Item:
    name: str
    kind: str
    effect: dict = None

    def __repr__(self):
        return f"{self.name} ({self.kind})"

    def to_dict(self):
        # effect may contain a weapon object; serialize if present
        # `effect` may be None, a plain dict, or contain embedded Weapon
        # objects (for weapon Items). We serialize Weapon objects using a
        # sentinel key `__weapon__` so `from_dict` can rehydrate them.
        eff = None
        if self.effect is None:
            eff = None
        else:
            # shallow copy but convert any Weapon objects inside
            eff = {}
            for k, v in self.effect.items():
                if isinstance(v, Weapon):
                    eff[k] = {'__weapon__': v.to_dict()}
                else:
                    eff[k] = v
        return {'name': self.name, 'kind': self.kind, 'effect': eff}

    @staticmethod
    def from_dict(d):
        if not d:
            return None
        eff = d.get('effect')
        parsed = None
        if eff is None:
            parsed = None
        else:
            parsed = {}
            for k, v in eff.items():
                if isinstance(v, dict) and '__weapon__' in v:
                    parsed[k] = Weapon.from_dict(v['__weapon__'])
                else:
                    parsed[k] = v
        return Item(d.get('name'), d.get('kind'), parsed)

# Weapon templates (5 per class, last is rare)
WEAPONS = {
    'Warrior': [
        Weapon('Iron Longsword', 5, (6,10), rarity=0.9, class_req='Warrior'),
        Weapon('Steel Cleaver', 7, (9,14), rarity=0.6, class_req='Warrior'),
        Weapon('Berserker Axe', 10, (13,20), rarity=0.4, class_req='Warrior'),
        Weapon('Guardian Blade', 12, (15,22), rarity=0.2, class_req='Warrior'),
        Weapon('Heartseeker, Ancient', 18, (22,35), rarity=0.05, class_req='Warrior'),
    ],
    'Mage': [
        Weapon('Oak Staff', 5, (4,8), rarity=0.9, class_req='Mage'),
        Weapon('Crystal Wand', 7, (7,12), rarity=0.6, class_req='Mage'),
        Weapon('Starlit Rod', 10, (10,16), rarity=0.4, class_req='Mage'),
        Weapon('Rune Scepter', 13, (14,20), rarity=0.2, class_req='Mage'),
        Weapon('Archmage Focus', 18, (20,34), rarity=0.05, class_req='Mage'),
    ],
    'Ranger': [
        Weapon('Shortbow', 5, (5,9), rarity=0.9, class_req='Ranger'),
        Weapon('Composite Bow', 8, (8,13), rarity=0.6, class_req='Ranger'),
        Weapon('Windrunner', 11, (11,17), rarity=0.4, class_req='Ranger'),
        Weapon('Hawkstrike', 14, (15,21), rarity=0.2, class_req='Ranger'),
        Weapon('Eagle of Dathen', 18, (18,32), rarity=0.05, class_req='Ranger'),
    ],
}

# Starter weapons - given to players at start; low stats and bound/starter=True
STARTER_WEAPONS = {
    'Warrior': Weapon('Rusty Sword', 1, (1,3), rarity=1.0, class_req='Warrior', starter=True, bound=True),
    'Mage': Weapon('Basic Staff', 1, (1,3), rarity=1.0, class_req='Mage', starter=True, bound=True),
    'Ranger': Weapon('Basic Bow', 1, (1,3), rarity=1.0, class_req='Ranger', starter=True, bound=True),
}

MONSTER_WEAPONS = []

MONSTER_ITEM_POOL = [
    Item('Lesser Health Potion', 'potion', {'hp':25}),
    Item('Greater Health Potion', 'potion', {'hp':50}),
]

# Junk sellable items
BRONZE_SCRAP = Item('Bronze Scrap', 'junk', {'sell': 2})
SILVER_ROCK = Item('Silver Rock', 'junk', {'sell': 5})
GOLD_CLUMP = Item('Gold Clump', 'junk', {'sell': 10})

# Include junk in the monster item pool so players can find sellables
MONSTER_ITEM_POOL.extend([BRONZE_SCRAP, SILVER_ROCK, GOLD_CLUMP])

# Special key item used to unlock the boss room
KEY_ITEM = Item('Ancient Ruins Key', 'key', {})

# Loot generation moved to `game.loot` for clearer separation of concerns.


def get_weapon_by_name(name):
    """Return a Weapon instance from the WEAPONS templates by its name, or None."""
    if not name:
        return None
    for pool in WEAPONS.values():
        for w in pool:
            if w.name == name:
                return w
    return None


def is_super_rare_weapon(weapon):
    """Return True if a weapon is considered the super-rare, bound-to-player item.

    We treat weapons with rarity <= 0.05 as super-rare and non-sellable.
    """
    if not weapon:
        return False
    return getattr(weapon, 'rarity', 1.0) <= 0.05


def estimate_sell_price(item):
    """Return estimated sell price for `item`, or `None` if not sellable.

    - Junk: uses `effect['sell']`.
    - Weapon: looks up its template and returns `level_req * 10` when sellable.
    - Other kinds: return `None`.
    """
    if not item:
        return None
    if getattr(item, 'kind', None) == 'junk':
        return int(item.effect.get('sell', 0)) if item.effect else 0
    if getattr(item, 'kind', None) == 'weapon':
        # Item.effect may embed a `weapon` object or be a reference by name
        w = item.effect.get('weapon') if item.effect else None
        if not w:
            w = get_weapon_by_name(item.name)
        if not w:
            return None
        # super-rare or bound/starter weapons are not sellable
        if is_super_rare_weapon(w) or getattr(w, 'bound', False) or getattr(w, 'starter', False):
            return None
        return int(w.level_req * 10)
    return None


def estimate_resell_price(item):
    """Estimate how much a merchant would resell `item` for (or None).

    For junk: same as sell price. For weapons: `level_req * 12` if template exists.
    """
    if not item:
        return None
    if getattr(item, 'kind', None) == 'junk':
        return int(item.effect.get('sell', 0)) if item.effect else 0
    if getattr(item, 'kind', None) == 'weapon':
        # Merchant resale uses a slightly higher coefficient than player
        # sell price so merchants can profit on transactions.
        w = item.effect.get('weapon') if item.effect else None
        if not w:
            w = get_weapon_by_name(item.name)
        if w:
            return int(w.level_req * 12)
    return None

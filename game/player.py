# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Player class and class-specific stat helpers.

This module wraps the `Player` class (subclass of `Creature`) and
functions that define base stats and per-level gains for each class.
"""

from .creature import Creature
from .items import Item
from .utils import rnd
from .items import WEAPONS
from .utils import MAX_LEVEL


def class_base_stats(pclass, level):
    """Return base stats for a class at `level`.

    The returned mapping contains keys: ``hp``, ``mp``, ``atk``, ``def``.
    These values are used during `Player` construction to initialize max
    hitpoints, mana, attack and defense. The formulas are intentionally
    simple and tuned per-class.
    """
    if pclass == 'Warrior':
        return {'hp': 80 + level * 10, 'mp': 20 + level * 2, 'atk': 12 + level * 2, 'def': 8 + level}
    if pclass == 'Mage':
        return {'hp': 50 + level * 6, 'mp': 80 + level * 8, 'atk': 8 + level, 'def': 4 + level//2}
    if pclass == 'Ranger':
        return {'hp': 65 + level * 8, 'mp': 40 + level * 4, 'atk': 11 + level*1.5, 'def': 6 + level//1.5}
    return {'hp': 60, 'mp': 30, 'atk': 10, 'def': 5}


def class_level_gains(pclass):
    """Return the per-level stat gains for a class.

    The dictionary keys align with the `Creature` attributes that are
    increased on level up. These gains are applied in
    ``Player._apply_level_up``.
    """
    if pclass == 'Warrior':
        return {'hp': 10, 'mp': 2, 'atk': 2, 'def': 1}
    if pclass == 'Mage':
        return {'hp': 6, 'mp': 8, 'atk': 1, 'def': 0}
    if pclass == 'Ranger':
        return {'hp': 8, 'mp': 4, 'atk': 1, 'def': 1}
    return {'hp': 8, 'mp': 3, 'atk': 1, 'def': 1}

class Player(Creature):
    """Player character with inventory, equipment and progression helpers.

    This class extends `Creature` with RPG-style progression (XP/levels), an
    inventory with limits, equipment (currently only a weapon slot), and
    convenience methods for equipping, selling, and saving/loading state.

    Notes:
    - Starter weapons (from `items.STARTER_WEAPONS`) are treated as bound
      and are equipped automatically when present.
    - Inventory items are expected to be `Item` instances; some legacy
      save formats are tolerated by `load_state`.
    """

    def __init__(self, name, pclass, level=5):
        self.pclass = pclass
        self.level = level
        base = class_base_stats(pclass, level)
        super().__init__(name, level, base['hp'], base['mp'], base['atk'], base['def'])
        self.xp = 0
        self.inventory = []
        self.equipment = {'weapon': None}
        self.gold = 0
        self.last_hit = False
        # Each player tracks their own position so players can split up
        self.pos = (0, 0)
        # Inventory limit
        self.inv_limit = 30
        # Track death penalties
        self.death_count = 0
        # Give starter weapon for class (bound, cannot be sold or lost)
        try:
            from .items import STARTER_WEAPONS, Item
            starter = STARTER_WEAPONS.get(self.pclass)
            if starter:
                # equip starter weapon and also keep it in equipment; do not place in inventory
                self.equipment['weapon'] = starter
        except Exception:
            pass

    def level_up_check(self):
        """Check XP against thresholds and apply level-ups.

        This method will repeatedly increase the player's level while their XP
        meets the next-level threshold. The helper `xp_for_level` provides the
        required XP for each level. Leveling applies the per-class gains and
        restores HP/MP to the new maxima.
        """
        from .utils import xp_for_level
        # Keep leveling while XP meets next-level threshold.
        while self.level < MAX_LEVEL and self.xp >= xp_for_level(self.level + 1):
            self.level += 1
            self._apply_level_up()
            # Informational: leveling prints are fine during interactive runs
            print(f"{self.name} leveled up! Now level {self.level}.")

    def _apply_level_up(self):
        """Apply the per-level stat gains for the player's class.

        This updates max HP/MP, attack and defense and fully restores the
        player's current HP/MP to the new maxima.
        """
        gains = class_level_gains(self.pclass)
        self.max_hp += gains['hp']
        self.max_mp += gains['mp']
        self.atk += gains['atk']
        self.defense += gains['def']
        self.hp = self.max_hp
        self.mp = self.max_mp

    def equip(self, weapon):
        """Attempt to equip `weapon`.

        Returns True on success, False otherwise. Equipment checks include
        class requirements and level requirements. The method prints a user
        friendly message on failure which is acceptable for interactive use.
        """
        # Verify class and level requirements.
        if weapon.class_req and weapon.class_req != self.pclass:
            print("Cannot equip this weapon (class mismatch).")
            return False
        if self.level < weapon.level_req:
            print("Level too low to equip this weapon.")
            return False
        self.equipment['weapon'] = weapon
        print(f"{self.name} equips {weapon.name}.")
        return True

    def attack_damage(self):
        """Compute attack damage for this player for a single attack.

        The damage is derived from the player's attack stat plus weapon
        damage when equipped, with a small random variance applied. The
        result is clamped to a minimum of 1.
        """
        base = self.atk
        w = self.equipment.get('weapon')
        if w:
            base += w.dmg()
        return max(1, base + rnd(-2, 2))

    def save_state(self):
        """Return a JSON-serializable snapshot of the player's state.

        The returned mapping is intentionally conservative and compatible with
        the existing `Player.load_state` implementation. Equipment is stored
        as a single weapon dict (or ``None``) and inventory items are
        converted via `to_dict()` when available.
        """
        return {
            'name': self.name,
            'pclass': self.pclass,
            'level': self.level,
            'xp': self.xp,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'mp': self.mp,
            'max_mp': self.max_mp,
            'atk': self.atk,
            'defense': self.defense,
            'inventory': [ (i.to_dict() if hasattr(i,'to_dict') else {'name':str(i),'kind':'misc','effect':None}) for i in self.inventory],
            'equipment': (self.equipment['weapon'].to_dict() if self.equipment['weapon'] else None),
            'gold': self.gold,
            'pos': self.pos,
            'death_count': self.death_count,
            'inv_limit': self.inv_limit
        }

    @staticmethod
    def load_state(data):
        """Create a new `Player` from serialized `data`.

        This method tolerates some legacy save formats (tuple-based inventory
        entries or equipment saved as a weapon name). It prefers using the
        `Item.from_dict`/`Weapon.from_dict` helpers when available.
        """
        # Create a new Player instance and rehydrate fields from saved data
        p = Player(data['name'], data['pclass'], data['level'])
        p.xp = data['xp']
        p.hp = data['hp']
        p.max_hp = data['max_hp']
        p.mp = data['mp']
        p.max_mp = data['max_mp']
        p.atk = data['atk']
        p.defense = data['defense']
        # Rehydrate inventory items
        from .items import Item as ItemClass
        inv = []
        for it in data.get('inventory', []):
            try:
                if isinstance(it, dict) and it.get('name'):
                    inv.append(ItemClass.from_dict(it))
                else:
                    # legacy tuple format
                    n, k, e = it
                    inv.append(ItemClass(n, k, e))
            except Exception:
                pass
        p.inventory = inv
        p.gold = data.get('gold', 0)
        p.pos = tuple(data.get('pos', (0, 0)))
        p.death_count = data.get('death_count', 0)
        p.inv_limit = data.get('inv_limit', 30)
        # Rehydrate equipped weapon if present (saved as dict via to_dict)
        equip_data = data.get('equipment')
        if equip_data:
            from .items import Weapon
            try:
                # if equip_data looks like a weapon dict
                if isinstance(equip_data, dict) and equip_data.get('name'):
                    p.equipment['weapon'] = Weapon.from_dict(equip_data)
                else:
                    # legacy: equip stored as name; try lookup
                    from .items import get_weapon_by_name
                    w = get_weapon_by_name(equip_data)
                    if w:
                        p.equipment['weapon'] = w
            except Exception:
                pass
        return p

    def add_item(self, item):
        """Add an item to inventory if space allows.

        Returns True if the item was added, False if the inventory limit was
        reached. Caller is responsible for user-facing messaging; this method
        prints a message for interactive convenience.
        """
        if len(self.inventory) >= self.inv_limit:
            print(f"{self.name}'s inventory is full (limit {self.inv_limit}).")
            return False
        self.inventory.append(item)
        return True

    def sell_item(self, idx):
        """Sell an inventory item by index (0-based).

        Returns a tuple ``(price, sold_item)`` on success, or ``None`` when the
        item cannot be sold (invalid index, bound/starter/super-rare items,
        or otherwise unsellable). Price estimation is delegated to
        `items.estimate_sell_price` to centralize pricing logic.
        """
        try:
            it = self.inventory[idx]
        except Exception:
            print('Invalid item index.')
            return None
        # Use centralized price estimation to keep logic consistent
        from .items import estimate_sell_price, is_super_rare_weapon
        price = estimate_sell_price(it)
        if price is None:
            # If weapon might be non-sellable due to rarity/bound flags, give a helpful message
            if getattr(it, 'kind', None) == 'weapon':
                w = it.effect.get('weapon') if it.effect else None
                if not w:
                    from .items import get_weapon_by_name
                    w = get_weapon_by_name(it.name)
                if w and is_super_rare_weapon(w):
                    print('This item is bound and cannot be sold.')
                    return None
                if w and (getattr(w, 'bound', False) or getattr(w, 'starter', False)):
                    print('This item is bound or a starter weapon and cannot be sold.')
                    return None
            print('This item cannot be sold here.')
            return None
        # Proceed with sale
        sold = self.inventory.pop(idx)
        self.gold += price
        print(f"{self.name} sells {sold.name} for {price} gold.")
        return price, sold

    def lose_random_items(self, count):
        """Remove up to `count` random items from inventory.

        Items that are protected (revive tokens, super-rare weapons, bound or
        starter weapons) are excluded from removal. The method returns a list
        of removed items (which may be empty). Removal is implemented by
        selecting indices and popping them in descending order to avoid
        reindexing issues.
        """
        import random
        removed = []
        candidates = []
        from .items import get_weapon_by_name, is_super_rare_weapon
        for i, it in enumerate(self.inventory):
            # Do not allow removal of revive tokens
            if it.kind == 'revive':
                continue
            # If weapon and super rare, skip
            if it.kind == 'weapon':
                w = it.effect.get('weapon') if it.effect else None
                if not w:
                    w = get_weapon_by_name(it.name)
                if w and is_super_rare_weapon(w):
                    continue
                # skip bound or starter weapons from being dropped
                if getattr(w, 'bound', False) or getattr(w, 'starter', False):
                    continue
            candidates.append(i)
        if not candidates:
            return removed
        k = min(len(candidates), count)
        picks = random.sample(candidates, k)
        # Remove highest indices first to avoid reindexing issues
        for idx in sorted(picks, reverse=True):
            removed_item = self.inventory.pop(idx)
            removed.append(removed_item)
        return removed

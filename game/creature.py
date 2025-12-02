# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Basic Creature model.

This module defines the `Creature` type used for monsters and simple NPCs.
Keep it lightweight: health, attack/defense stats, and xp_value for kills.
Methods are intentionally simple to make testing and serialization easy.
"""


class Creature:
    def __init__(self, name, level, hp, mp, atk, defense, special=None, xp_value=0):
        """Minimal creature representation used for monsters and NPCs.

        The class intentionally keeps behavior light — it's primarily a data
        holder for HP/MP and basic combat stats. Higher-level game logic
        (damage formulas, status effects, AI) should live outside this
        class to keep it easy to test and serialize.

        Args:
            name: display name of the creature.
            level: integer level used for scaling and XP calculations.
            hp: base/max hit points.
            mp: base/max mana points.
            atk: base attack value.
            defense: base defense value.
            special: optional tag used by dungeon generation or bosses.
            xp_value: XP awarded to players when this creature is killed.
        """
        # identity and growth
        self.name = name
        self.level = level
        # HP / MP and current values
        self.max_hp = hp
        self.hp = hp
        self.max_mp = mp
        self.mp = mp
        # combat stats
        self.atk = atk
        self.defense = defense
        # optional special marker (e.g. 'elite_key') and XP reward
        self.special = special
        self.xp_value = xp_value

    def is_alive(self):
        """Return True if the creature has remaining hit points.

        This is the canonical liveliness check used by combat loops.
        """
        return self.hp > 0

    def take_damage(self, d: int) -> int:
        """Apply incoming damage `d` to this creature.

        The method clamps HP at zero and returns the actual hitpoint loss.
        Damage calculation (armor mitigation, criticals, etc.) is expected
        to be performed by the caller — this method only applies the final
        damage value.

        Returns:
            The integer amount of HP removed (may be less than `d` if the
            creature was already low on HP).
        """
        prev = self.hp
        self.hp = max(0, self.hp - int(d))
        return prev - self.hp

    def heal(self, amount):
        """Restore hitpoints by `amount`, capped at `max_hp`.

        The method is safe to call even when the creature is at zero HP; it
        simply increases the HP value (calling code may decide if healing a
        dead creature should trigger revive semantics).
        """
        self.hp = min(self.max_hp, self.hp + amount)

    def to_dict(self) -> dict:
        """Return a serializable snapshot of this creature's state."""
        return {
            'name': self.name,
            'level': self.level,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'mp': self.mp,
            'max_mp': self.max_mp,
            'atk': self.atk,
            'defense': self.defense,
            'special': self.special,
            'xp_value': self.xp_value,
        }

    @staticmethod
    def from_dict(data: dict) -> 'Creature':
        """Recreate a Creature from a dict produced by `to_dict`.

        This helper is convenient for tests and for any code that serializes
        creature state across layers. It tolerates missing keys by using
        sensible defaults.
        """
        name = data.get('name', 'Unknown')
        level = data.get('level', 1)
        max_hp = data.get('max_hp', data.get('hp', 1))
        max_mp = data.get('max_mp', data.get('mp', 0))
        atk = data.get('atk', 1)
        defense = data.get('defense', 0)
        c = Creature(name, level, max_hp, max_mp, atk, defense, data.get('special'), data.get('xp_value', 0))
        c.hp = data.get('hp', c.max_hp)
        c.mp = data.get('mp', c.max_mp)
        return c

    def __repr__(self):
        return f"{self.name} (Lv{self.level}) HP:{self.hp}/{self.max_hp}"

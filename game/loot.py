# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Centralized loot generation helpers.

This module contains the randomized loot-generation utilities used by the
game. Loot rules are intentionally simple and tunable; keeping them in one
place makes unit testing and balance adjustments easier.

Two primary helpers are provided:
- ``generate_loot(level)``: attempt to produce a weapon appropriate for a
    requested level (or ``None`` if no weapon is generated).
- ``generate_chest(player_levels)``: generate a single chest reward based on
    party levels — may return a `Weapon`, a consumable `Item` (potion), or a
    gold pouch `Item`.

Design notes:
- The functions use small probability thresholds (e.g. 30%, 40%) to control
    how often higher-value items appear. These numbers are intentionally
    expressed in the code so they can be adjusted during tuning.
- Weapon selection is weighted by each weapon's ``rarity`` attribute so that
    rarer weapons are less likely to be selected unless they explicitly have
    higher weight.
"""

import random
from typing import Optional, Sequence

from .items import WEAPONS, Item
from .utils import rnd


def generate_loot(level: int) -> Optional[object]:
        """Attempt to return a weapon appropriate for `level`.

        Behavior and rationale:
        - There is a ~30% chance the call will attempt to return a weapon. This
            keeps weapon drops relatively uncommon compared to consumables/gold.
        - A weapon class is chosen at random from `WEAPONS` and then filtered to
            the candidates near the requested `level` (within +/- 6 levels). If no
            candidates match, the full pool is used as a fallback to avoid empty
            results.
        - Candidate selection uses `random.choices` with weights derived from the
            `rarity` attribute on each weapon object. Higher rarity values increase
            selection probability.

        Returns:
        - A weapon object from the `WEAPONS` pools, or ``None`` when no weapon is
            produced by the roll.
        """
        # Roll to decide whether we attempt a weapon drop (approx 30% chance)
        if rnd(0, 100) > 30:
                return None

        # Pick one weapon class (e.g., 'swords', 'staves') and select a pool
        target_class = random.choice(list(WEAPONS.keys()))
        pool = WEAPONS[target_class]

        # Prefer weapons reasonably close to the player's level to keep drops
        # useful. The +/-6 window is a balance between variety and usefulness.
        candidates = [w for w in pool if abs(w.level_req - level) <= 6]
        if not candidates:
                # Fallback: if no nearby-level weapons, use the full pool instead of
                # returning nothing.
                candidates = pool

        # Build weights from each candidate's rarity to bias selection.
        weights = [getattr(w, 'rarity', 1) for w in candidates]

        # Use weighted random selection; if something goes wrong, fall back to
        # uniform selection to avoid raising during gameplay.
        try:
                choice = random.choices(candidates, weights=weights, k=1)[0]
                return choice
        except Exception:
                return random.choice(candidates)


def generate_chest(player_levels: Sequence[int]) -> object:
        """Generate a chest reward using the average party level.

        The chest generation logic is intentionally simple and uses a few
        probabilistic branches:
        - Determine an integer party level as the average of `player_levels`.
        - 40% chance to attempt to include a weapon (delegates to
            ``generate_loot``). If that call returns a weapon, it is used.
        - Otherwise, fall back to either a healing potion (50%) or a gold
            pouch (50%). Potion and gold values are expressed as `Item` objects so
            they can be handled by existing inventory/serialization code.

        Args:
                player_levels: sequence of player level integers in the party.

        Returns:
                Either a weapon object from `WEAPONS` or an `Item` representing a
                potion or a gold pouch.
        """
        # Compute a reasonable party level; enforce minimum of 1.
        lvl = max(1, sum(player_levels) // len(player_levels))

        # 40% chance the chest contains a weapon. This keeps weapon chests
        # occasional but not frequent for better balance.
        if rnd(0, 100) < 40:
                w = generate_loot(lvl)
                if w:
                        return w

        # No weapon chosen — return a consumable or gold pouch.
        if rnd(0, 100) < 50:
                # Healing potion uses a conservative fixed value; tuning can change
                # potency or introduce tiers later.
                return Item('Greater Health Potion', 'potion', {'hp': 50})

        # Gold pouch with a small random roll for variability.
        return Item('Pouch of Gold', 'gold', {'amount': rnd(30, 120)})

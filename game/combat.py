# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Combat manager and related helpers.

This module implements the turn-based combat loop and small helpers used
by the combat system. The implementation is intentionally small and
test-friendly: all interactive I/O goes through injectable handlers
(`input_handler`, `printer`) so unit tests can simulate player choices
without monkeypatching global builtins.

Key responsibilities:
- Determine initiative and iterate actor turns.
- Provide a `CombatManager` class that encapsulates combat state for
    easier testing and future extension.
- Expose small helpers used by both tests and the interactive CLI such
    as `select_target()` and `apply_item()`.
"""

import random
from .utils import rnd


def initiative_order(players, enemies):
    """Return a shuffled turn order list of tuples ('P'|'E', index).

    Only living players and enemies are included. The function returns a
    list of tuples where the first element is `'P'` for player or `'E'`
    for enemy and the second is the index into the original list. The
    order is shuffled each round to add variety to encounters.
    """
    order = []
    for i, p in enumerate(players):
        if p.is_alive():
            order.append(('P', i))
    for j, e in enumerate(enemies):
        if e.is_alive():
            order.append(('E', j))
    random.shuffle(order)
    return order


def apply_item(player, item, printer=print):
    """Apply a consumable `item` effect to `player`.

    Supported kinds are currently:
    - `'potion'`: heals HP by `item.effect['hp']` (default 0)
    - `'mana'`: restores MP by `item.effect['mp']` (default 0)

    The `printer` is injectable for tests and UI separation.
    """
    if item.kind == 'potion':
        amount = item.effect.get('hp', 0)
        player.heal(amount)
        printer(f"{player.name} uses {item.name} and heals {amount} HP.")
    elif item.kind == 'mana':
        amount = item.effect.get('mp',0)
        player.mp = min(player.max_mp, player.mp + amount)
        printer(f"{player.name} uses {item.name} and restores {amount} MP.")


def use_special(player, enemies, printer=print):
    # Class-based special abilities. Keep these simple and self-contained.
    # Each branch applies predictable effects consumable by tests.
    if player.pclass == 'Warrior':
        from .utils import alive_entities
        live = alive_entities(enemies)

        if not live:
            printer('No targets.')
            return

        target = random.choice(live)
        dmg = int(player.atk * 1.8 + rnd(0,4))
        target.take_damage(dmg)
        printer(f"{player.name} uses 'Cleave' on {target.name} for {dmg} damage.")

        if not target.is_alive():
            player.last_hit = True

    elif player.pclass == 'Mage':
        if player.mp >= 8:
            player.mp -= 8
            from .utils import alive_entities
            live = alive_entities(enemies)
            if not live:
                printer('No targets.')
                return
            for t in live:
                dmg = int(player.atk * 1.2 + rnd(3,7))
                t.take_damage(dmg)
            printer(f"{player.name} casts 'Arcane Burst' across enemies.")
        else:
            printer('Not enough MP!')
    elif player.pclass == 'Ranger':
        if player.mp >= 5:
            player.mp -= 5
            from .utils import alive_entities
            live = alive_entities(enemies)
            if not live:
                printer('No targets.')
                return
            target = random.choice(live)
            dmg = int(player.atk * 1.6 + rnd(1,5))
            target.take_damage(dmg)
            printer(f"{player.name} uses 'Piercing Shot' on {target.name} for {dmg} damage.")
            if not target.is_alive():
                player.last_hit = True
        else:
            printer('Not enough MP!')


def select_target(targets, input_handler=input, printer=print):
    """List alive targets and prompt the user to pick one.

    `targets` is an iterable of entity objects with a sensible `str()`.
    Returns the chosen target object or `None` if the selection is
    invalid or there are no viable targets. Uses `input_handler` for
    testable prompting.
    """
    from .utils import alive_entities
    live = alive_entities(targets)
    if not live:
        return None
    for idx, e in enumerate(live, 1):
        printer(f"{idx}) {e}")
    sel = input_handler("Target #: ")
    try:
        sel = int(sel) - 1
        return live[sel]
    except Exception:
        return None


def player_turn(player, enemies, input_handler=input, printer=print):
    """Backward-compatible wrapper for a player's turn.

    This function remains for backwards compatibility and delegates to
    `CombatManager.player_turn`. Interactive I/O is provided by the
    `input_handler` and `printer` parameters so tests can control
    player choices deterministically.

    Returns `'fled'` when the player successfully flees, otherwise
    returns `None`.
    """
    # Backward-compatible wrapper that delegates to `CombatManager`'s
    # `player_turn` implementation. The full interactive logic now
    # lives on `CombatManager.player_turn` for clarity and testability.
    mgr = CombatManager(players=[], enemies=enemies, input_handler=input_handler, printer=printer)
    return mgr.player_turn(player)


def enemy_action(enemy, players, printer=print):
    """Simple enemy AI action.

    Chooses a target from living players and deals damage based on a
    compact formula. Target selection can be tuned via
    `game.utils.ENEMY_TARGET_MODE` (e.g. 'weakest'). Uses `printer` for
    output so tests can capture enemy messages.
    """
    # backward-compatible wrapper that delegates to CombatManager
    mgr = CombatManager(players=players, enemies=[], printer=printer)
    return mgr.enemy_action(enemy)


def combat(players, enemies, distribute_cb=None, death_cb=None, input_handler=input, printer=print):
    """Run a combat encounter between `players` and `enemies`.

    The function delegates to `CombatManager` to encapsulate state. The
    optional `distribute_cb(enemy, players)` is invoked for each enemy
    defeated (used by the game to award XP and generate loot). An
    optional `death_cb(players)` is called after combat to let the
    caller apply death penalties or respawn logic.
    """
    # Use a CombatManager for encapsulation; keeps legacy API stable
    manager = CombatManager(players, enemies, distribute_cb=distribute_cb, death_cb=death_cb, input_handler=input_handler, printer=printer)
    return manager.run()


class CombatManager:
    """Encapsulate combat state and loop logic for easier extension.

    The manager holds the lists of players and enemies as well as the
    I/O handlers and callback hooks. It exposes `run()` to execute the
    encounter and `player_turn()` / `enemy_action()` methods which can be
    unit-tested directly.
    """

    def __init__(self, players, enemies, distribute_cb=None, death_cb=None, input_handler=input, printer=print):
        self.players = players
        self.enemies = enemies
        self.distribute_cb = distribute_cb
        self.death_cb = death_cb
        self.input_handler = input_handler
        self.printer = printer

    def run(self):
        printer = self.printer
        input_handler = self.input_handler
        # Announce combat and list enemy participants for player clarity
        printer('\nCombat starts!')
        for e in self.enemies:
            printer(f" - {e}")

        # Each round we compute an initiative order and iterate until one
        # side is defeated or a player successfully flees.
        turn_order = initiative_order(self.players, self.enemies)
        fled = False
        while any(p.is_alive() for p in self.players) and any(e.is_alive() for e in self.enemies) and not fled:
            for actor_type, idx in turn_order:
                # Defensive short-circuit: if combat ended while iterating
                if not any(p.is_alive() for p in self.players) or not any(e.is_alive() for e in self.enemies) or fled:
                    break
                if actor_type == 'P':
                    p = self.players[idx]
                    result = self.player_turn(p)
                    if result == 'fled':
                        # A successful flee aborts the encounter and skips
                        # XP/loot distribution.
                        fled = True
                        break
                else:
                    e = self.enemies[idx]
                    if e.is_alive():
                        self.enemy_action(e)
            # Recompute initiative for the next round
            turn_order = initiative_order(self.players, self.enemies)

        printer('Combat ended.')

        # Distribute XP/loot only when players did not flee
        if not fled and self.distribute_cb:
            for e in self.enemies:
                if not e.is_alive():
                    self.distribute_cb(e, self.players)

        # Call the optional death handler to manage respawn/penalties
        if self.death_cb:
            self.death_cb(self.players)
        return None

    def player_turn(self, player):
        """Handle a single player's turn using this manager's I/O and enemy list.

        The method reads a single action from `input_handler` and applies
        it to the combat state. It uses `select_target` and `apply_item`
        helpers for selection and consumable use. Returns `'fled'` when
        the player successfully runs away.
        """
        if not player.is_alive():
            return
        printer = self.printer
        input_handler = self.input_handler
        enemies = self.enemies

        # Short status line showing level, HP and MP
        printer(f"\n{player.name}'s turn (Lv{player.level}) HP:{player.hp}/{player.max_hp} MP:{player.mp}/{player.max_mp}")

        # Action menu (multi-line for clarity)
        printer('\nActions — enter the number of the desired action and press Enter:')
        printer(' 1) Attack       2) Defend      3) Use Item')
        printer(' 4) Special      5) Run')
        choice = input_handler('Action (1-5): ').strip()

        if choice == '1':
            # Attack: choose a live enemy target and apply damage
            target = select_target(enemies, input_handler=input_handler, printer=printer)
            if target is None:
                printer("Invalid target, wasted turn.")
                return
            dmg = player.attack_damage() - target.defense
            dmg = max(1, int(dmg))
            target.take_damage(dmg)
            printer(f"{player.name} hits {target.name} for {dmg} damage.")
            if not target.is_alive():
                printer(f"{target.name} dies!")
                # Mark last hit for XP distribution logic elsewhere
                player.last_hit = True
            else:
                player.last_hit = False

        elif choice == '2':
            # Defend increases defense for simplicity; consider making
            # this a temporary buff in future refactors.
            printer(f"{player.name} braces for incoming attacks (Defend).")
            player.defense += 3

        elif choice == '3':
            # Use an inventory item (consumable). Uses centralized
            # inventory formatting helper to keep UI consistent.
            if not player.inventory:
                printer("No items to use.")
                return
            from .utils import inventory_to_lines
            for line in inventory_to_lines(player.inventory, include_index=True):
                printer(line)
            sel = input_handler('Use item #: ')
            try:
                sel = int(sel)-1
                it = player.inventory.pop(sel)
                apply_item(player, it, printer=printer)
            except Exception:
                printer("Invalid choice.")

        elif choice == '4':
            # Class-based special ability (may consume MP)
            use_special(player, enemies, printer=printer)

        elif choice == '5':
            # Attempt to flee; success aborts the combat loop
            chance = 0.6
            if random.random() < chance:
                printer(f"{player.name} successfully flees from combat!")
                return 'fled'
            else:
                printer(f"{player.name} fails to flee.")
                return None

        else:
            printer("No action taken.")
        return None

    def enemy_action(self, enemy):
        """Enemy AI action using this manager's player list and printer.

        Chooses a target from living players (configurable via
        `game.utils.ENEMY_TARGET_MODE`) and deals damage calculated by a
        compact, readable formula. `printer` is used to emit combat
        messages so tests can capture and assert on them.
        """
        printer = self.printer
        if not enemy.is_alive():
            return
        from .utils import alive_entities
        live = alive_entities(self.players)
        if not live:
            return
        from .utils import ENEMY_TARGET_MODE
        if ENEMY_TARGET_MODE == 'weakest':
            target = min(live, key=lambda pl: pl.hp)
        else:
            target = random.choice(live)
        # Damage formula keeps minimum damage >= 1 and adds small random
        # variance to keep encounters lively.
        dmg = max(1, int(enemy.atk - target.defense * 0.5 + rnd(-1,2)))
        target.take_damage(dmg)
        printer(f"{enemy.name} attacks {target.name} for {dmg} damage.")

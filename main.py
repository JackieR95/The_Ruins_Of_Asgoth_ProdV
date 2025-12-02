# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Top-level CLI for the Ruins of Asgoth game.

This module implements the interactive game loop and a few convenience
helpers used by the CLI (inventory grid display, death handling and XP/loot
distribution). The core game logic remains inside the `game/` package —
this file focuses on presenting menus and wiring together the gameplay
callbacks.

Notes on testability:
- The module uses ``input()`` and ``print()`` directly for the CLI. For
  unit tests, the game logic is exercised via the lower-level functions in
  the `game/` package; this file is primarily intended for manual play and
  light smoke testing.
"""

from game.player import Player
from game.items import WEAPONS, STARTER_WEAPONS, Item
from game.dungeon import Dungeon
from game.combat import combat
from game.save import save_game, load_game

import random
from game.utils import rnd


def handle_deaths(players, dungeon):
    """Process players that died during combat and apply penalties.

    Behavior:
    - If a player has a revive token in their inventory, consume it and
      respawn the player with partial HP/MP without penalty.
    - Otherwise increment the player's death count, remove a small amount
      of gold (capped), randomly drop 1-3 non-protected items, and respawn
      the player at the dungeon start position with partial HP/MP.

    The function prints brief status messages for interactive clarity.
    """
    # Handle players who died during combat: respawn at start, drop one item and some gold
    for p in players:
        if not p.is_alive():
            print(f"\n-- {p.name} has fallen!")
            # Check for revive token: if present, consume and avoid penalties
            revive_idx = None
            for i, it in enumerate(p.inventory):
                # inventory may contain `Item` or raw `Weapon` objects;
                # use getattr to safely check the `kind` attribute.
                if getattr(it, 'kind', None) == 'revive':
                    revive_idx = i
                    break
            if revive_idx is not None:
                p.inventory.pop(revive_idx)
                print(f"{p.name} uses a Revive Token and avoids penalties.")
                # respawn without penalty
                p.pos = dungeon.start_pos
                p.hp = max(1, p.max_hp // 2)
                p.mp = max(0, p.max_mp // 2)
                print(f"{p.name} awakens at {p.pos} with HP {p.hp}/{p.max_hp}.")
                # defensive: ensure player ends up with proper weapon (ancient if present, else starter)
                try:
                    ensure_equipped_weapon(p)
                except Exception:
                    pass
                continue
            # Increment death count and compute gold penalty (capped at 30)
            p.death_count = getattr(p, 'death_count', 0) + 1
            gold_penalty = min(p.death_count, 30)
            lost = min(p.gold, gold_penalty)
            p.gold = max(0, p.gold - lost)
            print(f"{p.name} loses {lost} gold (death count {p.death_count}).")
            # lose some random items (1-3), excluding super-rare and revive tokens
            import random as _r
            num = _r.randint(1, 3)
            removed = p.lose_random_items(num)
            if removed:
                try:
                    lost_names = ', '.join([getattr(it, 'name', str(it)) for it in removed])
                except Exception:
                    lost_names = str(removed)
                print(f"{p.name} lost items on death: {lost_names}")
            # respawn at start with partial HP/MP
            p.pos = dungeon.start_pos
            p.hp = max(1, p.max_hp // 2)
            p.mp = max(0, p.max_mp // 2)
            print(f"{p.name} awakens at {p.pos} with HP {p.hp}/{p.max_hp}.")
            # defensive: ensure player ends up with proper weapon (ancient if present, else starter)
            try:
                ensure_equipped_weapon(p)
            except Exception:
                pass

def choose_class(player_no=1):
    print(f"Choose class for Player {player_no}: 1) Warrior  2) Mage  3) Ranger")
    choice = input('> ').strip()
    mapping = {'1':'Warrior','2':'Mage','3':'Ranger'}
    return mapping.get(choice, 'Warrior')

def show_stats(players):
    for p in players:
        # Show XP as per-level progress: current progress toward next level (progress/required)
        from game.utils import xp_for_level, MAX_LEVEL
        # cumulative XP thresholds
        cur_level_thr = xp_for_level(p.level)
        next_level_thr = xp_for_level(p.level + 1) if p.level < MAX_LEVEL else None
        # Always show the player's total (cumulative) XP, plus per-level progress
        if next_level_thr is None:
            # At max level, show total XP and mark MAX
            xp_display = f"{p.xp} (MAX)"
        else:
            # Show cumulative XP alongside the per-level requirement using
            # a simple `current / required` format (e.g. `110 / 330`). This
            # keeps the values visually connected and avoids the nested
            # parenthetical display.
            required = next_level_thr - cur_level_thr
            # Compute progress toward next level.
            # Backwards-compatible handling:
            # - Some code (and tests) keep `p.xp` as the small per-level
            #   progress value (e.g. 23) while other flows treat `p.xp` as
            #   cumulative total. To support both, if `p.xp` is less than the
            #   cumulative threshold for the current level, treat it as the
            #   per-level progress directly; otherwise subtract the current
            #   level threshold to get per-level progress from a cumulative
            #   value.
            if p.xp < cur_level_thr:
                progress = p.xp
            else:
                progress = max(0, p.xp - cur_level_thr)
            xp_display = f"{progress}/{required}"

        print(f"{p.name} - {p.pclass} Lv{p.level} HP:{p.hp}/{p.max_hp} MP:{p.mp}/{p.max_mp} XP:{xp_display}")


def show_inventory_grid(player):
    """Display a 5×6 inventory grid (30 slots) with full item names and equipped weapon."""
    equipped = player.equipment.get('weapon') if hasattr(player, 'equipment') else None
    eq_name = getattr(equipped, 'name', str(equipped)) if equipped else 'None'
    print(f"\nEquipped: {eq_name}")
    print(f"Gold: {player.gold}")
    slots = 30
    cols = 5
    cell_width = 28
    cells = []
    for i in range(slots):
        if i < len(player.inventory):
            name = player.inventory[i].name
            cell = f"{i+1}:{name}"
        else:
            cell = f"{i+1}: ---"
        cells.append(f"[{cell}]".ljust(cell_width))
    # print rows
    for r in range(0, slots, cols):
        print(' '.join(cells[r:r+cols]))


def ensure_equipped_weapon(player):
    """Ensure a player has an appropriate weapon equipped.

    Priority: if the player has any super-rare / 'ancient' weapon in inventory,
    equip that. Otherwise ensure the class starter weapon is equipped and
    present in inventory.
    """
    from game.items import STARTER_WEAPONS, is_super_rare_weapon, get_weapon_by_name, Item
    # First look for any super-rare weapon in inventory
    for it in player.inventory:
        if it.kind == 'weapon':
            w = it.effect.get('weapon') if it.effect else None
            if not w:
                w = get_weapon_by_name(it.name)
            if w and is_super_rare_weapon(w):
                # equip the ancient/super-rare weapon
                player.equipment['weapon'] = w
                return

    # If nothing ancient found, ensure there's a starter weapon equipped
    if not player.equipment.get('weapon'):
        starter = STARTER_WEAPONS.get(player.pclass)
        if starter:
            # if starter not present as an Item in inventory, add it
            found = False
            for it in player.inventory:
                if it.kind == 'weapon' and it.name == starter.name:
                    found = True
                    break
            if not found:
                player.inventory.append(Item(starter.name, 'weapon', {'weapon': starter}))
            # equip starter (assign directly to avoid equip checks)
            player.equipment['weapon'] = starter
    return

def game_loop():
    print('Welcome to the Ruins of Asgoth')
    print('1) New Game  2) Load Game')
    if input('> ').strip() == '2':
        loaded = load_game()
        if loaded:
            players, dungeon = loaded
        else:
            players = None
    else:
        players = None

    if not players:
        players = []
        for i in range(1,3):
            name = input(f'Name for Player {i}: ') or f'Hero{i}'
            pclass = choose_class(i)
            p = Player(name, pclass, level=5)
            # give the bound starter weapon (use STARTER_WEAPONS so players get starter, not template)
            starter = STARTER_WEAPONS.get(pclass)
            if starter:
                p.inventory.append(Item(starter.name, 'weapon', {'weapon': starter}))
                p.equip(starter)
            p.inventory.append(Item('Lesser Health Potion', 'potion', {'hp':25}))
            players.append(p)
        dungeon = Dungeon(5,5)

    # Navigation is now per-player so players can split up and move independently.
    while True:
        dungeon.draw_map(players)
        # Map legend for players
        print('\nMap Legend: [T]=Trader  [E]=Elite  [B]=Boss  [M]=Monsters  [C]=Chest  [ ]=Empty')
        show_stats(players)
        for p in players:
            if not p.is_alive():
                continue
            print(f"\n{p.name}'s turn. Position: {p.pos}")
            # clearer, multi-line actions menu to reduce mis-keys
            print('\nActions — enter the number of the desired action and press Enter:')
            print(' 1) Forward       2) Left        3) Right       4) Back')
            print(' 5) Inventory     6) Save        7) Quit        8) Restart')
            print(' 9) Help')
            choice = input('Action (1-9): ').strip()
            if choice == '1':
                room = dungeon.move_player(p, 'forward')
            elif choice == '2':
                # Block moving left from the dungeon entrance at (0,0)
                if p.pos == dungeon.start_pos:
                    print('A solid stone wall blocks that way — the ruins entrance is here.')
                    room = dungeon.current_room_for(p)
                else:
                    room = dungeon.move_player(p, 'left')
            elif choice == '3':
                room = dungeon.move_player(p, 'right')
            elif choice == '4':
                # Block moving back from the dungeon entrance at (0,0)
                if p.pos == dungeon.start_pos:
                    print('You cannot go back further — the entrance is behind you.')
                    room = dungeon.current_room_for(p)
                else:
                    room = dungeon.move_player(p, 'back')
            elif choice == '5':
                print(f"\n{p.name} inventory: {p.inventory} | Gold: {p.gold}")
                # show inventory grid and actions
                show_inventory_grid(p)
                print('\nType: `equip <index>`, `use <index>`, `give <index>`, or `skip`')
                cmd = input('> ').strip()
                if cmd.startswith('equip'):
                    try:
                        idx = int(cmd.split()[1]) - 1
                        it = p.inventory[idx]
                        if it.kind == 'weapon' and it.effect.get('weapon'):
                            p.equip(it.effect['weapon'])
                    except Exception:
                        print('Invalid equip.')
                elif cmd.startswith('use'):
                    try:
                        idx = int(cmd.split()[1]) - 1
                        it = p.inventory.pop(idx)
                        from game.combat import apply_item
                        apply_item(p, it)
                    except Exception:
                        print('Invalid use.')
                elif cmd.startswith('give'):
                    # syntax: give <index>
                    try:
                        parts = cmd.split()
                        if len(parts) < 2:
                            print('Usage: give <index>')
                        else:
                            idx = int(parts[1]) - 1
                            # This game is strictly two-player; auto-target the other player
                            if len(players) != 2:
                                print('Give currently only supported in 2-player games.')
                            else:
                                recipient = players[1] if players[0] is p else players[0]
                                if recipient is p:
                                    print('Cannot give to yourself.')
                                elif idx < 0 or idx >= len(p.inventory):
                                    print('Invalid item index.')
                                else:
                                    item = p.inventory[idx]
                                    # prevent giving bound/starter or super-rare weapons
                                    if item.kind == 'weapon':
                                        w = item.effect.get('weapon') if item.effect else None
                                        from game.items import get_weapon_by_name, is_super_rare_weapon
                                        if not w:
                                            w = get_weapon_by_name(item.name)
                                        if w and (getattr(w, 'bound', False) or getattr(w, 'starter', False) or is_super_rare_weapon(w)):
                                            print('This item is bound or cannot be transferred.')
                                        elif len(recipient.inventory) >= recipient.inv_limit:
                                            print(f"{recipient.name}'s inventory is full.")
                                        else:
                                            # ask for confirmation before performing transfer
                                            confirm = input(f"Give {item.name} to {recipient.name}? y/n ").strip().lower()
                                            if confirm != 'y':
                                                print('Give cancelled.')
                                            else:
                                                sold = p.inventory.pop(idx)
                                                recipient.inventory.append(sold)
                                                print(f"{p.name} gave {sold.name} to {recipient.name}.")
                    except Exception:
                        print('Invalid give command. Use: give <index>')
                continue
            elif choice == '6':
                save_game(players, dungeon)
                # Explicit UI confirmation when saving within the game
                try:
                    if isinstance(players, (list, tuple)) and len(players) >= 2:
                        print('Both players saved to savegame.json.')
                    else:
                        print(f"Saved {len(players) if isinstance(players, (list,tuple)) else 1} player(s).")
                except Exception:
                    print('Game saved.')
                continue
            elif choice == '7':
                print('Quit game? y/n')
                if input('> ').strip().lower() == 'y':
                    print('Goodbye.')
                    return None
                continue
            elif choice == '8':
                print('Restart game? Current progress will be lost. y/n')
                if input('> ').strip().lower() == 'y':
                    print('Restarting...')
                    return 'restart'
                continue
            elif choice == '9':
                # brief help text
                print('\nHelp:')
                print('- Move using Forward/Left/Right/Back to navigate the dungeon grid.')
                print('- Inventory lets you equip, use, or give items to teammates.')
                print("  Use: `equip <index>`, `use <index>`, or `give <index> <player_no>` at the inventory prompt.")
                print('- Combat actions: Attack, Defend, Use Item, Special, Run.')
                print('- Adjacent allies will be prompted to join your fights.')
                print('- If you die you respawn at the start, losing some gold and an item.')
                print('- Save to keep progress; Restart will reset the run.')
                input('\nPress Enter to continue...')
                continue

            # Enter the room the player moved into
            room = dungeon.current_room_for(p)
            dungeon.enter_room_for_player(room, p, players, distribute_cb=distribute_xp_loot, death_cb=lambda ps: handle_deaths(ps, dungeon))
            # Refresh status after any room interactions (combat/chest/merchant)
            try:
                show_stats(players)
            except Exception:
                pass

        # after each round of player turns, check if game over (all players dead)
        if all(not p.is_alive() for p in players):
            print('Your party was defeated. Game over.')
            break
        # check boss cleared
        boss_room = [r for r in dungeon.rooms.values() if r.is_boss_room][0]
        if boss_room and not any(e.is_alive() for e in getattr(boss_room,'monsters',[])) and not dungeon.boss_locked:
            print('You have cleared the dungeon! Congratulations!')
            break

# XP and loot distribution callback
from game.loot import generate_loot
from game.items import KEY_ITEM

def distribute_xp_loot(enemy, players):
    # Explicit handling for a two-player game (clarifies behavior):
    # - If both players participated and both are alive, split XP equally.
    # - If only one survived (or only one participated), that survivor gets all XP.
    # For any other participant counts, fall back to a general rule: equal split
    # among surviving participants if >1, else full XP to the sole survivor.
    participants = list(players)
    if not participants:
        return
    alive = [p for p in participants if p.is_alive()]
    if not alive:
        return
    # Allow for defensive fallback: if an enemy has no xp_value set
    # (or it's zero), compute a reasonable default based on level so
    # players always receive XP for kills.
    base_xp = getattr(enemy, 'xp_value', 0) or (10 + enemy.level * 5)
    # Debug trace removed for normal play (XP reporting follows below).
    # Track actual XP awarded per player so we can print clear feedback
    xp_awarded = {p: 0 for p in players}
    last_hit_players = [p for p in participants if p.last_hit]
    winner = last_hit_players[-1] if last_hit_players else random.choice(alive)

    if len(participants) == 2:
        # Two-player-specific logic
        if len(alive) == 2:
            # both alive -> equal split
            share = base_xp // 2
            for p in alive:
                p.xp += share
                xp_awarded[p] += share
            leftover = base_xp - (share * 2)
            if leftover:
                winner.xp += leftover
                xp_awarded[winner] += leftover
        else:
            # only one alive -> that survivor gets all XP
            survivor = alive[0]
            survivor.xp += base_xp
            xp_awarded[survivor] += base_xp
    else:
        # General fallback for N-player scenarios
        if len(participants) > 1 and len(alive) > 1:
            share = base_xp // len(alive)
            for p in alive:
                p.xp += share
                xp_awarded[p] += share
            leftover = base_xp - (share * len(alive))
            if leftover:
                winner.xp += leftover
                xp_awarded[winner] += leftover
        else:
            receiver = alive[0] if len(alive) == 1 else winner
            receiver.xp += base_xp
            xp_awarded[receiver] += base_xp
    # Print explicit XP gain messages so interactive players notice rewards
    for p, amt in xp_awarded.items():
        if amt:
            print(f"{p.name} gains {amt} XP.")

    loot = generate_loot(enemy.level)
    # Special-case: elite that holds the key
    if getattr(enemy, 'special', None) == 'elite_key':
        print(f"{winner.name} receives the Ancient Ruins Key from {enemy.name}!")
        winner.inventory.append(KEY_ITEM)
    else:
        if loot:
            print(f"{winner.name} receives loot: {loot}")
            winner.inventory.append(loot)
    g = rnd(5, 15) * enemy.level
    winner.gold += g
    print(f"{winner.name} gains {g} gold.")
    for p in players:
        p.last_hit = False
    for p in players:
        p.level_up_check()

if __name__ == '__main__':
    # Allow restarting the game loop without relaunching the script.
    while True:
        result = game_loop()
        if result == 'restart':
            # loop to start a fresh run
            continue
        break

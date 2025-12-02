# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Dungeon and room logic.

The dungeon is a small grid of `Room` objects. This module handles
room construction, player movement, and per-room events such as
monsters, chests, merchants and the boss encounter.

Design notes:
- Rooms are lightweight containers with optional `monsters`, `chest`
    and `merchant` fields.
- Interactive prompts are performed via injected `input_handler` and
    `printer` parameters (see `enter_room_for_player`) so unit tests can
    simulate player choices deterministically.
"""

from .creature import Creature
from .combat import combat
from .items import Item
from .loot import generate_chest, generate_loot
from .utils import BOSS_LEVEL
import random

class Room:
    """Simple container representing a dungeon room.

    Public fields:
    - `x`, `y`: room coordinates
    - `visited`: whether this room has been explored
    - `monsters`: list of `Creature` objects present
    - `chest`: loot content (Item or Weapon template)
    - `merchant`: optional `Merchant` instance
    - `is_boss_room`: boolean marker for boss chamber
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visited = False
        self.monsters = []
        self.chest = None
        self.merchant = None
        self.is_boss_room = False

    def ascii(self):
        # Mark special rooms: Boss (B), Elite (E), Trader/Merchant (T), Chest (C), Monsters (M)
        if self.is_boss_room:
            return '[B]'
        if getattr(self, 'special', None) == 'elite':
            return '[E]'
        if self.merchant:
            return '[T]'
        if self.chest:
            return '[C]'
        if self.monsters:
            return '[M]'
        return '[ ]'

class Dungeon:
    def __init__(self, width=5, height=5):
        self.width = width
        self.height = height
        # Build fixed dungeon layout (not random). We'll use a simple grid
        # but mark special rooms explicitly below.
        self.rooms = {(x,y): Room(x,y) for x in range(width) for y in range(height)}
        # boss room is at bottom-right by convention
        self.rooms[(width-1, height-1)].is_boss_room = True
        self.boss_locked = True
        # place an elite monster in a fixed room (rare elite with key)
        elite_coord = (width-2, height-2)
        elite_room = self.rooms[elite_coord]
        # elite that holds the key (mark via special attribute)
        elite = Creature('Ruins Sentinel (Elite)', 23, 350, 80, 28, 12, special='elite_key', xp_value=1500)
        elite_room.monsters = [elite]
        elite_room.special = 'elite'
        self.merchant_coord = (1, 0)  # fixed merchant room
        self.rooms[self.merchant_coord].merchant = Merchant()
        self.start_pos = (0,0)

    def draw_map(self, players=None):
        """Render a compact ASCII map of the dungeon.

        If `players` is provided, their initials replace or augment the
        room marker so it's easy to see player positions at a glance.
        The map intentionally omits numeric headers to remain compact.
        """
        print('\nDungeon Map:')

        # Build overlay of player initials if players provided
        overlay = {}
        if players:
            for p in players:
                try:
                    if not p.is_alive():
                        continue
                    pos = tuple(p.pos)
                    overlay.setdefault(pos, []).append(p)
                except Exception:
                    continue

        # print rows without numeric headers; show initial(s) or room ascii
        for y in range(self.height):
            row = ''
            for x in range(self.width):
                pos = (x, y)
                base = self.rooms[pos].ascii()
                inner = base[1:-1].strip() if isinstance(base, str) and len(base) >= 2 else ''
                if pos in overlay:
                    initials = '/'.join([pl.name[0].upper() for pl in overlay[pos]])
                    # combine initials with existing room marker if present using initials:marker
                    if inner:
                        cell = f'[{initials}:{inner}]'
                    else:
                        cell = f'[{initials}]'
                else:
                    cell = base
                row += cell
            print(row)

    def move_player(self, player, direction):
        """Move `player` in `direction` and return the `Room` they land in.

        Movement clamps to the dungeon bounds. Directions supported:
        `'forward'` (increase y), `'back'` (decrease y), `'left'`, and
        `'right'` (change x).
        """
        px, py = player.pos
        if direction == 'forward':
            player.pos = (px, min(self.height-1, py+1))
        elif direction == 'left':
            player.pos = (max(0, px-1), py)
        elif direction == 'right':
            player.pos = (min(self.width-1, px+1), py)
        elif direction == 'back':
            player.pos = (px, max(0, py-1))
        return self.current_room_for(player)

    def current_room_for(self, player):
        """Return the `Room` object for `player`'s current position."""
        return self.rooms[player.pos]

    def enter_room_for_player(self, room, player, all_players, distribute_cb, death_cb, input_handler=input, printer=print):
        """Handle a player entering `room`.

        - `player`: the actor who initiated entering the room
        - `all_players`: list of all party members (used to detect adjacent joiners)
        - `distribute_cb`: callback `distribute_cb(enemy, players)` invoked when an enemy dies
        - `death_cb`: callback `death_cb(players)` invoked after combat ends

        `input_handler` and `printer` are injectable I/O handlers used for
        prompts (tests should pass stubs here).
        """
        # Determine which players are present in this room (alive)
        from .utils import alive_entities
        players_here = [p for p in all_players if p.pos == player.pos and p.is_alive()]

        # Helper: find adjacent players (Manhattan distance == 1)
        def adjacent_players(coord, players):
            """Return players who are adjacent (Manhattan distance <=1) to `coord`.

            This includes co-located players (distance 0) and adjacent ones
            (distance 1). The initiating `player` is excluded. This allows
            the game to explicitly ask teammates who are already in the
            room whether they want to (re-)confirm joining the fight.
            """
            ax, ay = coord
            res = []
            for pl in players:
                if not pl.is_alive():
                    continue
                if pl is player:
                    continue
                px, py = pl.pos
                if abs(px - ax) + abs(py - ay) <= 1:
                    res.append(pl)
            return res

        # helper to prompt adjacent players to join and add them to players_here
        def prompt_adjacent_join():
            """Prompt adjacent players (Manhattan distance 1) to join combat.

            When a player accepts, move them into the room and add them to
            `players_here` so they participate in the upcoming encounter.
            """
            adj = adjacent_players((room.x, room.y), all_players)
            for ap in adj:
                # Ask each nearby teammate whether they want to join. If
                # they accept and are not already recorded in `players_here`,
                # move them into the room and add them to the participant list.
                printer(f"{ap.name} is nearby. Join the fight? (y/n)")
                ans = input_handler('> ').strip().lower()
                if ans.startswith('y'):
                    if ap.pos != (room.x, room.y):
                        ap.pos = (room.x, room.y)
                    if ap not in players_here:
                        players_here.append(ap)

        # If the room already has monsters (pre-placed), prompt adjacent players then fight
        if room.monsters:
            prompt_adjacent_join()
            printer('Monsters lurk in this room!')
            combat(players_here, room.monsters, distribute_cb, death_cb, input_handler=input_handler, printer=printer)
            return
        if room.visited:
            if random.randint(0,100) < 50:
                # spawn 1-3 monsters scaled to players here
                group = [generate_enemy_from_players(players_here) for _ in range(random.randint(1,3))]
                room.monsters = group
                printer('Re-encounter! Monsters appear in the room.')
                combat(players_here, room.monsters, distribute_cb, death_cb, input_handler=input_handler, printer=printer)
            else:
                printer('The room is quiet. Nothing new.')
        else:
            room.visited = True
            roll = random.randint(0,100)
            if room.is_boss_room:
                if self.boss_locked:
                    printer('A massive sealed door stands before you. It needs a key.')
                    # check if any player here has the key
                    key_holder = None
                    for p in players_here:
                        for it in p.inventory:
                            if it.kind == 'key':
                                key_holder = (p, it)
                                break
                        if key_holder:
                            break
                    if key_holder:
                        p_with_key, key_item = key_holder
                        printer(f"{p_with_key.name} uses {key_item.name} to unlock the door.")
                        p_with_key.inventory.remove(key_item)
                        self.boss_locked = False
                    else:
                        printer('You cannot enter; find the key first.')
                        return
                boss = Creature('Ancient Dragon', BOSS_LEVEL, 600, 200, 40, 15, xp_value=2000)
                room.monsters = [boss]
                printer('\nYou enter the boss chamber...')
                prompt_adjacent_join()
                combat(players_here, room.monsters, distribute_cb, death_cb, input_handler=input_handler, printer=printer)
                if all(not p.is_alive() for p in players_here):
                    printer('All heroes here have fallen. The dungeon claims them.')
                    return
                # Generate boss loot (two attempts to increase chance of a weapon)
                boss_loot = generate_loot(BOSS_LEVEL) or generate_loot(BOSS_LEVEL)
                distribute_boss_loot(boss, boss_loot, players_here, printer=printer)
                printer('The ancient treasure is yours. You win (for now).')
            elif roll < 45:
                group = [generate_enemy_from_players(players_here) for _ in range(random.randint(1,3))]
                room.monsters = group
                printer('Monsters lurk in this room!')
                prompt_adjacent_join()
                combat(players_here, room.monsters, distribute_cb, death_cb, input_handler=input_handler, printer=printer)
            elif roll < 75:
                chest_loot = generate_chest([p.level for p in players_here])
                room.chest = chest_loot
                printer('You found a chest!')
                # single player interaction if only one here
                self.handle_chest(room, players_here, printer=printer)
            elif roll < 90:
                # Merchant room is fixed during init; just handle visit
                if room.merchant:
                    printer('You find a traveling merchant in the room.')
                    self.handle_merchant(room.merchant, players_here, input_handler=input_handler, printer=printer)
            else:
                printer('The room is empty, but quiet. You find a small cache of gold.')
                for p in players_here:
                    g = random.randint(2,7)
                    p.gold += g
                    printer(f"{p.name} picks up {g} gold.")

    def handle_chest(self, room, players, printer=print):
        """Resolve a chest interaction and award its contents to players.

        Chests may contain a weapon template or an `Item`. Weapons are
        wrapped as `Item` instances and awarded to a random alive
        participant; gold is split evenly among alive players.
        """
        if not room.chest:
            return
        content = room.chest
        # Announce chest contents. Content can be a Weapon or Item.
        printer(f"Chest contains: {content}")
        # Defensive: if the room somehow ended up as the content, bail out
        if isinstance(content, Room):
            return
        if hasattr(content, 'level_req'):
            # weapon template returned -- wrap as Item with weapon effect
            from .items import Item as ItemClass
            from .utils import alive_entities
            winner = random.choice(alive_entities(players))
            winner.inventory.append(ItemClass(content.name, 'weapon', {'weapon': content}))
            printer(f"{winner.name} gets {content}.")
        elif isinstance(content, Item):
            if content.kind == 'gold':
                amt = content.effect.get('amount', 0)
                from .utils import alive_entities
                alive = alive_entities(players)
                per = amt // len(alive)
                for p in alive:
                    p.gold += per
                printer(f"Gold split: each gains {per} gold.")
            else:
                from .utils import alive_entities
                p = random.choice(alive_entities(players))
                p.inventory.append(content)
                printer(f"{p.name} receives {content.name}.")
        room.chest = None

    def handle_merchant(self, merchant, players, input_handler=input, printer=print):
        """Present merchant UI and allow players to buy/sell.

        The merchant interaction loops each alive player in `players` and
        asks for a command. Supported commands are:
        - `buy <index>`: purchase an item from `merchant.inventory`
        - `sell <index>`: sell an item from the player's inventory
        - `skip`: skip interaction

        All state-modifying actions are confirmed with `prompt_confirm`
        and the function uses centralized helpers for price estimation and
        merchant acceptance rules.
        """
        # Show a concise merchant inventory listing (name, kind, price)
        printer(f"Merchant offers: {[(i.name,i.kind,price) for (i,price) in merchant.inventory]}")
        for p in players:
            if not p.is_alive():
                continue
            printer(f"{p.name} has {p.gold} gold.")
            printer('Type buy <index> to purchase, sell <index> to sell your item, or skip')
            cmd = input_handler('> ').strip()
            if cmd.startswith('buy'):
                try:
                    idx = int(cmd.split()[1]) - 1
                    item, price = merchant.inventory[idx]
                    # Confirm purchase before modifying state
                    from .utils import prompt_confirm
                    if not prompt_confirm(f"Confirm purchase {item.name} for {price} gold? (y/n)", input_handler=input_handler, printer=printer, default=False):
                        printer('Purchase cancelled.')
                    else:
                        if p.gold >= price:
                            # check inventory space
                            if p.add_item(item):
                                p.gold -= price
                                printer(f"{p.name} buys {item.name} for {price} gold.")
                            else:
                                printer('Purchase cancelled: inventory full.')
                        else:
                            printer('Not enough gold.')
                except Exception:
                    printer('Invalid purchase.')
            elif cmd.startswith('sell'):
                try:
                    idx = int(cmd.split()[1]) - 1
                    # Peek at the item to be sold so we can confirm with the player
                    try:
                        to_sell = p.inventory[idx]
                    except Exception:
                        printer('Invalid sell index.')
                        continue
                    # Estimate sell price for confirmation (centralized helper)
                    from .items import estimate_sell_price
                    est_price = estimate_sell_price(to_sell)
                    if est_price is None:
                        printer('This item cannot be sold here.')
                        continue
                    from .utils import prompt_confirm
                    if not prompt_confirm(f"Confirm sell {to_sell.name} for {est_price} gold? (y/n)", input_handler=input_handler, printer=printer, default=False):
                        printer('Sale cancelled.')
                        continue
                    # Proceed with actual sell; Player.sell_item will validate bound/special cases
                    result = p.sell_item(idx)
                    if result:
                        price_gained, sold_item = result
                        # compute merchant resell price using centralized helper
                        from .items import estimate_resell_price
                        resell_price = estimate_resell_price(sold_item) or price_gained
                        # merchant accepts the sold_item into inventory
                        # Only accept non-weapon consumables into merchant inventory
                        from .items import Item as ItemClass
                        if isinstance(sold_item, ItemClass):
                            if getattr(sold_item, 'kind', None) != 'weapon':
                                merchant.inventory.append((sold_item, resell_price))
                        else:
                            if getattr(sold_item, 'kind', None) != 'weapon':
                                merchant.inventory.append((ItemClass(sold_item.name, sold_item.kind, getattr(sold_item,'effect',None)), resell_price))
                        printer(f"{p.name} sold {sold_item.name} for {price_gained} gold. Merchant will resell for {resell_price}.")
                    else:
                        printer('Sale failed.')
                except Exception:
                    printer('Invalid sell command.')


class Merchant:
    def __init__(self):
        # Simple merchant inventory: tuples of (Item, price)
        from .items import Item
        # offer a few potions and one rare item
        self.inventory = [
            (Item('Lesser Health Potion', 'potion', {'hp':25}), 30),
            (Item('Greater Health Potion', 'potion', {'hp':50}), 80),
            (Item('Lesser Mana Potion', 'mana', {'mp':25}), 35),
            (Item('Greater Mana Potion', 'mana', {'mp':60}), 90),
            (Item('Revive Token', 'revive', {}), 300),
        ]


def generate_enemy_from_players(players):
    """Generate a monster scaled to the average player level.

    This helper uses a simple heuristic: average player level ± random
    adjustment. Keep scaling conservative to avoid runaway difficulty.
    """
    avg_lvl = max(1, sum(p.level for p in players)//len(players))
    # Allow enemies to be within +/-2 levels of average player level to
    # keep early-game encounters fair but varied (e.g., level-5 players
    # will see enemies level 3..7).
    lvl = max(1, avg_lvl + random.randint(-2,2))
    name = random.choice(['Skeleton','Goblin','Wight','Cave Bat','Giant Rat','Cultist','Dire Wolf'])
    # Basic stat formula; tune these coefficients to change encounter difficulty
    hp = 20 + lvl * 8
    mp = 5 + lvl * 2
    atk = 4 + lvl * 2
    defense = 1 + lvl
    xp = 10 + lvl * 5
    return Creature(f"{name}", lvl, hp, mp, atk, defense, xp_value=xp)


def distribute_boss_loot(boss, weapon, players, printer=print):
    """Award boss loot to a player.

    The logic prefers the player who landed the final blow (`last_hit`),
    otherwise picks a random alive participant. Boss loot also grants a
    large gold bonus.
    """
    last_hit_players = [p for p in players if p.last_hit]
    if last_hit_players:
        winner = last_hit_players[-1]
    else:
        winner = random.choice([p for p in players if p.is_alive()])
    printer(f"{winner.name} claims the boss loot: {weapon}!")
    winner.inventory.append(weapon if hasattr(weapon,'name') else Item(str(weapon),'misc',{}))
    # Fixed gold payout for boss victory; consider making this configurable
    winner.gold += 500

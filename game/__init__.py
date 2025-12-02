# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""`game` package exports and convenience helpers.

This file exposes the main submodules of the package through ``__all__``
so ``from game import ...`` imports are convenient in scripts and tests.
Keep the list small and intentionally focused on the public API of the
package.
"""

# public submodules
__all__ = [
	'utils',
	'items',
	'creature',
	'player',
	'combat',
	'dungeon',
	'save',
	'loot',
]

# Quick Start Guide - Turn-Based Tactical RPG

## Installation & Setup

### 1. Install Dependencies
```bash
pip install arcade
```

### 2. Run the Game
```bash
python main.py
```

## Game Overview

**Single Player** | **Turn-Based Combat** | **Grid-Based Movement**

The game alternates between:
- **Exploration Phase** (3 sec) - Character explores, auto-generates narrative
- **Combat Phase** - Player battles randomly spawned enemies

## How to Play

### Exploration Phase ⚔️
```
EXPLORATION PHASE
Searching for enemies...
Player gains experience from the journey.
[████████░░░░░░░░░░░] 55%

→ Wait 3 seconds for combat to start
```

### Combat Phase 🎮

**Your Character**: Blue circle on grid
**Enemies**: Red circles on grid

#### Step 1: Move
```
Press [M] → Blue tiles highlight reachable positions
Arrow Keys or Click on blue tile → Move
```

#### Step 2: Attack
```
Press [A] → Red tiles highlight attackable positions
Arrow Keys or Click on red tile → Attack target
```

#### Step 3: End Turn
```
Press [E] → Enemies take their turns
```

**Repeat** until:
- ✓ All enemies defeated (Victory!) → Next exploration
- ✗ Your HP reaches 0 (Defeat!) → Restart combat

## Controls Quick Reference

| Action | Key | Mouse |
|--------|-----|-------|
| Select Movement | M | - |
| Select Attack | A | - |
| Move/Attack North | ↑ | Click blue/red tile |
| Move/Attack South | ↓ | Click blue/red tile |
| Move/Attack West | ← | Click blue/red tile |
| Move/Attack East | → | Click blue/red tile |
| End Your Turn | E | - |

## Game Stats

### Starting Character
- **Name**: Hero
- **Level**: 1
- **HP**: 20
- **Attack**: 7
- **Defense**: 5
- **Speed**: 6
- **Weapon**: Sword (Range 1, Damage 8)

### Combat Mechanics

#### Movement
- **Range**: 5 tiles per turn
- **Cost**: 1 action per turn
- **Blocked by**: Obstacles and map boundaries

#### Attack
- **Range**: 1 adjacent tile
- **Hit Chance**: ~90% (modified by speed difference)
- **Crit Chance**: 5% (+ level difference bonus)
- **Crit Damage**: 3× normal damage
- **Minimum Damage**: 1

#### Experience System
- **Gain**: 50 + (enemy_level × 10) per defeated enemy
- **Level Up**: Requires increasing XP amounts
- **Stat Growth**: Random improvement on level up

### Enemy Spawning

| Player Level | Expected Enemies | Difficulty |
|--------------|------------------|-----------|
| 1-3 | 2-4 | Balanced |
| 4-6 | 4-6 | Moderate |
| 7-10 | 6-8 | Challenging |
| 10+ | 8 | Very Hard |

## Strategy Tips

### Movement
- **Plan ahead**: Check red tiles to decide where to move
- **Positioning**: Move to positions that maximize coverage
- **Retreat**: Move away from strong enemies to regain HP
- **Encirclement**: Try to avoid being surrounded

### Combat
- **Focus fire**: Eliminate weak enemies first (lower HP)
- **Range management**: Stay at edges of your attack range
- **Kiting**: Move away while attacking to avoid damage
- **Prediction**: Anticipate enemy movements

### Leveling
- **Early game**: Focus on avoiding damage
- **Mid game**: Build up attack power
- **Late game**: Manage multiple enemies with smart positioning

## Game Progression

```
Level 1-3: Learn mechanics
  └─ 2-4 basic enemies per battle

Level 4-6: Comfortable progression  
  └─ 4-6 enemies per battle

Level 7-10: Strategic depth
  └─ 6-8 enemies per battle

Level 10+: Maximum challenge
  └─ 8 enemies per battle
```

## Customization

### Easy Changes

#### Make Movement Easier
Edit [game.py](game.py#L15):
```python
self.movement_range = 7  # Was 5, increase for easier movement
```

#### Make Combat Harder
Edit [Combat/tactical_combat.py](Combat/tactical_combat.py#L100):
```python
hit_chance = 85  # Was 90, decrease for more misses
```

#### Change Player Starting Stats
Edit [game.py](game.py#L54):
```python
player = PlayerCharacter(
    "Hero",
    level=1,
    hp=30,          # Increase for more health
    hp_max=30,
    attack=10,      # Increase for more damage
    defense=7,      # Increase for more defense
    speed=8,        # Increase for better hit/dodge
    position=(0, 0),
    attacks=[basic_attack]
)
```

## Common Issues & Solutions

### Q: Game won't start
**A**: Check that `maps_imgs/map_living_room_and_kitchen.tmx` exists

### Q: Can't move or attack during combat
**A**: Make sure it's PLAYER TURN (should say "PLAYER TURN" in green at top)

### Q: Red tiles showing but can't attack
**A**: Enemy might be at edge of range. Move closer and try again.

### Q: Game is too easy
**A**: Edit [game.py](game.py) to spawn more enemies:
```python
self.spawner.spawn_rules["max_enemies"] = 12  # More enemies
```

### Q: Game is too hard
**A**: Increase player starting HP or decrease enemy spawn count

## File Structure

```
├── main.py                    ← Run this file
├── game.py                    ← Main game loop
├── Map/
│   └── game_map.py           ← Map system
├── Entities/
│   ├── Character.py          ← Base character
│   ├── Player_character.py    ← Player class
│   ├── Ennemy.py             ← Enemy class
│   └── Attack.py             ← Attack mechanics
├── Combat/
│   ├── tactical_combat.py     ← NEW: Turn-based combat
│   └── combat_manager.py      ← Legacy (unused)
├── system/
│   ├── exploration_phase.py   ← NEW: Exploration phase
│   ├── enemy_spawner.py       ← Enemy creation
│   ├── xp_system.py           ← Experience system
│   └── ai_controller.py       ← Legacy (unused)
├── GAME_MECHANICS.md          ← Full mechanics guide
├── REFACTORING_SUMMARY.md     ← Technical changes
└── API_REFERENCE.md           ← Detailed API docs
---

**Enjoy the game! Have fun with tactical combat!** 🎮

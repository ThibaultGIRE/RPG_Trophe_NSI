# Tactical RPG - Turn-Based Combat System

## Overview

This is a turn-based tactical RPG where a single player character progresses through exploration and combat phases. The game features grid-based tactical combat inspired by Fire Emblem, with strategic movement and attack positioning.

## Game Phases

### Exploration Phase
- **Duration**: 3 seconds per phase
- **Display**: Text-based narrative showing the character's movement and story progression
- **Mechanics**: 
  - Character automatically moves to a random location
  - Player gains experience from exploration
  - Narrative messages describe the journey
  - Automatically transitions to combat after timer completes

### Combat Phase
- **Grid-based Tactical Map**: Square tile map with grid coordinates
- **Turn-based System**: 
  - Player turn: Move and attack
  - Enemy turns: Enemies take actions sequentially
  - Speed stat determines turn order (not used in this simplified version)

## Game Mechanics

### Player Character
- **Single playable character** named "Hero"
- **Starting Stats**:
  - Level: 1
  - HP: 20
  - Attack: 7
  - Defense: 5
  - Speed: 6
- **Basic Attack**: Sword with range 1, base damage 8

### Movement System
- **Movement Range**: 5 tiles per turn (shown by blue tiles)
- **Blue Tiles**: Display all walkable positions within movement range
- **Attack Range**: 1 tile (adjacent tiles only)
- **Red Tiles**: Display all attackable positions
- **Obstacles**: Impassable terrain blocks movement

### Combat Actions

#### Player Turn Actions
1. **Move (Press M)**
   - Select movement action to highlight all reachable tiles (blue)
   - Click or use arrow keys to move
   - Can only move once per turn
   
2. **Attack (Press A)**
   - Select attack action to highlight all attackable tiles (red)
   - Click or use arrow keys to select target
   - Can only attack once per turn

3. **End Turn (Press E)**
   - Finish player actions and start enemy turns

#### Enemy AI
- **Simple AI**: Enemies move towards the player if not in range
- **Attack**: Enemies attack if the player is within range
- **Order**: Enemies take turns sequentially after player's turn

### Combat Resolution

#### Hit Calculation
- Base hit chance: 90%
- Modified by: `90 - 2 × (defender.speed - attacker.speed)`
- Range: 10% to 95% hit chance

#### Damage Calculation
- Base damage = attack weapon damage + attacker.attack - defender.defense
- Minimum damage: 1

#### Critical Hits
- Base crit chance: 5%
- Modified by: `5 + (attacker.level - defender.level)`
- Range: 0% to 40% crit chance
- Critical hit multiplier: 3x damage

### Enemy Spawning

#### Level-Based Spawning
- **Number of Enemies**:
  - Base: 2-4 enemies
  - Player level > 5: +2 enemies
  - Player level > 10: +2 additional enemies
  - Maximum: 8 enemies

- **Enemy Levels**:
  - Base enemy level = player level
  - Variance: ±3 levels
  - Minimum level: 1

- **Enemy Stats Scaling**:
  - HP: Base HP + (level - 1) × 2
  - Attack: Base attack + (level - 1)
  - Defense: Base defense + (level - 1) ÷ 2
  - Speed: Base speed (unchanged)

#### Enemy Types
1. **Base Enemy** (default)
   - HP: 15, Attack: 7, Defense: 3, Speed: 3
   
2. **Boss** (stronger variant)
   - HP: 50, Attack: 15, Defense: 10, Speed: 10

### Experience & Leveling

#### XP Rewards
- Base reward per enemy: 50 XP
- Enemy level bonus: 10 XP per level
- Total XP = (50 + level × 10) × number of defeated enemies

#### Level Up
- Requires: `150 × (level)²` XP
- **Stat Growth Rates**:
  - HP: 60% chance +1
  - Attack: 45% chance +1
  - Defense: 40% chance +1
  - Speed: 50% chance +1

## Controls

### Exploration Phase
- Automatic - no player input needed
- Timer counts down from 3 seconds

### Combat Phase

| Key | Action |
|-----|--------|
| **M** | Select Movement action |
| **A** | Select Attack action |
| **↑** | Move up / Target above |
| **↓** | Move down / Target below |
| **←** | Move left / Target left |
| **→** | Move right / Target right |
| **E** | End player turn |
| **Mouse Click** | Move to tile or attack target (when tile is highlighted) |

## Game Flow

```
1. Start Game
   ↓
2. Exploration Phase (3 seconds)
   - Character moves to random location
   - Display narrative text
   ↓
3. Combat Phase
   - Spawn enemies based on player level
   - Display tactical map
   - Player takes turn:
     * Move (optional)
     * Attack (optional)
     * End turn
   - Enemies take turns:
     * Move towards player
     * Attack if in range
   - Check win/lose conditions
   ↓
4. Victory → Gain XP → Return to Step 2
   or
   Defeat → Reset player HP → Return to Step 2
```

## Display

### Exploration Phase UI
- **Title**: "EXPLORATION PHASE"
- **Action Log**: Narrative messages about character movement
- **Progress Bar**: Visual timer (0-100%)

### Combat Phase UI
- **Turn Indicator**: "PLAYER TURN" or "ENEMY TURN" (color coded)
- **Player Stats**: HP, Level
- **Control Legend**: Key bindings and descriptions
- **Highlighted Tiles**: Blue (movement) or Red (attack range)
- **Enemy Info**: List of alive enemies with HP
- **Minimap**: Grid showing all positions

## Technical Architecture

### Core Files

1. **game.py** - Main game window and state manager
   - Handles phase transitions
   - Manages drawing and input
   - Coordinates all systems

2. **Combat/tactical_combat.py** - Tactical combat system
   - Movement range calculations (BFS algorithm)
   - Attack range calculations
   - Combat resolution and hit/crit calculations
   - Turn management

3. **system/exploration_phase.py** - Exploration phase manager
   - Narrative generation
   - Timer management
   - Character positioning

4. **system/enemy_spawner.py** - Enemy spawning system
   - Level-based enemy count calculation
   - Enemy stat scaling
   - Random placement on map

5. **Map/game_map.py** - Game map system
   - Grid-based pathfinding
   - Obstacle detection
   - Coordinate conversions (grid ↔ pixel)

6. **Entities/** - Character system
   - **Character.py**: Base character class with stats and abilities
   - **Player_character.py**: Player-specific features
   - **Ennemy.py**: Enemy-specific features
   - **Attack.py**: Attack definition with damage calculation

### Game Systems

- **XpSystem**: Handles experience and leveling
- **AIController**: Enemy decision making (simplified in tactical combat)
- **CombatManager**: Legacy system (replaced by TacticalCombat)

## Dependencies

- **Python 3.7+**
- **arcade** - Graphics and game loop
- **random** - Enemy spawning and level generation

## How to Run

```bash
python main.py
```

Requires:
- Valid TMX map file: `maps_imgs/map_living_room_and_kitchen.tmx`
- Proper tile asset files in `maps_imgs/tiles/`

## Customization

### Adjust Movement Range
Edit `TacticalCombat.__init__()` in [Combat/tactical_combat.py](Combat/tactical_combat.py#L15):
```python
self.movement_range = 5  # Change this value
```

### Adjust Attack Range
Edit the `_get_attack_tiles()` method in [Combat/tactical_combat.py](Combat/tactical_combat.py#L61):
```python
self.attack_range = 1  # Change this value
```

### Adjust Enemy Spawn Count
Edit `_calculate_enemy_count()` in [system/enemy_spawner.py](system/enemy_spawner.py#L40):
```python
base_count = randint(2, 4)  # Adjust min/max
```

### Adjust Player Starting Stats
Edit `create_player()` in [game.py](game.py#L54):
```python
player = PlayerCharacter(
    "Hero",
    level=1,
    hp=20,  # Change HP
    # ... modify other stats
)
```

## Future Enhancements

1. **Multiple attack types** with different ranges
2. **Special abilities** with cooldowns
3. **Items and equipment** system
4. **Multiple enemy types** with unique behaviors
5. **Boss battles** with special mechanics
6. **Save/load system**
7. **Difficulty levels**
8. **Procedural map generation**
9. **Pathfinding visualization** for enemies
10. **Sound and music** system

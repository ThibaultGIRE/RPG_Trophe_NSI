# API Reference - New Game Systems

## Combat/tactical_combat.py

### Class: TacticalCombat

Main system for managing turn-based tactical combat with grid-based movement and positioning.

#### Constructor
```python
TacticalCombat(player, enemies, game_map)
```
- **player**: PlayerCharacter object for the player
- **enemies**: List of Enemy objects
- **game_map**: GameMap instance for pathfinding and terrain

#### Attributes
```python
.current_turn          # "player" or "enemy" - whose turn it is
.player_has_moved      # bool - if player moved this turn
.player_has_attacked   # bool - if player attacked this turn
.movement_range        # int - tiles player can move per turn (default: 5)
.attack_range          # int - tiles player can attack (default: 1)
.enemy_turn_index      # int - current enemy index in turn order
```

#### Methods

##### `get_movement_tiles() -> set`
Calculate all reachable tiles from current player position.

**Returns**: Set of (x, y) coordinates within movement range

**Complexity**: O(n) where n = number of walkable tiles

**Example**:
```python
reachable = combat.get_movement_tiles()
# Returns: {(5,5), (5,6), (5,7), (4,6), (3,6), ...}
```

---

##### `get_attack_tiles(from_position=None) -> set`
Calculate all attackable tiles from given position (or player if not specified).

**Parameters**:
- `from_position` (tuple): (x, y) to calculate from. Default: player position

**Returns**: Set of (x, y) coordinates within attack range

**Example**:
```python
# Get current player attack range
targets = combat.get_attack_tiles()

# Get potential targets after moving to (6, 7)
future_targets = combat.get_attack_tiles((6, 7))
```

---

##### `player_move(new_x: int, new_y: int) -> bool`
Attempt to move the player to a new position.

**Parameters**:
- `new_x` (int): Target x coordinate
- `new_y` (int): Target y coordinate

**Returns**: 
- `True` if move successful (and marks `player_has_moved = True`)
- `False` if move invalid or already moved this turn

**Raises**: No exceptions, returns bool for success

**Example**:
```python
if combat.player_move(6, 7):
    print("Player moved successfully")
else:
    print("Invalid move or already moved this turn")
```

---

##### `player_attack(target_x: int, target_y: int) -> dict`
Execute a player attack on target position.

**Parameters**:
- `target_x` (int): Target x coordinate
- `target_y` (int): Target y coordinate

**Returns**: Dictionary with keys:
```python
{
    "success": bool,              # True if attack executed
    "reason": str,                # "Already attacked", "Out of range", etc
    "target": str,                # Enemy name (if successful)
    "damage": int,                # Damage dealt (if successful)
    "target_hp": int              # Target remaining HP (if successful)
}
```

**Example**:
```python
result = combat.player_attack(5, 6)
if result["success"]:
    print(f"Hit {result['target']} for {result['damage']} damage!")
    print(f"Enemy HP: {result['target_hp']}")
else:
    print(f"Attack failed: {result['reason']}")
```

---

##### `end_player_turn() -> None`
End the player's turn and start enemy turns.

**Side Effects**:
- Sets `current_turn = "enemy"`
- Resets `enemy_turn_index = 0`

**Example**:
```python
combat.end_player_turn()
# Now enemies will take their turns
```

---

##### `process_enemy_turn() -> dict`
Process one enemy's action and move to next enemy.

**Returns**: Dictionary describing action taken:
```python
{
    "type": "attack|move|no_action|turn_end",
    "enemy": str,           # Enemy name (if not turn_end)
    "damage": int,          # Damage dealt (if attack)
    "target": str,          # Target name (if attack)
    "player_hp": int,       # Player HP after attack (if attack)
    "to": tuple             # New position (if move)
}
```

**Note**: Call repeatedly until `current_turn` becomes "player"

**Example**:
```python
while combat.current_turn == "enemy":
    action = combat.process_enemy_turn()
    if action["type"] == "attack":
        print(f"{action['enemy']} attacked player for {action['damage']} damage!")
```

---

##### `check_combat_end() -> str`
Check if combat has ended.

**Returns**: 
- `"victory"` - All enemies defeated
- `"defeat"` - Player HP <= 0
- `"ongoing"` - Combat continues

**Example**:
```python
result = combat.check_combat_end()
if result == "victory":
    award_xp()
elif result == "defeat":
    game_over()
```

---

## system/exploration_phase.py

### Class: ExplorationPhase

Manages the exploration phase between combats with automatic movement and narrative.

#### Constructor
```python
ExplorationPhase(game_map, player)
```
- **game_map**: GameMap instance
- **player**: PlayerCharacter object

#### Attributes
```python
.timer                 # float - elapsed time in seconds
.exploration_complete  # bool - whether phase is complete
.action_log           # list - narrative messages
```

#### Methods

##### `start_exploration() -> None`
Begin a new exploration sequence.

**Side Effects**:
- Resets timer to 0
- Generates new narrative messages
- Updates action_log

**Example**:
```python
exploration = ExplorationPhase(game_map, player)
exploration.start_exploration()
```

---

##### `get_action_log() -> list`
Retrieve the current exploration narrative messages.

**Returns**: List of string messages

**Example**:
```python
messages = exploration.get_action_log()
for message in messages:
    print(message)
# Output:
# Exploring the area...
# Searching for enemies...
```

---

##### `update(delta_time: float) -> bool`
Update exploration timer.

**Parameters**:
- `delta_time` (float): Seconds elapsed since last frame

**Returns**:
- `True` if exploration complete (3 seconds elapsed)
- `False` otherwise

**Example**:
```python
# In game loop
if exploration.update(delta_time):
    print("Exploration complete, starting combat!")
```

---

##### `random_character_position() -> tuple`
Get a random valid position on the map.

**Returns**: Tuple (x, y) of random walkable position

**Example**:
```python
x, y = exploration.random_character_position()
game_map.move_character(player, x, y)
```

---

## system/enemy_spawner.py

### Class: Ennemy_Spawner

Spawns enemies with level-based scaling and variety.

#### Constructor
```python
Ennemy_Spawner(game_map)
```
- **game_map**: GameMap instance

#### Attributes
```python
.spawn_rules = {
    "min_enemies": 1,
    "max_enemies": 8,
    "level_variance": 3
}
```

#### Methods

##### `spawn_wave(player_level: int) -> list`
Spawn a complete wave of enemies.

**Parameters**:
- `player_level` (int): Current player level

**Returns**: List of Enemy objects

**Spawning Logic**:
- Base enemies: 2-4
- Player level > 5: +2 enemies
- Player level > 10: +2 additional enemies
- Maximum: 8 enemies

**Enemy Level**:
- Base: player_level ± 3

**Example**:
```python
enemies = spawner.spawn_wave(player.level)
print(f"Spawned {len(enemies)} enemies")
```

---

##### `_calculate_enemy_count(player_level: int) -> int`
Determine number of enemies to spawn.

**Parameters**:
- `player_level` (int): Current player level

**Returns**: Number of enemies to spawn

**Algorithm**:
```
base_count = random(2, 4)
if player_level > 5:
    base_count += 2
if player_level > 10:
    base_count += 2
return min(base_count, max_enemies)
```

---

##### `spawn_enemies(enemy_type: dict, level: int) -> Enemy`
Spawn a single enemy with stat scaling.

**Parameters**:
- `enemy_type` (dict): Type info with keys: "type", "name", "attacks"
- `level` (int): Enemy level

**Stat Scaling**:
```python
hp = base_hp + (level - 1) * 2
attack = base_attack + (level - 1)
defense = base_defense + (level - 1) // 2
speed = base_speed  # Unchanged
```

**XP Reward**: 50 + (level × 10)

**Returns**: Fully initialized Enemy object

**Side Effects**:
- Places enemy on map at random valid position

**Example**:
```python
enemy_type = {
    "type": "base enemy",
    "name": "Goblin",
    "attacks": [basic_attack]
}
enemy = spawner.spawn_enemies(enemy_type, level=5)
```

---

## Integration Example

```python
from game import Game
import arcade

def main():
    # Initialize game
    game = Game("maps_imgs/map_living_room_and_kitchen.tmx")
    
    # Game automatically manages phases
    # - Exploration: 3 seconds with narrative
    # - Combat: Player vs enemies
    # - Victory: XP gain, loop back to exploration
    # - Defeat: Reset HP, loop back to exploration
    
    arcade.run()

if __name__ == "__main__":
    main()
```

---

## Data Flow Diagram

```
EXPLORATION PHASE
├─ ExplorationPhase.update()
│  ├─ Timer increases
│  └─ Return True when 3 seconds elapsed
├─ Call random_character_position()
└─ Place player on map

COMBAT PHASE
├─ Ennemy_Spawner.spawn_wave()
│  └─ Returns list of Enemy objects
├─ TacticalCombat.__init__()
│  └─ Initialize combat system
├─ Player Turn
│  ├─ get_movement_tiles() → Blue highlight
│  ├─ player_move() → Execute move
│  ├─ get_attack_tiles() → Red highlight
│  ├─ player_attack() → Execute attack
│  └─ end_player_turn()
├─ Enemy Turns
│  └─ process_enemy_turn() → Loop until complete
└─ check_combat_end() → Victory/Defeat/Ongoing
```

---

## Performance Considerations

### Movement Range Calculation
- **Algorithm**: Breadth-First Search (BFS)
- **Time Complexity**: O(m × n) where m, n = map dimensions
- **Space Complexity**: O(m × n) for visited set
- **Typical**: ~20-50ms for 50×50 map

### Enemy Spawning
- **Time Complexity**: O(k) where k = number of enemies
- **Placement Retries**: Max 20 attempts per enemy
- **Typical**: ~10ms for 4-8 enemies

### Combat Turn Processing
- **Time Complexity**: O(k) where k = number of enemies
- **Hit/Crit Calculation**: O(1) per attack
- **Typical**: ~5ms per turn

---

## Error Handling

All methods use defensive programming:
- No exceptions thrown from game logic
- Boolean returns indicate success/failure
- Dictionary returns contain status information
- Invalid moves simply fail (return False, not throw)

This allows for flexible error handling in the game loop without exception handling overhead.


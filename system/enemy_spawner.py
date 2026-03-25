import arcade
from Entities.Character import stat_de_base
from Entities.Ennemy import Enemy
from Entities.Attack import Attack
from random import randint, choice

class Ennemy_Spawner:
    def __init__(self, game_map):
        self.map = game_map
        self.spawn_rules = {
            "min_enemies": 1,
            "max_enemies": 8,
            "level_variance": 3,
            "obstacle_influence": 0.7  # 70% chance to spawn near obstacles
        }
        
    def initialize_spawn_system(self):
        """Initialize the spawn system by loading map data.
        
        This is the first step: load and analyze the background and obstacles.
        """
        # Step 1: Background is already loaded in GameMap.draw()
        # This method just confirms the map is ready for spawning
        if not hasattr(self.map, 'obstacles'):
            raise ValueError("Map must have obstacles loaded before spawning")
        
        # Step 2: Analyze obstacles to determine spawn zones
        self._analyze_obstacles()
        
        return True
    
    def _analyze_obstacles(self):
        """Analyze obstacle positions to create spawn zones.
        
        This is the second step: analyze obstacles to determine where mobs can spawn.
        """
        self.spawn_zones = {
            "near_obstacles": set(),  # Tiles adjacent to obstacles
            "away_from_obstacles": set(),  # Tiles not near obstacles
            "corners": set()  # Corner tiles of the map
        }
        
        # Find all walkable tiles
        for x in range(self.map.width):
            for y in range(self.map.height):
                if self.map.is_walkable(x, y) and not self.map.is_occupied(x, y):
                    # Check if tile is adjacent to an obstacle
                    is_near_obstacle = False
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            if (x + dx, y + dy) in self.map.obstacles:
                                is_near_obstacle = True
                                break
                        if is_near_obstacle:
                            break
                    
                    if is_near_obstacle:
                        self.spawn_zones["near_obstacles"].add((x, y))
                    else:
                        self.spawn_zones["away_from_obstacles"].add((x, y))
                    
                    # Check if it's a corner tile
                    if (x <= 1 or x >= self.map.width - 2) and (y <= 1 or y >= self.map.height - 2):
                        self.spawn_zones["corners"].add((x, y))
        
        # Ensure we have valid spawn positions
        if not self.spawn_zones["near_obstacles"]:
            self.spawn_zones["near_obstacles"] = self.spawn_zones["away_from_obstacles"].copy()
        if not self.spawn_zones["away_from_obstacles"]:
            self.spawn_zones["away_from_obstacles"] = self.spawn_zones["near_obstacles"].copy()
    
    def spawn_wave(self, player_level):
        """Spawn a wave with enemies based on player level and obstacle positions.
        
        This is the third step: spawn mobs based on the obstacle analysis.
        Enemies spawn strategically around obstacles for tactical positioning.

        Args:
            player_level (int): player's level

        Returns:
            list: list of enemies spawned
        """
        # Ensure spawn system is initialized
        if not hasattr(self, 'spawn_zones'):
            self.initialize_spawn_system()
        
        # Determine number of enemies based on level difference
        num_enemies = self._calculate_enemy_count(player_level)
        enemies = []

        boss_limit = min(2, max(0, (num_enemies - 1) // 2))
        boss_count = 0

        # Reserve some spawn positions based on obstacle strategy
        spawn_positions = self._get_strategic_spawn_positions(num_enemies)

        for i in range(num_enemies):
            enemy_level = player_level + randint(-self.spawn_rules["level_variance"], self.spawn_rules["level_variance"])
            enemy_level = max(1, enemy_level)

            is_boss_roll = randint(1, 100) <= 20
            if is_boss_roll and boss_count < boss_limit:
                enemy_type_key = "boss"
            else:
                enemy_type_key = "base enemy"

            enemy_type = {"type": enemy_type_key, "name": enemy_type_key, "attacks": []}
            
            # Get strategic spawn position
            spawn_pos = spawn_positions[i] if i < len(spawn_positions) else None
            
            enemy = self.spawn_enemy(enemy_type, enemy_level, spawn_pos)
            if enemy:
                if enemy_type_key == "boss":
                    boss_count += 1
                enemies.append(enemy)

        return enemies
    
    def _get_strategic_spawn_positions(self, num_enemies):
        """Get strategic spawn positions based on obstacles.
        
        Args:
            num_enemies: Number of enemies to spawn
            
        Returns:
            list: List of (x, y) tuples for spawn positions
        """
        positions = []
        near_obstacles = list(self.spawn_zones["near_obstacles"])
        away_from_obstacles = list(self.spawn_zones["away_from_obstacles"])
        corners = list(self.spawn_zones["corners"])
        
        for i in range(num_enemies):
            # Determine spawn strategy based on enemy index
            if i == 0 and len(corners) > 0:
                # First enemy: spawn in a corner for ambush
                pos = choice(corners)
            elif randint(1, 100) <= self.spawn_rules["obstacle_influence"] * 100:
                # High chance to spawn near obstacles (cover positions)
                if near_obstacles:
                    pos = choice(near_obstacles)
                else:
                    pos = choice(away_from_obstacles) if away_from_obstacles else None
            else:
                # Spawn in open areas
                if away_from_obstacles:
                    pos = choice(away_from_obstacles)
                else:
                    pos = choice(near_obstacles) if near_obstacles else None
            
            if pos:
                positions.append(pos)
                # Remove used position to avoid overlapping
                if pos in near_obstacles:
                    near_obstacles.remove(pos)
                if pos in away_from_obstacles:
                    away_from_obstacles.remove(pos)
                if pos in corners:
                    corners.remove(pos)
        
        return positions
    
    def _calculate_enemy_count(self, player_level):
        """Calculate number of enemies based on level.
        
        Args:
            player_level: The player's level
            
        Returns:
            int: Number of enemies to spawn
        """
        # Few enemies if level is normal, more if level is high
        base_count = randint(2, 4)
        
        # Add more enemies for high-level players
        if player_level > 5:
            base_count += 2
        if player_level > 10:
            base_count += 2
        
        return min(base_count, self.spawn_rules["max_enemies"])
    
    def spawn_enemy(self, enemy_type, level, preferred_position=None):
        """Spawn a single enemy at a strategic position.
        
        Args:
            enemy_type: Dictionary with enemy type info
            level: Enemy level
            preferred_position: Preferred (x, y) tuple for spawn position
            
        Returns:
            Enemy: The spawned enemy
        """
        base_stat_enemy = stat_de_base[enemy_type["type"]]
        
        # Scale stats based on level
        hp = base_stat_enemy["hp"] + (level - 1) * 2
        hp_max = hp
        attack = base_stat_enemy["attack"] + (level - 1)
        defense = base_stat_enemy["defense"] + (level - 1) // 2
        speed = base_stat_enemy["speed"]
        
        # Create basic attack
        basic_attack = Attack("Claw", 80, 1, None, 5 + level)
        
        is_boss = enemy_type["type"] == "boss"
        move_range = 3 if is_boss else 4
        enemy_color = arcade.color.PURPLE if is_boss else arcade.color.RED

        enemy = Enemy(
            f"{enemy_type['name']}_{level}",
            level,
            hp,
            hp_max,
            attack,
            defense,
            speed,
            (0, 0),
            [basic_attack],
            is_boss=is_boss,
            move_range=move_range
        )
        enemy.color = enemy_color
        
        # Assign XP reward based on level
        enemy.xp_reward = 50 + (level * 10)

        # Try to place enemy at preferred position (based on obstacles)
        if preferred_position:
            x, y = preferred_position
            if self.map.is_walkable(x, y) and not self.map.is_occupied(x, y):
                placed = self.map.place_character(enemy, x, y)
                if placed:
                    return enemy

        # Fallback: try random positions
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            x = randint(0, self.map.width - 1)
            y = randint(0, self.map.height - 1)
            if (x, y) not in self.map.obstacles and self.map.is_walkable(x, y) and not self.map.is_occupied(x, y):
                placed = self.map.place_character(enemy, x, y)
            attempts += 1

        if not placed:
            return None

        return enemy
    
    def spawn_enemies(self, enemy_type, level):
        """DEPRECATED: Use spawn_enemy instead.
        
        This method is kept for backward compatibility.
        
        Args:
            enemy_type: Dictionary with enemy type info
            level: Enemy level
            
        Returns:
            Enemy: The spawned enemy
        """
        return self.spawn_enemy(enemy_type, level)
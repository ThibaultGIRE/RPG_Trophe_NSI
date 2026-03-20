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
            "level_variance": 3
        }
        
    def spawn_wave(self, player_level):
        """Spawn a wave with enemies based on player level.
        
        Enemies spawn in greater numbers if there's a large level difference.

        Args:
            player_level (int): player's level

        Returns:
            list: list of enemies spawned
        """
        # Determine number of enemies based on level difference
        num_enemies = self._calculate_enemy_count(player_level)
        enemies = []

        for _ in range(num_enemies):
            enemy_level = player_level + randint(-self.spawn_rules["level_variance"], self.spawn_rules["level_variance"])
            enemy_level = max(1, enemy_level)  # Ensure minimum level 1
            
            # pick a base enemy type from the stat table
            enemy_type_key = choice([k for k in stat_de_base.keys() if k != "player character"])
            enemy_type = {"type": enemy_type_key, "name": enemy_type_key, "attacks": []}
            enemy = self.spawn_enemies(enemy_type, enemy_level)
            if enemy:
                enemies.append(enemy)

        return enemies
    
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
    
    def spawn_enemies(self, enemy_type, level):
        """Spawn a single enemy.
        
        Args:
            enemy_type: Dictionary with enemy type info
            level: Enemy level
            
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
        
        enemy = Enemy(
            f"{enemy_type['name']}_{level}",
            level,
            hp,
            hp_max,
            attack,
            defense,
            speed,
            (0, 0),
            [basic_attack]
        )
        
        # Assign XP reward based on level
        enemy.xp_reward = 50 + (level * 10)

        # Try to place enemy on map
        placed = False
        attempts = 0
        while not placed and attempts < 20:
            x = randint(0, self.map.width - 1)
            y = randint(0, self.map.height - 1)
            if self.map.is_walkable(x, y) and not self.map.is_occupied(x, y):
                placed = self.map.place_character(enemy, x, y)
            attempts += 1

        if not placed:
            return None

        return enemy
    
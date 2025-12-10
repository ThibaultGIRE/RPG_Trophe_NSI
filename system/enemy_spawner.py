from Entities.Character import stat_de_base
from Entities.Ennemy import Enemy

class Ennemy_Spawner:
    def __init__(self, game_map):
        self.map = game_map
        self.spawn_rules = {
            "min_enemies": 2,
            "max_enemies": 8,
            "level_variance": 3
        }
        
    def spawn_wave(self, player_level):
        """Spawn a wave with a bunch of enemies

        Args:
            player_level (int): player's level

        Returns:
            list: list of enemies spawned
        """
        from random import randint

        num_enemies = randint(self.spawn_rules["min_enemies"], self.spawn_rules["max_enemies"])
        enemies = []

        for _ in range(num_enemies):
            enemy_level = player_level + randint(-self.spawn_rules["level_variance"], self.spawn_rules["level_variance"])
            enemy = self.spawn_enemy(type, enemy_level)
            enemies.append(enemy)

        return enemies
    
    def spawn_enemies(self, enemy_type, level):
        from random import randint
        
        base_stat_enemy = stat_de_base[enemy_type["type"]]
        enemy = Enemy(enemy_type["name"], base_stat_enemy["level"], base_stat_enemy["hp"], base_stat_enemy["hp_max"], base_stat_enemy["attack"], base_stat_enemy["defense"], base_stat_enemy["speed"], (0,0), enemy_type["attaques"])

        while True:
            x = randint(0, self.map.width - 1)
            y = randint(0, self.map.height - 1)
            if self.map.place_character(enemy, (x, y)):
                break

        return enemy
    
from Entities.Character import stat_de_base
from Entities.Ennemy import Enemy
from random import randint, choice

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
            # pick a base enemy type from the stat table
            enemy_type_key = choice(list(stat_de_base.keys()))
            enemy_type = {"type": enemy_type_key, "name": enemy_type_key, "attaques": []}
            enemy = self.spawn_enemies(enemy_type, enemy_level)
            enemies.append(enemy)

        return enemies
    
    def spawn_enemies(self, enemy_type, level):
        base_stat_enemy = stat_de_base[enemy_type["type"]]
        # use provided level for the spawned enemy
        enemy = Enemy(enemy_type["name"], level, base_stat_enemy["hp"], base_stat_enemy["hp_max"], base_stat_enemy["attack"], base_stat_enemy["defense"], base_stat_enemy["speed"], (0,0), enemy_type["attaques"])

        while True:
            x = randint(0, self.map.width - 1)
            y = randint(0, self.map.height - 1)
            # place_character expects x, y separate
            if self.map.place_character(enemy, x, y):
                break

        return enemy
    
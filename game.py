import arcade
from Map.game_map import GameMap
from system import *
from Entities.Player_character import PlayerCharacter
from Combat.combat_manager import CombatManager

class Game(arcade.Window):
    def __init__(self, tmx_file_path):
        temp_map = arcade.load_tilemap(tmx_file_path, scaling=1.0)
        screen_width = temp_map.width * temp_map.tile_width
        screen_height = temp_map.height * temp_map.tile_height
        super().__init__(screen_width, screen_height, "The Game")

        self.map = GameMap(tmx_file_path)

        self.players = self.create_player_team()
        self.ennemies = []

        self.combat_manager = None
        self.xp_system = XPSystem()
        self.spawner = EnemySpawner(self.map)
        self.ai = AIControler()

        self.running = True
        self.in_combat = False

        self.player_sprites = arcade.SpriteList()
        self.enemy_sprites = arcade.SpriteList()

        self.camera = arcade.Camera(screen_width, screen_height)

        arcade.set_background_color(arcade.color.BLACK)


    def create_player_team(self):

        players = [
            PlayerCharacter("Julie", 1, 12, 5, 6, 5, (0,0), []),
            PlayerCharacter("Valentin", 1, 15, 5, 7, 5, (0,0), []),
            PlayerCharacter("Nathan", 1, 15, 4, 7, 5, (0,0), [] ),
            PlayerCharacter("Thibault", 1, 15, 5, 6, 5, (0,0), [])
        ]

        for i, player in enumerate(players):
            self.map.place_character(player, 2 + i, 2)
        
        return players 
    
    def on_draw(self):
        self.clear()

        self.camera.use()

        self.map.scene.draw()

        self.player_sprites.draw()

        self.enemy_sprites.draw()

        self._draw_ui()

    def _draw_ui(self):
        for sprite in self.player_sprites:
            character = sprite.character

            bar_width = self.map.tile_width - 4
            bar_height = 4
            hp_ratio = character.hp / character.hp_max

            bar_x = sprite.center_x - bar_width // 2
            bar_y = sprite.center_y + self.map.tile_height // 2 + 2  

            arcade.draw_rect_filled(
                sprite.center_x, bar_y + bar_height //2,
                bar_width, bar_height,
                arcade.color.RED
            )

            arcade.draw_rect_filled(
                sprite.center_x + (bar_width * hp_ratio) // 2, bar_y + bar_height // 2,
                bar_width * hp_ratio, bar_height, 
                arcade.color.GREEN
            )
         
    def on_uptade(self, delta_time):
        if not self.in_combat and self.detect_enemy_proximity():
            self.start_combat()

        if self.in_combat:
            self.combat_turn()

        self._uptade_sprite_positions()

    def _uptade_sprite_positions(self):
        for sprite in self.player_sprites:
            pixel_x, pixel_y = self.map.grid_to_pixel(*sprite.character.position)
            sprite.center_x = pixel_x
            sprite.center_y = pixel_y

        for sprite in self.enemy_sprites:
            pixel_x, pixel_y = self.map.grid_to_pixel(*sprite.character.position)
            sprite.center_x = pixel_x
            sprite.center_y = pixel_y

    def on_key_press(self, key, modifiers):
        if not self.in_combat:
            player = self.player[0]
            x, y = player.position

            if key == arcade.key.UP:
                self.map.move_character(player, x, y + 1)
            elif key == arcade.key.DOWN:
                self.map.move_character(player, x, y - 1)
            elif key == arcade.key.LEFT:
                self.map.move_character(player, x - 1, y)
            elif key == arcade.key.RIGHT:
                self.map.move_character(player, x + 1, y)

    def detect_enemy_proximity(self):
        for player in self.players:
            for enemy in self.enemies:
                if self.map.in_attack_range(player, enemy):
                    return True
        return False
    
    def start_combat(self):
        self.in_combat = True
        self.combat_manager = CombatManager(self.players, self.ennemies)
        self.combat_ùanager.start_turn()

    def combat_turn(self):
        result = self.combat_manager.check_end_conditions()

        if result == "victory":
            self.end_combat(victory=True)
        elif result == "defeat":
            self.end_combat(victory=False)

    def end_combat(self, victory):
        if victory:
            total_xp = sum(enemy.xp_reward for enemy in self.enemies if not enemy.is_alive())
            xp_per_player = total_xp // len(self.players)

            for player in self.players:
                if player.is_alive():
                    self.xp_system.gain_xp(player, xp_per_player)

            avg_level = sum(player.level for player in self.players) // len(self.players)
            self.enemies = self.spawner.spawn_wave(avg_level)
            
        self.in_combat = False
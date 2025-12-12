import arcade
from Map.game_map import GameMap
from system import *
from Entities.Player_character import PlayerCharacter

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

        
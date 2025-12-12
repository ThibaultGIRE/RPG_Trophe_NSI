import arcade
from Map.game_map import GameMap
from system import *

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
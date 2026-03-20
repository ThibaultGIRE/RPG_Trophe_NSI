import arcade
import json
import os
import warnings
from arcade.exceptions import PerformanceWarning
from Map.game_map import GameMap
from system.enemy_spawner import Ennemy_Spawner
from system.xp_system import XpSystem
from system.exploration_phase import ExplorationPhase
from Entities.Player_character import PlayerCharacter
from Entities.Ennemy import Enemy
from Entities.Attack import Attack
from Combat.tactical_combat import TacticalCombat

warnings.filterwarnings("ignore", category=PerformanceWarning)

class Game(arcade.Window):
    def __init__(self):
        self.map = GameMap(width=14, height=10, tile_width=64, tile_height=64, obstacle_count=18)
        screen_width = self.map.width * self.map.tile_width
        screen_height = self.map.height * self.map.tile_height
        super().__init__(screen_width, screen_height, "Tactical RPG - Turn Based Combat", resizable=True)

        # Single playable character
        self.player = self.create_player()
        self.enemies = []
        self.last_xp_gain = 0

        # Game systems
        self.tactical_combat = None
        self.exploration = None
        self.xp_system = XpSystem()
        self.spawner = Ennemy_Spawner(self.map)

        # Game state
        self.phase = "menu"  # "menu", "exploration", or "combat"
        self.in_combat = False
        
        # Visual elements
        self.player_sprite = None
        self.enemy_sprites = arcade.SpriteList()
        
        self.camera = None
        
        # UI state
        self.selected_action = None  # "move" or "attack"
        self.highlighted_tiles = set()  # Tiles to highlight
        self.tile_color = arcade.color.BLUE  # Color for movement tiles
        self.turn_banner = ""
        self.turn_banner_timer = 0.0
        self.save_message = ""
        self.save_message_timer = 0.0
        
        arcade.set_background_color(arcade.color.BLACK)

    def create_player(self):
        """Create the single playable character.
        
        Returns:
            PlayerCharacter: The player character
        """
        # Create basic attack
        basic_attack = Attack("Sword", 85, 1, None, 8)
        
        player = PlayerCharacter(
            "Hero",
            level=1,
            hp=20,
            hp_max=20,
            attack=7,
            defense=5,
            speed=6,
            position=(0, 0),
            attacks=[basic_attack]
        )

        # Place player on a valid tile
        start_x, start_y = 0, 0
        while not self.map.is_walkable(start_x, start_y):
            start_x += 1
            if start_x >= self.map.width:
                start_x = 0
                start_y += 1
        self.map.place_character(player, start_x, start_y)
        
        return player 
    
    def get_map_draw_info(self):
        # Reserve side panels during combat so the map doesn't get hidden behind UI boxes.
        if self.phase == "combat":
            panel_width = 260
            margin = 10
            left_ui = panel_width + margin
            right_ui = panel_width + margin
            origin_x = left_ui
            draw_width = max(1, self.width - left_ui - right_ui)
        else:
            origin_x = 0
            draw_width = self.width

        origin_y = 0
        draw_height = self.height
        return self.map.get_draw_info(origin_x=origin_x, origin_y=origin_y, draw_width=draw_width, draw_height=draw_height)

    def grid_to_screen(self, grid_x, grid_y):
        info = self.get_map_draw_info()
        pixel_x = info["offset_x"] + grid_x * info["tile_w"] + info["tile_w"] / 2
        tile_offset_y = self.map.extra_rows_bottom
        pixel_y = info["offset_y"] + (grid_y + tile_offset_y) * info["tile_h"] + info["tile_h"] / 2
        return (pixel_x, pixel_y)

    def screen_to_grid(self, x, y):
        info = self.get_map_draw_info()
        if x < info["offset_x"] or y < info["offset_y"]:
            return None
        grid_x = int((x - info["offset_x"]) // info["tile_w"])
        relative_y = int((y - info["offset_y"]) // info["tile_h"])
        grid_y = relative_y - self.map.extra_rows_bottom
        min_y = -self.map.extra_rows_bottom
        max_y = self.map.height + self.map.extra_rows_top - 1
        if 0 <= grid_x < self.map.width and min_y <= grid_y <= max_y:
            return (grid_x, grid_y)
        return None

    def on_draw(self):
        self.clear()

        if self.phase == "menu":
            self._draw_menu()
            return

        if self.phase in ["victory", "defeat"]:
            self._draw_end_screen()
            return

        # Draw map and entities in available map space (reserve side panels in combat)
        if self.phase == "combat":
            panel_width = 260
            margin = 10
            left_ui = panel_width + margin
            right_ui = panel_width + margin
            map_origin_x = left_ui
            map_draw_w = max(1, self.width - left_ui - right_ui)
        else:
            map_origin_x = 0
            map_draw_w = self.width

        # Set combat row padding
        if self.phase == "combat":
            self.map.set_combat_extra_rows(top_rows=1, bottom_rows=1)
        else:
            self.map.clear_combat_extra_rows()

        self.map.draw(origin_x=map_origin_x, origin_y=0, draw_width=map_draw_w, draw_height=self.height)
        self._draw_characters()

        # Draw UI based on current phase
        if self.phase == "exploration":
            self._draw_exploration_ui()
        elif self.phase == "combat":
            self._draw_combat_ui()

        # Save/Load message
        if self.save_message_timer > 0 and self.save_message:
            arcade.draw_text(self.save_message, 10, 10, arcade.color.YELLOW, 14)

    def _draw_characters(self):
        """Draw player and enemy characters on the map."""
        # Draw player
        self._draw_character_sprite(self.player, arcade.color.BLUE)
        
        # Draw enemies
        for enemy in self.enemies:
            if enemy.is_alive():
                self._draw_character_sprite(enemy, arcade.color.RED)

    def _draw_character_sprite(self, character, color):
        """Draw a character sprite with HP bar.
        
        Args:
            character: Character to draw
            color: Color for the character sprite
        """
        pixel_x, pixel_y = self.grid_to_screen(*character.position)
        info = self.get_map_draw_info()

        # Draw character circle
        arc_radius = min(info["tile_w"], info["tile_h"]) / 3
        arcade.draw_circle_filled(pixel_x, pixel_y, arc_radius, color)
        
        # Draw HP bar
        bar_width = info["tile_w"] - 4
        bar_height = max(3, info["tile_h"] * 0.08)
        hp_ratio = character.hp / character.hp_max
        
        bar_y = pixel_y + info["tile_h"] / 2 + 2
        
        # Background (red)
        arcade.draw_lrbt_rectangle_filled(
            left=pixel_x - bar_width / 2,
            right=pixel_x + bar_width / 2,
            bottom=bar_y - bar_height / 2,
            top=bar_y + bar_height / 2,
            color=arcade.color.RED,
        )

        # HP (green)
        inner_width = max(1, bar_width * hp_ratio)
        arcade.draw_lrbt_rectangle_filled(
            left=pixel_x - bar_width / 2,
            right=pixel_x - bar_width / 2 + inner_width,
            bottom=bar_y - bar_height / 2,
            top=bar_y + bar_height / 2,
            color=arcade.color.GREEN,
        )

    def _draw_end_screen(self):
        message = "VICTOIRE !" if self.phase == "victory" else "DEFAITE"
        subtitle = "Appuyez sur Entrée pour recommencer." if self.phase == "victory" else "Appuyez sur Entrée pour relancer l'exploration."
        color = arcade.color.LIGHT_GREEN if self.phase == "victory" else arcade.color.LIGHT_CORAL

        arcade.draw_text(message, self.width / 2, self.height / 2 + 40, color, 36, anchor_x="center", anchor_y="center", bold=True)
        if self.phase == "victory":
            arcade.draw_text(f"XP gagnée: {self.last_xp_gain}", self.width / 2, self.height / 2, arcade.color.WHITE, 20, anchor_x="center", anchor_y="center")
            arcade.draw_text(f"Niveau: {self.player.level} XP: {self.player.xp}/{self.xp_system.required_xp(self.player.level)}", self.width / 2, self.height / 2 - 24, arcade.color.WHITE, 16, anchor_x="center", anchor_y="center")
        arcade.draw_text(subtitle, self.width / 2, self.height / 2 - 60, arcade.color.WHITE, 18, anchor_x="center", anchor_y="center")

    def _draw_exploration_ui(self):
        """Draw UI for exploration phase."""
        if not self.exploration:
            return

        # Draw action log
        y_offset = self.height - 50
        arcade.draw_text("EXPLORATION PHASE", 10, y_offset, arcade.color.WHITE, 14, bold=True)
        
        for i, action in enumerate(self.exploration.get_action_log()):
            arcade.draw_text(action, 10, y_offset - 25 - (i * 20), arcade.color.WHITE, 12)
        
        # Draw progress bar
        progress = min(1.0, self.exploration.timer / 3.0)
        bar_width = 200
        left = 50
        right = 50 + bar_width
        bottom = 20
        top = 40
        arcade.draw_line(left, bottom, right, bottom, arcade.color.WHITE, 2)
        arcade.draw_line(left, top, right, top, arcade.color.WHITE, 2)
        arcade.draw_line(left, bottom, left, top, arcade.color.WHITE, 2)
        arcade.draw_line(right, bottom, right, top, arcade.color.WHITE, 2)
        arcade.draw_lrbt_rectangle_filled(
            left=left + 1,
            right=left + 1 + bar_width * progress,
            bottom=bottom + 1,
            top=bottom + 19,
            color=arcade.color.GREEN,
        )
        arcade.draw_text(f"{progress*100:.0f}%", 60, 35, arcade.color.WHITE, 12)

    def _draw_combat_ui(self):
        """Draw UI for combat phase."""
        if not self.tactical_combat:
            return

        if self.turn_banner_timer > 0 and self.turn_banner:
            self._draw_turn_banner()

        panel_width = 260
        margin = 10
        left_panel_left = margin
        left_panel_right = left_panel_left + panel_width
        right_panel_right = self.width - margin
        right_panel_left = right_panel_right - panel_width
        panel_top = self.height - margin
        panel_bottom = margin

        arcade.draw_lrbt_rectangle_filled(left_panel_left, left_panel_right, panel_bottom, panel_top, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_lrbt_rectangle_outline(left_panel_left, left_panel_right, panel_bottom, panel_top, arcade.color.WHITE, 2)
        arcade.draw_lrbt_rectangle_filled(right_panel_left, right_panel_right, panel_bottom, panel_top, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_lrbt_rectangle_outline(right_panel_left, right_panel_right, panel_bottom, panel_top, arcade.color.WHITE, 2)

        # Draw turn indicator near top center of map zone
        turn_text = "PLAYER TURN" if self.tactical_combat.current_turn == "player" else "ENEMY TURN"
        turn_color = arcade.color.LIGHT_GREEN if self.tactical_combat.current_turn == "player" else arcade.color.LIGHT_RED
        arcade.draw_text(turn_text, self.width / 2, self.height - 30, turn_color, 16, anchor_x="center", bold=True)

        # Controls on left side panel
        controls_x = left_panel_left + 10
        controls_y = panel_top - 30
        arcade.draw_text("COMMANDES", controls_x, controls_y, arcade.color.AZURE, 14, bold=True)
        arcade.draw_text("M: Move", controls_x, controls_y - 26, arcade.color.WHITE, 12)
        arcade.draw_text("A: Attack", controls_x, controls_y - 46, arcade.color.WHITE, 12)
        arcade.draw_text("H: Heal", controls_x, controls_y - 66, arcade.color.WHITE, 12)
        arcade.draw_text("E: End Turn", controls_x, controls_y - 86, arcade.color.WHITE, 12)
        arcade.draw_text("Esc: Quit", controls_x, controls_y - 106, arcade.color.WHITE, 12)
        arcade.draw_text(f"Heal uses: {self.tactical_combat.heal_uses}", controls_x, controls_y - 130, arcade.color.LIGHT_GREEN, 12)

        # Hero stats on right side panel
        stats_x = right_panel_left + 10
        stats_y = panel_top - 30
        arcade.draw_text("HERO STATS", stats_x, stats_y, arcade.color.AZURE, 14, bold=True)
        arcade.draw_text(f"Level: {self.player.level}", stats_x, stats_y - 26, arcade.color.WHITE, 12)
        arcade.draw_text(f"HP: {self.player.hp}/{self.player.hp_max}", stats_x, stats_y - 46, arcade.color.WHITE, 12)
        arcade.draw_text(f"ATK: {self.player.attack}", stats_x, stats_y - 66, arcade.color.WHITE, 12)
        arcade.draw_text(f"DEF: {self.player.defense}", stats_x, stats_y - 86, arcade.color.WHITE, 12)
        arcade.draw_text(f"SPD: {self.player.speed}", stats_x, stats_y - 106, arcade.color.WHITE, 12)

        xp_required = self.xp_system.required_xp(self.player.level)
        xp_ratio = min(1.0, self.player.xp / xp_required if xp_required > 0 else 1.0)
        xp_bar_left = stats_x
        xp_bar_right = right_panel_right - 10
        xp_bar_height = 10
        xp_bar_y = stats_y - 130
        arcade.draw_lrbt_rectangle_filled(xp_bar_left, xp_bar_right, xp_bar_y - xp_bar_height / 2, xp_bar_y + xp_bar_height / 2, arcade.color.GRAY)
        filled_right = xp_bar_left + (xp_bar_right - xp_bar_left) * xp_ratio
        arcade.draw_lrbt_rectangle_filled(xp_bar_left, filled_right, xp_bar_y - xp_bar_height / 2, xp_bar_y + xp_bar_height / 2, arcade.color.GREEN)
        arcade.draw_text(f"XP: {self.player.xp}/{xp_required}", stats_x, xp_bar_y - 20, arcade.color.WHITE, 10)

        # Draw selected action above map
        if self.selected_action:
            action_text = f"Selected: {self.selected_action.upper()}"
            arcade.draw_text(action_text, self.width / 2, self.height - 60, arcade.color.YELLOW, 12, anchor_x="center")

        # Draw highlight tiles
        self._draw_highlighted_tiles()

    def _draw_turn_banner(self):
        """Draw temporary turn banner at center of screen."""
        if not self.turn_banner:
            return

        width = self.width * 0.6
        height = 70
        left = (self.width - width) / 2
        right = left + width
        top = self.height * 0.67
        bottom = top - height

        # Soft dark background and border
        arcade.draw_lrbt_rectangle_filled(
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            color=arcade.color.DARK_SLATE_GRAY,
        )
        arcade.draw_lrbt_rectangle_outline(
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            color=arcade.color.WHITE,
            border_width=3,
        )

        center_x = (left + right) / 2
        arcade.draw_text(
            self.turn_banner,
            center_x,
            bottom + height / 2,
            arcade.color.WHITE,
            20,
            anchor_x="center",
            anchor_y="center",
            bold=True,
            align="center",
            width=int(width - 20),
        )

    def _show_turn_banner(self, text, duration=2.0):
        """Show a temporary banner for turn messages."""
        self.turn_banner = text
        self.turn_banner_timer = duration

    def _draw_highlighted_tiles(self):
        """Draw highlighted movement and attack range tiles."""
        if self.tactical_combat.current_turn != "player" or not self.highlighted_tiles:
            return
        
        info = self.get_map_draw_info()
        for tile_x, tile_y in self.highlighted_tiles:
            pixel_x, pixel_y = self.grid_to_screen(tile_x, tile_y)

            # Draw semi-transparent tile
            if self.selected_action == "move":
                color = arcade.color.BLUE
            else:  # attack
                color = arcade.color.RED

            left = pixel_x - info["tile_w"] / 2 + 1
            right = pixel_x + info["tile_w"] / 2 - 1
            bottom = pixel_y - info["tile_h"] / 2 + 1
            top = pixel_y + info["tile_h"] / 2 - 1
            arcade.draw_line(left, bottom, right, bottom, color, 2)
            arcade.draw_line(left, top, right, top, color, 2)
            arcade.draw_line(left, bottom, left, top, color, 2)
            arcade.draw_line(right, bottom, right, top, color, 2)

    def on_update(self, delta_time):
        """Update game state each frame."""
        if self.phase == "exploration":
            self._update_exploration(delta_time)
        elif self.phase == "combat":
            self._update_combat(delta_time)

        # Update temporary combat banners
        if self.turn_banner_timer > 0:
            self.turn_banner_timer -= delta_time
            if self.turn_banner_timer <= 0:
                self.turn_banner_timer = 0
                self.turn_banner = ""
        if self.save_message_timer > 0:
            self.save_message_timer -= delta_time
            if self.save_message_timer <= 0:
                self.save_message_timer = 0
                self.save_message = ""

    def _update_exploration(self, delta_time):
        """Update exploration phase.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        if not self.exploration:
            self._start_exploration()
        
        # Check if exploration is complete
        if self.exploration.update(delta_time):
            self._transition_to_combat()

    def _start_exploration(self):
        """Start the exploration phase."""
        self.exploration = ExplorationPhase(self.map, self.player)
        self.exploration.start_exploration()

        # Place player at random valid free position
        for _ in range(100):
            pos = self.exploration.random_character_position()
            if not self.map.is_occupied(pos[0], pos[1]):
                self.map.move_character(self.player, pos[0], pos[1])
                return
        # fallback: keep current player position if no free tile found
        self.map.move_character(self.player, self.player.position[0], self.player.position[1])

    def _transition_to_combat(self):
        """Transition from exploration to combat phase."""
        self.phase = "combat"
        self.exploration = None
        
        # Spawn enemies based on player level
        self.enemies = self.spawner.spawn_wave(self.player.level)
        
        # Initialize tactical combat
        self.tactical_combat = TacticalCombat(self.player, self.enemies, self.map)
        self.selected_action = None
        self.highlighted_tiles = set()
        self._show_turn_banner("Tour du joueur")

    def _update_combat(self, delta_time):
        """Update combat phase.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        if not self.tactical_combat:
            return
        
        # Check for combat end
        result = self.tactical_combat.check_combat_end()
        
        if result == "victory":
            self._end_combat_victory()
        elif result == "defeat":
            self._end_combat_defeat()

    def _end_combat_victory(self):
        """Handle victory and transition to victory screen."""
        total_xp = sum(100 for enemy in self.enemies if not enemy.is_alive())
        self.last_xp_gain = total_xp
        self.xp_system.gain_xp(self.player, total_xp)

        # Cleanup enemy entities and end combat
        for enemy in self.enemies:
            old_pos = enemy.position
            if old_pos in self.map.entities:
                del self.map.entities[old_pos]
        self.enemies = []
        self.tactical_combat = None
        self.selected_action = None
        self.highlighted_tiles = set()

        self.phase = "victory"

    def _end_combat_defeat(self):
        """Handle defeat and transition to defeat screen."""
        self.player.hp = self.player.hp_max

        # Cleanup enemy entities and end combat
        for enemy in self.enemies:
            old_pos = enemy.position
            if old_pos in self.map.entities:
                del self.map.entities[old_pos]
        self.enemies = []
        self.tactical_combat = None
        self.selected_action = None
        self.highlighted_tiles = set()

        self.phase = "defeat"

    def _draw_menu(self):
        arcade.draw_text("Tactical RPG", self.width / 2, self.height - 120, arcade.color.WHITE, 36, anchor_x="center")
        arcade.draw_text("Press [ENTER] to Start", self.width / 2, self.height - 180, arcade.color.AZURE, 22, anchor_x="center")
        arcade.draw_text("Press [ESCAPE] to Quit", self.width / 2, self.height - 220, arcade.color.ORANGE, 20, anchor_x="center")
        arcade.draw_text("Controls: M=Move, A=Attack, E=End Turn", self.width / 2, self.height - 270, arcade.color.LIGHT_GRAY, 16, anchor_x="center")
        arcade.draw_text("S: Save, L: Load", self.width / 2, self.height - 310, arcade.color.LIGHT_GRAY, 16, anchor_x="center")

    def save_game(self):
        save_data = {
            "player": {
                "name": self.player.name,
                "level": self.player.level,
                "hp": self.player.hp,
                "hp_max": self.player.hp_max,
                "attack": self.player.attack,
                "defense": self.player.defense,
                "speed": self.player.speed,
                "xp": self.player.xp,
                "position": list(self.player.position),
                "attacks": [
                    {
                        "name": atk.name,
                        "precision": atk.precision,
                        "range": atk.range,
                        "special_effect": atk.special_effect,
                        "base_damage": atk.base_damage,
                    }
                    for atk in self.player.attacks
                ],
            },
            "map": {
                "width": self.map.width,
                "height": self.map.height,
                "tile_width": self.map.tile_width,
                "tile_height": self.map.tile_height,
                "obstacles": [list(o) for o in self.map.obstacles],
            },
            "enemies": [
                {
                    "name": enemy.name,
                    "level": enemy.level,
                    "hp": enemy.hp,
                    "hp_max": enemy.hp_max,
                    "attack": enemy.attack,
                    "defense": enemy.defense,
                    "speed": enemy.speed,
                    "position": list(enemy.position),
                    "attacks": [
                        {
                            "name": atk.name,
                            "precision": atk.precision,
                            "range": atk.range,
                            "special_effect": atk.special_effect,
                            "base_damage": atk.base_damage,
                        }
                        for atk in enemy.attacks
                    ],
                }
                for enemy in self.enemies
            ],
            "phase": self.phase,
        }

        save_path = os.path.join(os.getcwd(), "savegame.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        self.save_message = "Sauvegarde enregistrée !"
        self.save_message_timer = 2.0

    def load_game(self):
        save_path = os.path.join(os.getcwd(), "savegame.json")
        save_path = os.path.join(os.getcwd(), "savegame.json")
        if not os.path.exists(save_path):
            print("Aucune sauvegarde trouvée.")
            return

        with open(save_path, "r", encoding="utf-8") as f:
            save_data = json.load(f)

        map_data = save_data.get("map", {})
        self.map = GameMap(
            width=map_data.get("width", 14),
            height=map_data.get("height", 10),
            tile_width=map_data.get("tile_width", 64),
            tile_height=map_data.get("tile_height", 64),
            obstacle_count=0,
        )
        self.map.obstacles = set(tuple(x) for x in map_data.get("obstacles", []))
        self.map.entities.clear()

        player_data = save_data.get("player", {})
        player_attacks = [
            Attack(atk["name"], atk["precision"], atk["range"], atk.get("special_effect"), atk["base_damage"])
            for atk in player_data.get("attacks", [])
        ]
        self.player = PlayerCharacter(
            player_data.get("name", "Hero"),
            player_data.get("level", 1),
            player_data.get("hp", 20),
            player_data.get("hp_max", 20),
            player_data.get("attack", 7),
            player_data.get("defense", 5),
            player_data.get("speed", 6),
            tuple(player_data.get("position", [0, 0])),
            player_attacks,
        )
        self.player.xp = player_data.get("xp", 0)
        self.map.place_character(self.player, *self.player.position)

        self.enemies = []
        for enemy_data in save_data.get("enemies", []):
            enemy_attacks = [
                Attack(atk["name"], atk["precision"], atk["range"], atk.get("special_effect"), atk["base_damage"])
                for atk in enemy_data.get("attacks", [])
            ]
            enemy = Enemy(
                enemy_data.get("name", "Ennemi"),
                enemy_data.get("level", 1),
                enemy_data.get("hp", 15),
                enemy_data.get("hp_max", 15),
                enemy_data.get("attack", 7),
                enemy_data.get("defense", 3),
                enemy_data.get("speed", 3),
                tuple(enemy_data.get("position", [0, 0])),
                enemy_attacks,
            )
            self.map.place_character(enemy, *enemy.position)
            self.enemies.append(enemy)

        self.phase = save_data.get("phase", "exploration")
        self.tactical_combat = None
        self.selected_action = None
        self.highlighted_tiles = set()
        self.save_message = "Partie chargée !"
        self.save_message_timer = 2.0

    def on_key_press(self, key, modifiers):
        """Handle key press events."""
        if key == arcade.key.ESCAPE:
            self.close()
            return

        if key == arcade.key.S:
            self.save_game()
            return
        if key == arcade.key.L:
            self.load_game()
            return

        if self.phase == "menu":
            if key == arcade.key.ENTER or key == arcade.key.RETURN:
                self.phase = "exploration"
                self.exploration = None
                self.tactical_combat = None
                self.selected_action = None
                self.highlighted_tiles = set()
                self.enemies = []
                self.player.hp = self.player.hp_max
                self.map.entities.clear()
                start_x, start_y = 0, 0
                while not self.map.is_walkable(start_x, start_y):
                    start_x += 1
                    if start_x >= self.map.width:
                        start_x = 0
                        start_y += 1
                self.map.place_character(self.player, start_x, start_y)
                self._start_exploration()
            return

        if self.phase in ["victory", "defeat"]:
            if key == arcade.key.ENTER or key == arcade.key.RETURN:
                self.phase = "exploration"
                self.exploration = None
                self.tactical_combat = None
                self.selected_action = None
                self.highlighted_tiles = set()
                self.enemies = []
                self.player.hp = self.player.hp_max
                self.map.entities.clear()
                start_x, start_y = 0, 0
                while not self.map.is_walkable(start_x, start_y):
                    start_x += 1
                    if start_x >= self.map.width:
                        start_x = 0
                        start_y += 1
                self.map.place_character(self.player, start_x, start_y)
                self._start_exploration()
            return

        if self.phase == "combat":
            self._handle_combat_key(key, modifiers)
    
    def _handle_combat_key(self, key, modifiers):
        """Handle key press during combat.
        
        Args:
            key: Key code
            modifiers: Key modifiers
        """
        if self.tactical_combat.current_turn != "player":
            return
        
        # Select movement action
        if key == arcade.key.M:
            self.selected_action = "move"
            self.highlighted_tiles = self.tactical_combat.get_movement_tiles()
        
        # Select attack action
        elif key == arcade.key.A:
            self.selected_action = "attack"
            self.highlighted_tiles = self.tactical_combat.get_attack_tiles()

        # Select heal action
        elif key == arcade.key.H:
            self.selected_action = "heal"
            self.highlighted_tiles = set()
            heal_result = self.tactical_combat.player_heal()
            if heal_result["success"]:
                self.selected_action = None
                self.highlighted_tiles = set()
            else:
                print(f"Heal failed: {heal_result['reason']}")

        # Execute movement
        elif key == arcade.key.UP and self.selected_action == "move":
            x, y = self.player.position
            if self.tactical_combat.player_move(x, y + 1):
                self.selected_action = None
                self.highlighted_tiles = set()
        
        elif key == arcade.key.DOWN and self.selected_action == "move":
            x, y = self.player.position
            if self.tactical_combat.player_move(x, y - 1):
                self.selected_action = None
                self.highlighted_tiles = set()
        
        elif key == arcade.key.LEFT and self.selected_action == "move":
            x, y = self.player.position
            if self.tactical_combat.player_move(x - 1, y):
                self.selected_action = None
                self.highlighted_tiles = set()
        
        elif key == arcade.key.RIGHT and self.selected_action == "move":
            x, y = self.player.position
            if self.tactical_combat.player_move(x + 1, y):
                self.selected_action = None
                self.highlighted_tiles = set()
        
        # End player turn
        elif key == arcade.key.E:
            if self.tactical_combat.current_turn == "player":
                self.tactical_combat.end_player_turn()
                self.selected_action = None
                self.highlighted_tiles = set()
                self._show_turn_banner("Tour ennemi")

                # Process enemy turns
                self._process_all_enemy_turns()
    
    def _process_all_enemy_turns(self):
        """Process all enemy turns until player turn returns."""
        started_enemy = self.tactical_combat.current_turn == "enemy"
        while self.tactical_combat.current_turn == "enemy":
            self.tactical_combat.process_enemy_turn()
        if started_enemy and self.tactical_combat.current_turn == "player":
            self._show_turn_banner("Tour du joueur")
    
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click for tile selection in combat.
        
        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            button: Mouse button
            modifiers: Key modifiers
        """
        if self.phase != "combat" or not self.selected_action:
            return
        
        if self.tactical_combat.current_turn != "player":
            return
        
        # Convert pixel to grid coordinates
        grid_coords = self.screen_to_grid(x, y)
        if not grid_coords:
            return
        grid_x, grid_y = grid_coords

        if self.selected_action == "move":
            if self.tactical_combat.player_move(grid_x, grid_y):
                self.selected_action = None
                self.highlighted_tiles = set()
        
        elif self.selected_action == "attack":
            result = self.tactical_combat.player_attack(grid_x, grid_y)
            if result["success"]:
                if result.get("killed"):
                    xp_gain = result.get("xp_gain", 0)
                    self.last_xp_gain = xp_gain
                    self.xp_system.gain_xp(self.player, xp_gain)
                    print(f"Vous avez gagné {xp_gain} XP !")
                self.selected_action = None
                self.highlighted_tiles = set()

        self.in_combat = False
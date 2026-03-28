import arcade
import json
import os
import time
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
        super().__init__(screen_width, screen_height, "The_Game", resizable=True, fullscreen=True)

        # Personnage jouable unique
        self.player = self.create_player()
        self.enemies = []
        self.last_xp_gain = 0

        # Systèmes de jeu
        self.tactical_combat = None
        self.exploration = None
        self.xp_system = XpSystem()
        self.spawner = Ennemy_Spawner(self.map)

        # Système de sauvegarde
        self.SAVE_SLOTS = 3
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.save_folder = os.path.join(project_root, "data", "saves")
        self._ensure_save_folder()
        self.previous_phase = "exploration"

        # État du jeu
        self.phase = "menu"  # "menu", "exploration", "combat", "load_menu", "save_menu", "victory", "defeat", "tutorial"
        self.in_combat = False
        
        # État de confirmation de suppression
        self.deleting_slot = None  # Numéro de slot considéré pour suppression (1-3)
        
        # Éléments visuels
        self.player_sprite = None
        self.enemy_sprites = arcade.SpriteList()
        
        self.camera = None
        
        # État de l'interface utilisateur
        self.selected_action = None  # "move" ou "attack"
        self.highlighted_tiles = set()  # Cases à mettre en surbrillance
        self.tile_color = arcade.color.BLUE  # Couleur pour les cases de mouvement
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

    def _ensure_save_folder(self):
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder, exist_ok=True)

    def _get_save_path(self, slot):
        return os.path.join(self.save_folder, f"save_slot_{slot}.json")

    def _has_save_slot(self, slot):
        return os.path.exists(self._get_save_path(slot))
    
    def _any_save_exists(self):
        return any(self._has_save_slot(slot) for slot in range(1, self.SAVE_SLOTS + 1))

    def _read_slot_info(self, slot):
        path = self._get_save_path(slot)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                player = data.get("player", {})
                return {
                    "name": player.get("name", "Hero"),
                    "level": player.get("level", 1),
                    "hp": player.get("hp", 0),
                    "hp_max": player.get("hp_max", 0),
                    "xp": player.get("xp", 0),
                    "saved_at": data.get("saved_at", "?")
                }
        except Exception:
            return None

    def _start_new_game(self):
        # Show tutorial first
        self.phase = "tutorial"
        self.enemies = []
        self.tactical_combat = None
        self.exploration = None
        self.selected_action = None
        self.highlighted_tiles = set()
        self.save_message = ""
        self.save_message_timer = 0.0
        self.last_xp_gain = 0

        self.player.hp = self.player.hp_max
        self.map.entities.clear()
        
        # Regenerate heal station for new game
        self.map.heal_station = None
        self.map._generate_heal_station()
        
        # Reinitialize spawner to analyze obstacles
        self.spawner.initialize_spawn_system()
        
        start_x, start_y = 0, 0
        while not self.map.is_walkable(start_x, start_y):
            start_x += 1
            if start_x >= self.map.width:
                start_x = 0
                start_y += 1
        self.map.place_character(self.player, start_x, start_y)

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

        if self.phase == "load_menu":
            self._draw_load_menu()
            return

        if self.phase == "save_menu":
            self._draw_save_menu()
            return

        if self.phase in ["victory", "defeat"]:
            self._draw_end_screen()
            return

        if self.phase == "tutorial":
            self._draw_tutorial()
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
                color = getattr(enemy, "color", arcade.color.RED)
                self._draw_character_sprite(enemy, color)

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
        # Draw background based on phase
        if self.phase == "victory":
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, arcade.color.BLUE)
        else:
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, arcade.color.DARK_RED)
        
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
        arcade.draw_text("PHASE D'EXPLORATION", 10, y_offset, arcade.color.WHITE, 14, bold=True)
        
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
        turn_text = "TOUR DU JOUEUR" if self.tactical_combat.current_turn == "player" else "TOUR ENNEMI"
        turn_color = arcade.color.LIGHT_GREEN if self.tactical_combat.current_turn == "player" else arcade.color.LIGHT_RED
        arcade.draw_text(turn_text, self.width / 2, self.height - 30, turn_color, 16, anchor_x="center", bold=True)

        # Controls on left side panel
        controls_x = left_panel_left + 10
        controls_y = panel_top - 30
        arcade.draw_text("COMMANDES", controls_x, controls_y, arcade.color.AZURE, 14, bold=True)
        arcade.draw_text("M: Déplacer", controls_x, controls_y - 26, arcade.color.WHITE, 12)
        arcade.draw_text("A: Attaquer", controls_x, controls_y - 46, arcade.color.WHITE, 12)
        arcade.draw_text("H: Soigner", controls_x, controls_y - 66, arcade.color.WHITE, 12)
        arcade.draw_text("E: Finir le tour", controls_x, controls_y - 86, arcade.color.WHITE, 12)
        arcade.draw_text("Échap: Quitter", controls_x, controls_y - 106, arcade.color.WHITE, 12)
        arcade.draw_text("S: Sauvegarder", controls_x, controls_y - 126, arcade.color.WHITE, 12)
        arcade.draw_text("L: Charger", controls_x, controls_y - 146, arcade.color.WHITE, 12)
        arcade.draw_text(f"Utilisations de soin: {self.tactical_combat.heal_uses}", controls_x, controls_y - 170, arcade.color.LIGHT_GREEN, 12)
        
        # Draw icons below commands
        icon_y = controls_y - 200
        arcade.draw_text("LÉGENDE", controls_x, icon_y, arcade.color.AZURE, 14, bold=True)
        
        # Enemy icon (red circle)
        icon_x = controls_x + 10
        icon_y -= 30
        arcade.draw_circle_filled(icon_x, icon_y, 10, arcade.color.RED)
        arcade.draw_text("Ennemi", icon_x + 15, icon_y - 5, arcade.color.WHITE, 11)
        
        # Boss icon (purple circle with border)
        icon_y -= 25
        arcade.draw_circle_outline(icon_x, icon_y, 12, arcade.color.PURPLE, 3)
        arcade.draw_circle_filled(icon_x, icon_y, 10, arcade.color.PURPLE)
        arcade.draw_text("Boss", icon_x + 15, icon_y - 5, arcade.color.WHITE, 11)
        
        # Obstacle icon (gray square)
        icon_y -= 25
        arcade.draw_lrbt_rectangle_filled(icon_x - 8, icon_x + 8, icon_y - 8, icon_y + 8, arcade.color.GRAY)
        arcade.draw_text("Obstacle", icon_x + 15, icon_y - 5, arcade.color.WHITE, 11)
        
        # Heal station icon (light green circle)
        icon_y -= 25
        arcade.draw_circle_filled(icon_x, icon_y, 10, arcade.color.LIGHT_GREEN)
        arcade.draw_text("Station de soin", icon_x + 15, icon_y - 5, arcade.color.LIGHT_GREEN, 11)

        # Hero stats on right side panel
        stats_x = right_panel_left + 10
        stats_y = panel_top - 30
        arcade.draw_text("STATS DU HÉROS", stats_x, stats_y, arcade.color.AZURE, 14, bold=True)
        arcade.draw_text(f"Niveau: {self.player.level}", stats_x, stats_y - 26, arcade.color.WHITE, 12)
        arcade.draw_text(f"PV: {self.player.hp}/{self.player.hp_max}", stats_x, stats_y - 46, arcade.color.WHITE, 12)
        arcade.draw_text(f"ATK: {self.player.attack}", stats_x, stats_y - 66, arcade.color.WHITE, 12)
        arcade.draw_text(f"DÉF: {self.player.defense}", stats_x, stats_y - 86, arcade.color.WHITE, 12)
        arcade.draw_text(f"VIT: {self.player.speed}", stats_x, stats_y - 106, arcade.color.WHITE, 12)

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
            action_text = f"Sélectionné: {self.selected_action.upper()}"
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
        self.phase = "exploration"
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

    def _restart_game(self):
        """Restart the game after combat ends without showing tutorial."""
        self.phase = "exploration"
        self.enemies = []
        self.tactical_combat = None
        self.exploration = None
        self.selected_action = None
        self.highlighted_tiles = set()
        self.save_message = ""
        self.save_message_timer = 0.0
        self.last_xp_gain = 0

        self.player.hp = self.player.hp_max
        self.map.entities.clear()
        
        # Regenerate heal station for new game
        self.map.heal_station = None
        self.map._generate_heal_station()
        
        # Reinitialize spawner to analyze obstacles
        self.spawner.initialize_spawn_system()
        
        start_x, start_y = 0, 0
        while not self.map.is_walkable(start_x, start_y):
            start_x += 1
            if start_x >= self.map.width:
                start_x = 0
                start_y += 1
        self.map.place_character(self.player, start_x, start_y)

        # Start exploration directly (skip tutorial)
        self._start_exploration()

    def _draw_menu(self):
        # Draw blue background
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, arcade.color.JADE)
        
        # Calculate vertical center position
        title_y = self.height / 2 + 40
        subtitle_y = self.height / 2 - 20
        
        arcade.draw_text("The_Game", self.width / 2, title_y, arcade.color.DARK_JUNGLE_GREEN, 48, anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_text("Appuyez sur ENTRÉE pour lancer le jeu", self.width / 2, subtitle_y, arcade.color.DARK_JUNGLE_GREEN, 24, anchor_x="center", anchor_y="center")

    def _draw_tutorial(self):
        """Draw tutorial screen with game instructions."""
        # Draw blue background
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, arcade.color.JADE)
        
        # Calculate total content height for centering
        # Title + 80px gap + instructions (20 lines: 16 regular @ 25px, 4 empty @ 15px)
        content_height = 80 + (16 * 25) + (4 * 15)  # = 540
        
        # Calculate starting Y position to center content
        title_y = self.height / 2 + content_height / 2 - 40
        arcade.draw_text("BIENVENUE DANS THE_GAME !", self.width / 2, title_y, arcade.color.DARK_JUNGLE_GREEN, 36, anchor_x="center", anchor_y="center", bold=True)
        
        instructions = [
            "CONTRÔLES DE BASE :",
            "",
            "M : Activer le mode déplacement (cases bleues)",
            "   Utilisez les flèches du clavier pour vous déplacer",
            "",
            "A : Activer le mode attaque (cases rouges)",
            "   Cliquez sur une case rouge pour attaquer un ennemi",
            "",
            "H : Se soigner (limité à 3 utilisations par combat)",
            "",
            "E : Finir votre tour (les ennemis joueront après)",
            "",
            "LÉGENDE :",
            "● Bleu : Votre personnage",
            "● Rouge : Ennemis normaux",
            "● Violet : Boss ennemis",
            "■ Gris : Obstacles (infranchissables)",
            "● Vert : Stations de soin",
            "",
            "BONNE CHANCE !",
            "",
            "Appuyez sur ENTRÉE pour commencer"
        ]
        
        y_offset = title_y - 80
        for line in instructions:
            if "CONTRÔLES" in line or "LÉGENDE" in line:
                arcade.draw_text(line, self.width / 2, y_offset, arcade.color.DARK_JUNGLE_GREEN, 18, anchor_x="center", anchor_y="center", bold=True)
            elif "BONNE CHANCE" in line:
                arcade.draw_text(line, self.width / 2, y_offset, arcade.color.DARK_JUNGLE_GREEN, 20, anchor_x="center", anchor_y="center", bold=True)
            elif "ENTRÉE" in line and "Appuyez" in line:
                arcade.draw_text(line, self.width / 2, y_offset, arcade.color.DARK_JUNGLE_GREEN, 18, anchor_x="center", anchor_y="center", bold=True)
            elif line.startswith("●"):
                arcade.draw_text(line, self.width / 2, y_offset, arcade.color.DARK_JUNGLE_GREEN, 16, anchor_x="center", anchor_y="center")
            elif line.startswith("■"):
                arcade.draw_text(line, self.width / 2, y_offset, arcade.color.DARK_JUNGLE_GREEN, 16, anchor_x="center", anchor_y="center")
            elif line == "":
                y_offset -= 15
                continue
            else:
                arcade.draw_text(line, self.width / 2, y_offset, arcade.color.DARK_JUNGLE_GREEN, 16, anchor_x="center", anchor_y="center")
            y_offset -= 25

    def _draw_load_menu(self):
        # Draw jade background
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, arcade.color.JADE)
        
        title = "Choisissez un emplacement de sauvegarde"
        title_color = arcade.color.DARK_JUNGLE_GREEN
        
        # Show delete mode indicator
        if self.deleting_slot == -1:
            title = "MODE SUPPRESSION - Appuyez sur 1, 2 ou 3"
            title_color = arcade.color.DARK_JUNGLE_GREEN
        
        # Calculate vertical center position for content
        # Title at top center of content block
        title_y = self.height / 2 + 60
        arcade.draw_text(title, self.width / 2, title_y, title_color, 28, anchor_x="center", anchor_y="center")
        
        # Save slots below title
        slot_y_start = title_y - 50
        for slot in range(1, self.SAVE_SLOTS + 1):
            info = self._read_slot_info(slot)
            y = slot_y_start - (slot - 1) * 40
            
            # Highlight slots in delete mode
            if self.deleting_slot == -1 and info:
                arcade.draw_lrbt_rectangle_filled(
                    left=self.width / 2 - 250,
                    right=self.width / 2 + 250,
                    bottom=y - 12,
                    top=y + 12,
                    color=arcade.color.LAVENDER_BLUE
                )
            
            if info:
                saved_at = info.get("saved_at", "?")
                arcade.draw_text(f"{slot}) {info['name']} Nv {info['level']} PV {info['hp']}/{info['hp_max']} XP {info['xp']} ({saved_at})", self.width / 2, y, arcade.color.DARK_JUNGLE_GREEN, 14, anchor_x="center", anchor_y="center")
            else:
                arcade.draw_text(f"{slot}) Vide", self.width / 2, y, arcade.color.DARK_JUNGLE_GREEN, 16, anchor_x="center", anchor_y="center")
        
        # Footer text at bottom center of content block
        footer_y = slot_y_start - 150
        if self.deleting_slot == -1:
            arcade.draw_text("1-3: Supprimer | D ou ÉCHAP: Annuler", self.width / 2, footer_y, arcade.color.DARK_JUNGLE_GREEN, 16, anchor_x="center", anchor_y="center")
        else:
            arcade.draw_text("1-3: Charger | D: Mode suppression | N: Nouvelle partie | ÉCHAP: Retour", self.width / 2, footer_y, arcade.color.DARK_JUNGLE_GREEN, 16, anchor_x="center", anchor_y="center")

    def _draw_save_menu(self):
        # Draw jade background
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, arcade.color.JADE)
        
        arcade.draw_text("Enregistrer la partie : choisissez un slot", self.width / 2, self.height - 120, arcade.color.BLACK, 28, anchor_x="center")
        for slot in range(1, self.SAVE_SLOTS + 1):
            info = self._read_slot_info(slot)
            y = self.height - 180 - slot * 40
            if info:
                saved_at = info.get("saved_at", "?")
                arcade.draw_text(f"{slot}) {info['name']} Nv {info['level']} - REMPLACE ({saved_at})", self.width / 2, y, arcade.color.ORANGE, 14, anchor_x="center")
            else:
                arcade.draw_text(f"{slot}) Vide", self.width / 2, y, arcade.color.LIGHT_GREEN, 16, anchor_x="center")
        arcade.draw_text("1-3: Sauvegarder | ÉCHAP: Annuler", self.width / 2, 60, arcade.color.YELLOW, 16, anchor_x="center")

    def save_game(self, slot):
        self._ensure_save_folder()
        # Save only player stats
        save_data = {
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "player": {
                "name": self.player.name,
                "level": self.player.level,
                "hp": self.player.hp,
                "hp_max": self.player.hp_max,
                "attack": self.player.attack,
                "defense": self.player.defense,
                "speed": self.player.speed,
                "xp": self.player.xp,
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
        }

        slot_path = self._get_save_path(slot)
        with open(slot_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        self.save_message = f"Sauvegarde enregistrée dans slot {slot}!"
        self.save_message_timer = 2.0

    def _find_first_walkable_empty_tile(self):
        for y in range(self.map.height):
            for x in range(self.map.width):
                if self.map.is_walkable(x, y) and not self.map.is_occupied(x, y):
                    return (x, y)
        return None

    def _place_entity(self, entity, position):
        x, y = position
        if self.map.place_character(entity, x, y):
            return True

        # Try to keep the entity on a nearby valid tile
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                nx, ny = x + dx, y + dy
                if self.map.is_walkable(nx, ny) and not self.map.is_occupied(nx, ny):
                    return self.map.place_character(entity, nx, ny)

        fallback = self._find_first_walkable_empty_tile()
        if fallback:
            return self.map.place_character(entity, fallback[0], fallback[1])
        return False

    def delete_game(self, slot):
        """Delete a save game file.
        
        Args:
            slot: Slot number to delete (1-3)
        """
        slot_path = self._get_save_path(slot)
        if not os.path.exists(slot_path):
            self.save_message = f"Aucune sauvegarde dans le slot {slot}."
            self.save_message_timer = 2.0
            return False
        
        try:
            os.remove(slot_path)
            self.save_message = f"Sauvegarde slot {slot} supprimée !"
            self.save_message_timer = 2.0
            self.deleting_slot = None
            return True
        except Exception as e:
            self.save_message = f"Erreur lors de la suppression: {e}"
            self.save_message_timer = 2.0
            self.deleting_slot = None
            return False

    def load_game(self, slot):
        slot_path = self._get_save_path(slot)
        if not os.path.exists(slot_path):
            self.save_message = f"Aucune sauvegarde dans le slot {slot}."
            self.save_message_timer = 2.0
            return False

        with open(slot_path, "r", encoding="utf-8") as f:
            save_data = json.load(f)

        # Load player stats only
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
            (0, 0),  # Temporary position, will be placed later
            player_attacks,
        )
        self.player.xp = player_data.get("xp", 0)

        # Regenerate a new map with heal station
        self.map = GameMap(width=14, height=10, tile_width=64, tile_height=64, obstacle_count=18)
        self.map.entities.clear()
        
        # Ensure heal station is generated
        if not self.map.heal_station:
            self.map._generate_heal_station()

        # Update spawner with new map and reinitialize
        self.spawner.map = self.map
        self.spawner.initialize_spawn_system()

        # Place player on a valid tile
        start_x, start_y = 0, 0
        while not self.map.is_walkable(start_x, start_y):
            start_x += 1
            if start_x >= self.map.width:
                start_x = 0
                start_y += 1
        self.map.place_character(self.player, start_x, start_y)

        # Spawn enemies based on player level
        self.enemies = self.spawner.spawn_wave(self.player.level)

        # Start in exploration phase
        self.phase = "exploration"
        self.tactical_combat = None
        self.exploration = None
        self.selected_action = None
        self.highlighted_tiles = set()
        self.last_xp_gain = 0

        # Start exploration
        self._start_exploration()

        self.save_message = f"Sauvegarde slot {slot} chargée !"
        self.save_message_timer = 2.0
        return True

    def on_key_press(self, key, modifiers):
        """Handle key press events."""
        print(f"Key pressed: {key}, Current phase: {self.phase}")
        if key == arcade.key.ESCAPE:
            if self.phase in ["load_menu", "save_menu"]:
                self.phase = "menu"
                return
            self.close()
            return

        if self.phase == "menu":
            if key == arcade.key.ENTER or key == arcade.key.RETURN:
                if self._any_save_exists():
                    self.phase = "load_menu"
                else:
                    self._start_new_game()
                return
            return

        if self.phase == "load_menu":
            # Handle ESC to cancel delete mode
            if key == arcade.key.ESCAPE:
                if self.deleting_slot is not None:
                    self.deleting_slot = None
                    return
                self.phase = "menu"
                return
            
            # Handle D key to toggle delete mode
            if key == arcade.key.D:
                self.deleting_slot = -1 if self.deleting_slot is None else None
                return
            
            # In delete mode, pressing 1/2/3 deletes the slot directly
            if self.deleting_slot == -1 and key in [arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3]:
                slot = 1 if key == arcade.key.KEY_1 else 2 if key == arcade.key.KEY_2 else 3
                if self._has_save_slot(slot):
                    self.delete_game(slot)
                else:
                    self.save_message = f"Aucune sauvegarde dans le slot {slot}."
                    self.save_message_timer = 2.0
                return
            
            # Load game normally (only if not in delete mode)
            if self.deleting_slot is None:
                if key == arcade.key.KEY_1:
                    slot = 1
                elif key == arcade.key.KEY_2:
                    slot = 2
                elif key == arcade.key.KEY_3:
                    slot = 3
                else:
                    slot = None

                if slot is not None:
                    if self.load_game(slot):
                        # phase is restored by load_game
                        pass
                    return
                if key == arcade.key.N:
                    self._start_new_game()
                    return
            return

        if self.phase == "save_menu":
            if key == arcade.key.KEY_1:
                slot = 1
            elif key == arcade.key.KEY_2:
                slot = 2
            elif key == arcade.key.KEY_3:
                slot = 3
            else:
                slot = None

            if slot is not None:
                self.save_game(slot)
                self.phase = self.previous_phase
                return
            if key == arcade.key.ESCAPE:
                self.phase = self.previous_phase
                return
            return

        if key == arcade.key.S and self.phase in ["exploration", "combat"]:
            self.previous_phase = self.phase
            self.phase = "save_menu"
            return

        if key == arcade.key.L and self.phase in ["menu", "exploration", "combat"]:
            self.phase = "load_menu"
            return

        if self.phase in ["victory", "defeat"]:
            if key == arcade.key.ENTER or key == arcade.key.RETURN:
                self._restart_game()
            return

        if self.phase == "tutorial":
            # Check for all possible Enter key variations (regular Enter and numpad Enter)
            if key == arcade.key.ENTER or key == arcade.key.RETURN or key == arcade.key.NUM_ENTER:
                print("Tutoriel : Touche Entrée détectée - Démarrage de l'exploration")
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
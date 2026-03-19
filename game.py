import arcade
from Map.game_map import GameMap
from system.enemy_spawner import Ennemy_Spawner
from system.xp_system import XpSystem
from system.exploration_phase import ExplorationPhase
from Entities.Player_character import PlayerCharacter
from Entities.Attack import Attack
from Combat.tactical_combat import TacticalCombat

class Game(arcade.Window):
    def __init__(self):
        self.map = GameMap(width=14, height=10, tile_width=64, tile_height=64, obstacle_count=18)
        screen_width = self.map.width * self.map.tile_width
        screen_height = self.map.height * self.map.tile_height
        super().__init__(screen_width, screen_height, "Tactical RPG - Turn Based Combat")

        # Single playable character
        self.player = self.create_player()
        self.enemies = []

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
    
    def on_draw(self):
        self.clear()

        if self.phase == "menu":
            self._draw_menu()
            return

        # Draw map and entities
        self.map.draw()
        self._draw_characters()

        # Draw UI based on current phase
        if self.phase == "exploration":
            self._draw_exploration_ui()
        elif self.phase == "combat":
            self._draw_combat_ui()

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
        pixel_x, pixel_y = self.map.pixel_to_grid(*character.position)
        
        # Draw character circle
        arcade.draw_circle_filled(pixel_x, pixel_y, self.map.tile_width // 3, color)
        
        # Draw HP bar
        bar_width = self.map.tile_width - 4
        bar_height = 4
        hp_ratio = character.hp / character.hp_max
        
        bar_y = pixel_y + self.map.tile_height // 2 + 2
        
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
        
        # Draw turn indicator
        turn_text = "PLAYER TURN" if self.tactical_combat.current_turn == "player" else "ENEMY TURN"
        turn_color = arcade.color.LIGHT_GREEN if self.tactical_combat.current_turn == "player" else arcade.color.LIGHT_RED
        arcade.draw_text(turn_text, 10, self.height - 40, turn_color, 16, bold=True)
        
        # Draw player stats
        y = self.height - 70
        arcade.draw_text(f"HP: {self.player.hp}/{self.player.hp_max}", 10, y, arcade.color.WHITE, 12)
        arcade.draw_text(f"Level: {self.player.level}", 10, y - 20, arcade.color.WHITE, 12)
        
        # Draw controls
        y -= 60
        arcade.draw_text("CONTROLS:", 10, y, arcade.color.YELLOW, 12, bold=True)
        y -= 25
        arcade.draw_text("[M] Move", 10, y, arcade.color.WHITE, 11)
        arcade.draw_text("[A] Attack", 150, y, arcade.color.WHITE, 11)
        arcade.draw_text("[H] Heal", 260, y, arcade.color.WHITE, 11)
        arcade.draw_text("[E] End Turn", 340, y, arcade.color.WHITE, 11)
        
        arcade.draw_text(f"Heal uses: {self.tactical_combat.heal_uses}", 10, y - 30, arcade.color.LIGHT_GREEN, 12)

        # Draw selected action
        if self.selected_action:
            action_text = f"Selected: {self.selected_action.upper()}"
            arcade.draw_text(action_text, 10, y - 50, arcade.color.YELLOW, 12)
        
        # Draw highlighted tiles
        self._draw_highlighted_tiles()
        
        # Draw enemy info
        y = self.height - 70
        x = self.width - 250
        arcade.draw_text("ENEMIES:", x, y, arcade.color.YELLOW, 12, bold=True)
        y -= 25
        
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy_text = f"{enemy.name} - HP: {enemy.hp}/{enemy.hp_max}"
                arcade.draw_text(enemy_text, x, y, arcade.color.WHITE, 11)
                y -= 20

    def _draw_highlighted_tiles(self):
        """Draw highlighted movement and attack range tiles."""
        if self.tactical_combat.current_turn != "player" or not self.highlighted_tiles:
            return
        
        for tile_x, tile_y in self.highlighted_tiles:
            pixel_x, pixel_y = self.map.pixel_to_grid(tile_x, tile_y)
            
            # Draw semi-transparent tile
            if self.selected_action == "move":
                color = arcade.color.BLUE
                alpha = 100
            else:  # attack
                color = arcade.color.RED
                alpha = 100
            
            # Draw dotted outline tile
            left = pixel_x - self.map.tile_width / 2 + 1
            right = pixel_x + self.map.tile_width / 2 - 1
            bottom = pixel_y - self.map.tile_height / 2 + 1
            top = pixel_y + self.map.tile_height / 2 - 1
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
        
        # Place player at random position
        pos = self.exploration.random_character_position()
        self.map.move_character(self.player, pos[0], pos[1])

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
        """Handle victory and transition to next phase."""
        # Calculate XP rewards
        total_xp = sum(100 for enemy in self.enemies if not enemy.is_alive())
        self.xp_system.gain_xp(self.player, total_xp)
        
        # Reset for next exploration
        self.phase = "exploration"
        self.tactical_combat = None
        self.selected_action = None
        self.highlighted_tiles = set()
        
        # Clear enemies
        for enemy in self.enemies:
            old_pos = enemy.position
            if old_pos in self.map.entities:
                del self.map.entities[old_pos]
        self.enemies = []

    def _end_combat_defeat(self):
        """Handle defeat."""
        # Game over - for now, restart
        print("Game Over! Defeat!")
        # Reset player HP
        self.player.hp = self.player.hp_max
        self.phase = "exploration"
        self.tactical_combat = None
        self.selected_action = None
        self.highlighted_tiles = set()
        
        # Clear enemies
        for enemy in self.enemies:
            old_pos = enemy.position
            if old_pos in self.map.entities:
                del self.map.entities[old_pos]
        self.enemies = []

    def _draw_menu(self):
        arcade.draw_text("Tactical RPG", self.width / 2, self.height - 120, arcade.color.WHITE, 36, anchor_x="center")
        arcade.draw_text("Press [ENTER] to Start", self.width / 2, self.height - 180, arcade.color.AZURE, 22, anchor_x="center")
        arcade.draw_text("Press [ESCAPE] to Quit", self.width / 2, self.height - 220, arcade.color.ORANGE, 20, anchor_x="center")
        arcade.draw_text("Controls: M=Move, A=Attack, E=End Turn", self.width / 2, self.height - 270, arcade.color.LIGHT_GRAY, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        """Handle key press events."""
        if key == arcade.key.ESCAPE:
            self.close()
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
                
                # Process enemy turns
                self._process_all_enemy_turns()
    
    def _process_all_enemy_turns(self):
        """Process all enemy turns until player turn returns."""
        while self.tactical_combat.current_turn == "enemy":
            self.tactical_combat.process_enemy_turn()
    
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
        grid_x, grid_y = self.map.grid_to_pixel(x, y)
        
        if self.selected_action == "move":
            if self.tactical_combat.player_move(grid_x, grid_y):
                self.selected_action = None
                self.highlighted_tiles = set()
        
        elif self.selected_action == "attack":
            result = self.tactical_combat.player_attack(grid_x, grid_y)
            if result["success"]:
                self.selected_action = None
                self.highlighted_tiles = set()
            
        self.in_combat = False
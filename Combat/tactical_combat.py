import random
from collections import deque

class TacticalCombat:
    """Manages turn-based tactical combat with grid-based movement."""
    
    def __init__(self, player, enemies, game_map):
        """Initialize tactical combat.
        
        Args:
            player: The player character
            enemies: List of enemy characters
            game_map: The game map
        """
        self.player = player
        self.enemies = enemies
        self.game_map = game_map
        
        self.current_turn = "player"  # "player" or "enemy"
        self.enemy_turn_index = 0
        self.player_has_moved = False
        self.player_has_attacked = False
        self.player_has_healed = False
        
        # Movement, attack and heal ranges
        self.movement_range = 5  # Player can move up to 5 tiles per turn
        self.attack_range = 1  # Default attack range
        self.heal_amount = 10
        self.heal_uses = self.player.level * 4
        
    def get_movement_tiles(self):
        """Calculate all tiles within movement range from player position.
        
        Returns:
            set: Coordinates of tiles within movement range
        """
        if self.player_has_moved:
            return set()
            
        reachable = set()
        queue = deque([(self.player.position, 0)])
        visited = {self.player.position}
        
        while queue:
            (x, y), distance = queue.popleft()
            
            if distance <= self.movement_range:
                reachable.add((x, y))
            
            if distance < self.movement_range:
                for nx, ny in self.game_map.get_neighbors(x, y):
                    if (nx, ny) not in visited and not self.game_map.is_occupied(nx, ny):
                        visited.add((nx, ny))
                        queue.append(((nx, ny), distance + 1))
        
        return reachable
    
    def get_attack_tiles(self, from_position=None):
        """Calculate all tiles within attack range.
        
        Args:
            from_position: Position to calculate from (default: player position)
            
        Returns:
            set: Coordinates of tiles within attack range
        """
        if self.player_has_attacked:
            return set()
        
        position = from_position or self.player.position
        attackable = set()
        
        for x in range(position[0] - self.attack_range, position[0] + self.attack_range + 1):
            for y in range(position[1] - self.attack_range, position[1] + self.attack_range + 1):
                if self.game_map.is_walkable(x, y) and (x, y) != position:
                    attackable.add((x, y))
        
        return attackable
    
    def player_move(self, new_x, new_y):
        """Move the player to a new position.
        
        Args:
            new_x: New x coordinate
            new_y: New y coordinate
            
        Returns:
            bool: True if move was successful
        """
        if self.player_has_moved:
            return False
        
        movement_tiles = self.get_movement_tiles()
        if (new_x, new_y) not in movement_tiles:
            return False
        if self.game_map.is_occupied(new_x, new_y) and (new_x, new_y) != self.player.position:
            return False

        self.game_map.move_character(self.player, new_x, new_y)
        self.player_has_moved = True
        return True
    
    def player_attack(self, target_x, target_y):
        """Player attacks a target at the given position.
        
        Args:
            target_x: Target x coordinate
            target_y: Target y coordinate
            
        Returns:
            dict: Attack result with damage and target info
        """
        if self.player_has_attacked:
            return {"success": False, "reason": "Already attacked this turn"}
        
        attack_tiles = self.get_attack_tiles()
        if (target_x, target_y) not in attack_tiles:
            return {"success": False, "reason": "Target out of range"}
        
        # Find enemy at target position
        target = None
        for enemy in self.enemies:
            if enemy.position == (target_x, target_y) and enemy.is_alive():
                target = enemy
                break
        
        if not target:
            return {"success": False, "reason": "No valid target"}
        
        # Resolve attack
        damage = self._resolve_attack(self.player, target)
        self.player_has_attacked = True

        killed = False
        xp_gain = 0
        if not target.is_alive():
            killed = True
            xp_gain = 100
            if target.position in self.game_map.entities:
                del self.game_map.entities[target.position]

        return {
            "success": True,
            "target": target.name,
            "damage": damage,
            "target_hp": target.hp,
            "killed": killed,
            "xp_gain": xp_gain,
        }

    def player_heal(self):
        """Heal the player if heal uses remain.

        Returns:
            dict: Result with success and message.
        """
        if self.player_has_healed or self.player_has_attacked:
            return {"success": False, "reason": "Action already used this turn"}
        if self.heal_uses <= 0:
            return {"success": False, "reason": "No heal uses left"}
        if self.player.hp >= self.player.hp_max:
            return {"success": False, "reason": "HP already full"}

        self.player.heal_self(self.heal_amount)
        self.heal_uses -= 1
        self.player_has_healed = True
        return {"success": True, "amount": self.heal_amount, "current_hp": self.player.hp, "uses_left": self.heal_uses}

    def _resolve_attack(self, attacker, defender):
        """Calculate damage and apply it to defender.
        
        Args:
            attacker: Attacking character
            defender: Defending character
            
        Returns:
            int: Damage dealt
        """
        if not self._roll_hit(attacker, defender):
            return 0
        
        damage = self._calculate_damage(attacker, defender)
        
        if self._roll_crit(attacker, defender):
            damage *= 3
        
        defender.take_damage(damage)
        return damage
    
    def _roll_hit(self, attacker, defender):
        """Determine if attack hits.
        
        Args:
            attacker: Attacking character
            defender: Defending character
            
        Returns:
            bool: True if attack hits
        """
        hit_chance = 90 - 2 * (defender.speed - attacker.speed)
        hit_chance = max(10, min(95, hit_chance))
        return random.randint(1, 100) <= hit_chance
    
    def _roll_crit(self, attacker, defender):
        """Determine if attack is a critical hit.
        
        Args:
            attacker: Attacking character
            defender: Defending character
            
        Returns:
            bool: True if critical hit
        """
        crit_chance = 5 + (attacker.level - defender.level)
        crit_chance = max(0, min(40, crit_chance))
        return random.randint(1, 100) <= crit_chance
    
    def _calculate_damage(self, attacker, defender):
        """Calculate base damage.
        
        Args:
            attacker: Attacking character
            defender: Defending character
            
        Returns:
            int: Base damage
        """
        if attacker.attacks:
            base_damage = attacker.attacks[0].base_damage
        else:
            base_damage = 5
        
        raw_damage = base_damage + attacker.attack - defender.defense
        return max(1, raw_damage)
    
    def end_player_turn(self):
        """End the player's turn and start enemy turn."""
        self.current_turn = "enemy"
        self.enemy_turn_index = 0
        self.player_has_moved = False
        self.player_has_attacked = False
        self.player_has_healed = False
    
    def process_enemy_turn(self):
        """Process one enemy's turn and return action result.
        
        Returns:
            dict: Information about the enemy action taken
        """
        if self.enemy_turn_index >= len(self.enemies):
            self.current_turn = "player"
            self.player_has_moved = False
            self.player_has_attacked = False
            self.player_has_healed = False
            return {"type": "turn_end"}
        
        enemy = self.enemies[self.enemy_turn_index]
        
        if not enemy.is_alive():
            self.enemy_turn_index += 1
            return self.process_enemy_turn()
        
        # Simple AI: move towards player or attack
        ex, ey = enemy.position
        px, py = self.player.position
        
        distance = abs(px - ex) + abs(py - ey)
        
        result = {"enemy": enemy.name}
        
        # Attack if in range
        if distance <= self.attack_range and self.player.is_alive():
            damage = self._resolve_attack(enemy, self.player)
            result.update({
                "type": "attack",
                "damage": damage,
                "target": "player",
                "player_hp": self.player.hp
            })
        else:
            # Move towards player
            if distance > 1:
                if abs(px - ex) > abs(py - ey):
                    new_x = ex + (1 if px > ex else -1)
                    new_y = ey
                else:
                    new_x = ex
                    new_y = ey + (1 if py > ey else -1)
                
                if self.game_map.is_walkable(new_x, new_y) and not self.game_map.is_occupied(new_x, new_y):
                    self.game_map.move_character(enemy, new_x, new_y)
                    result["type"] = "move"
                    result.update({"to": (new_x, new_y)})
                else:
                    result["type"] = "no_action"
            else:
                result["type"] = "no_action"
        
        self.enemy_turn_index += 1
        return result
    
    def check_combat_end(self):
        """Check if combat has ended.
        
        Returns:
            str: "victory", "defeat", or "ongoing"
        """
        if not self.player.is_alive():
            return "defeat"
        
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if not alive_enemies:
            return "victory"
        
        return "ongoing"

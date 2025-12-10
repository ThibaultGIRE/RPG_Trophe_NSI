class AIController:
    @staticmethod
    def get_best_move(enemy, players, game_map):
        """Determine the best move for an enemy character to approach the player.

        Args:
            enely (Personnage): The enemy character.
            player (Personnage): The player character.
        """
        target = AIController.get_best_target(enemy, players)

        if not target:
            return None
        
        if game_map.in_attack_range(enemy, target):
            return ("attack", target)
        
        move = AIController.move_towards(enemy, target, game_map) 
        return ("move", move)
    
    @staticmethod
    def get_best_target(enemy, players):
        """Select the best target player for the enemy to attack.

        Args:
            enemy (Personnage): The enemy character.
            players (list): List of player characters.
            """
        
        alive_players = [player for player in players if player.is_alive()]
        if not alive_players:
            return None
        return min(alive_players, key=lambda player: player.hp)
    
    @staticmethod
    def move_towards(enemy, target, game_map):
        """Calculate the next position for the enemy to move towards the target.

        Args:
            enemy (Personnage): The enemy character.
            target (Personnage): The target player character.
            game_map (Map): The game map.
        """
        ex, ey = enemy.position
        tx, ty = target.position

        if abs(tx - ex) > abs(ty - ey):
            new_x = ex + (1 if tx > ex else -1)
            new_y = ey
        else:
            new_x = ex 
            new_y = ey +(1 if ty > ey else -1)

        if game_map.is_walkable(new_x, new_y):
            return (new_x, new_y)
        
        return enemy.position
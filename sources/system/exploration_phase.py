import random

class ExplorationPhase:
    """Manages the exploration phase where the character moves between combats."""
    
    def __init__(self, game_map, player):
        """Initialize exploration phase.
        
        Args:
            game_map: The game map
            player: The player character
        """
        self.game_map = game_map
        self.player = player
        self.action_log = []
        self.exploration_complete = False
        self.timer = 0
        
    def start_exploration(self):
        """Start a new exploration sequence."""
        self.action_log = []
        self.exploration_complete = False
        self.timer = 0
        self._generate_exploration_narrative()
    
    def _generate_exploration_narrative(self):
        """Generate random exploration narrative messages."""
        narratives = [
            "Exploration de la zone...",
            "A la recherche de nouvelles aventures...",
            "En train de chercher des ennemis...",
            "Vous pouvez utiliser les flèches directionelles au lieu de cliquer lors du déplacement ",
            "La station de soins permet de récupérer la moitié des potions manquantes",
            "N'oubliez pas de sauvegarder avant de quitter le jeu !",
        ]
        
        stats = [
            f"{self.player.name} a gagné de l'expérience.",
            f"{self.player.name} trouve des fournitures en chemin.",
            f"{self.player.name} se sent plus fort.",
        ]
        
        self.action_log.append(random.choice(narratives))
        self.action_log.append(random.choice(stats))
    
    def get_action_log(self):
        """Get the current action log.
        
        Returns:
            list: Log of actions taken during exploration
        """
        return self.action_log
    
    def update(self, delta_time):
        """Update exploration timer.
        
        Args:
            delta_time: Time elapsed since last frame
            
        Returns:
            bool: True if exploration should end
        """
        self.timer += delta_time
        
        # Exploration takes 3 seconds
        if self.timer >= 3.0:
            self.exploration_complete = True
            return True
        
        return False
    
    def random_character_position(self):
        """Randomly place character on the map.
        
        Returns:
            tuple: (x, y) position
        """
        while True:
            x = random.randint(2, self.game_map.width - 3)
            y = random.randint(2, self.game_map.height - 3)
            if self.game_map.is_walkable(x, y):
                return (x, y)

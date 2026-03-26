import arcade
from Entities.Character import Personnage

class Enemy(Personnage):
    def __init__(self, nom, niveau, pv, pv_max, attack, defense, speed, position, attacks, is_boss=False, move_range=4):
        super().__init__(nom, niveau, pv, pv_max, attack, defense, speed, position, attacks)
        self.xp_reward = 50  # Default XP reward
        self.is_boss = is_boss
        self.move_range = move_range
        self.color = arcade.color.PURPLE if is_boss else arcade.color.RED

    def decide_action(self, map, player):
        # let the class AiControler decide the action
        pass

    def choose_target(self, players):
        """Choose the player with the lowest hp

        Args:
            players (list): list of player characters

        Returns:
            bool: None if there's no player alive
            obj: player xith the lowest hp otherwise
        """
        alive_players = []

        for player in players:
            if player.is_alive():
                alive_players.append(player)

        if not alive_players:
            return None
        
        return min(alive_players, key = lambda player: player.hp)
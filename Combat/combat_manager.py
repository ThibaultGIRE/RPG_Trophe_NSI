import random

class CombatManager:
    def __init__(self, players, enemies):
        # game_map removed from constructor to match usage elsewhere
        self.players = players
        self.enemies = enemies
        self.turn_order = []
        self.current_turn_index = 0

    def start_turn(self):
        all_characters = self.players+ self.enemies
        self.turn_order = sorted(
            [c for c in all_characters if c.is_alive()], #c est un Character
            key = lambda c: c.speed,
            reverse = True
        )

    def perform_action(self, character, action, target):
        if action == "attack" and target:
            damage = self.resolve_attack(character, target, character.attacks[0])
            
            # Double attaque ?
            if character.can_double_attack(target):
                damage += self.resolve_attack(character, target, character.attacks[0])

    def roll_hit(self, attacker, defender):
        #entre 10 et 95% de réussite
        hit_chance = 90 - 2 * (defender.speed - attacker.speed)
        hit_chance = max(10, min(95, hit_chance))  # entre 10% et 95%
        return random.randint(1, 100) <= hit_chance
    
    def roll_crit(self, attacker, defender):
        crit_chance = 5 + (attacker.level - defender.level)
        crit_chance = max(0, min(40, crit_chance)) #entre 0 et 40% de chance
        return random.randint(1, 100) <= crit_chance
            
    def resolve_attack(self, attacker, defender, attack):
        if not self.roll_hit(attacker, defender):
            return 0 #esquivée
        
        damage = attack.calculate_damage(attacker, defender)

        if self.roll_crit(attacker, defender):
            damage *= 3 #coup critique réussi

        defender.take_damage(damage)
        return damage
    
    def check_end_conditions(self):
        if all(not enemy.is_alive() for enemy in self.enemies):
            return "victory"
        elif all(not player.is_alive() for player in self.players):
            return "defeat"
        return "ongoing"
            
        

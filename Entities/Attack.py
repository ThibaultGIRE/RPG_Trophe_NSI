class Attack:
    def __init__(self, name, precision, special_effect, base_damage):
        self.name = name
        self.precision = precision
        self.special_effect = special_effect
        self.base_damage = base_damage

    def calculate_damage(self, attacker, target):
        raw_damage = self.base_damage + attacker.attack - target.defense
        return max(1, raw_damage)
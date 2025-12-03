class Attack:
    def __init__(self, name, precision, special_effect, base_damage):
        self.name = name
        self.precision = precision
        self.special_effect = special_effect
        self.base_damage = base_damage

    def calculate_damage(self, enemy, target):
        pass
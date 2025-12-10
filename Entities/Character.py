from Entities.Attack import Attack

class Personnage:
    def __init__(self, name,level, hp, hp_max, attack, defense, speed, position, attacks):
        '''Initialize a Charadter instance.

        Args:
            name (str): character's name
            level (int): current level
            hp (int): current health points
            hp_max (int): maximum health point
            attack (int): stat for attack power
            defense (int): stat for defense power
            speed (int): stat for speed
            position (tuple): character's positon as (x, y)
            attacks (list): list of Attack objects
        '''
        self.name = name
        self.level = level
        self.xp = 0
        self.hp = hp
        self.hp_max = hp_max
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.position = position #tuple (x,y)
        self.attacks = attacks #liste 

    def move(self, dx, dy):
        """move the character

        Args:
            dx (int): number of step in x direction
            dy (int): number of step in y direction
        """
        x, y = self.position
        self.position = (x + dx, y + dy)

    def take_damage(self, damage):
        """Take of damage to the character's hp

        Args:
            damage (int): number of damage to take of the character's hp
        """
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        """Heal the character 

        Args:
            amount (int): amount of hp to heal
        """
        self.hp += amount
        if self.hp > self.hp_max:
            self.hp = self.hp_max
    
    def is_alive(self):
        """Check if the character is alive

        Returns:
            bool: True if the character is alive, False otherwise
        """
        return self.hp > 0
    
    def do_attack(self, target, attack_obj):
        """Perform an attack on a target character

        Args:
            target (_type_): _description_
            attack_obj (_type_): _description_
        """
        pass  # À implémenter

    def is_in_range(self, target, attack_obj):
        """Check if the target is in range of the attack

        Args:
            target (obj): target character
            attack_obj (obj): attack object

        Returns:
            bool: True if the target is in range, False otherwise
        """
        distance = abs(self.position[0] - target.position[0]) +abs(self.position[1] - target.position[1])
        return distance <= attack_obj.range
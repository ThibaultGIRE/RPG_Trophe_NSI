from Entities.Attack import Attack

class Personnage:
    def __init__(self, nom, points_de_vie, niveau, pv, pv_max, attack, defense, speed, position, attacks):
        '''Initialisation du personnage. Notes : position est un tuple (x,y) et attacks est une liste. Différencier attacks de attack'''
        self.nom = nom
        self.points_de_vie = points_de_vie
        self.niveau = niveau
        self.xp = 0
        self.pv = pv
        self.pv_max = pv_max
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.position = position #tuple (x,y)
        self.attacks = attacks #liste 

    def move(self, dx, dy):
        '''Déplace le personnage de dx en x et dy en y'''
        x, y = self.position
        self.position = (x + dx, y + dy)

    def take_damage(self, damage):
        '''Réduit les points de vie du personnage en fonction des dégâts reçus'''
        self.points_de_vie -= damage
        if self.points_de_vie < 0:
            self.points_de_vie = 0

    def heal(self, amount):
        '''Soigne le personnage d'une certaine quantité'''
        self.points_de_vie += amount
        if self.points_de_vie > self.pv_max:
            self.points_de_vie = self.pv_max
    
    def is_alive(self):
        '''Retourne True si le personnage est en vie, False sinon'''
        return self.points_de_vie > 0
    
    def do_attack(self, target, attack_obj):
        '''Faire une attaque'''
        pass  # À implémenter

    def is_in_range(self, target, attack_obj):
        '''Vérifie si la cible est dans la portée de l'attaque'''
        distance = abs(self.position[0] - target.position[0]) +abs(self.position[1] - target.position[1])
        return distance <= attack_obj.range
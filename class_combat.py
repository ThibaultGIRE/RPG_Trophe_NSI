DEGATS_NORMAUX = 10
DEGATS_SPECIAUX = 25

class Combat:
    def __init__(self, attaquant, defenseur):
        self.attaquant = attaquant
        self.defenseur = defenseur

    def attaquer(self):
        attaque = Attaque()
        if self.attaquant.points_de_vie <= 0:
            print(f"{self.attaquant.nom} ne peut pas attaquer car il est KO.")
        
        if self.type_attaque == 'normale':
            attaque.attaque_normale(self.defenseur)

        if self.type_attaque == 'speciale':
            attaque.attaque_speciale(self.defenseur)

class Attaque:
    def __init__(self):
        self.type_attaque = input("Entrez le type d'attaque (normale/speciale) : ").strip().lower()
        self.degats = None

    def definir_type_attaque(self):
        if self.type_attaque not in ['normale', 'speciale']:
            raise ValueError("Type d'attaque invalide. Choisissez normale ou speciale")
        
        elif self.type_attaque == 'normale':
            self.type_attaque = 'normale'

        elif self.type_attaque == 'speciale':
            self.type_attaqie = 'speciale'

    def definir_degats(self):
        if self.type_attaque == 'normale':
            self.degats = DEGATS_NORMAUX
        elif self.type_attaque == 'speciale':
            self.degats = DEGATS_SPECIAUX

    def attaque_normale(self, cible):
        cible.points_de_vie -= self.degats
        print(f"Attaque normale inflige {self.degats} points de dégâts à {cible.nom}")

    def attaque_speciale(self, cible):
        cible.points_de_vie -= DEGATS_SPECIAUX
        print(f"Attaque spéciale inflige {DEGATS_SPECIAUX} points de dégâts à {cible.nom}")
    
class Personnage:
    def __init__(self, nom, points_de_vie):
        self.nom = nom
        self.points_de_vie = points_de_vie
    
class Heros(Personnage):
    def __init__(self, nom, points_de_vie):
        super().__init__(nom, points_de_vie)

        self.niveau = 1
        self.experience = 0

class Monstre(Personnage):
    def __init__(self, nom, points_de_vie):
        super().__init__(nom, points_de_vie)

        self.nombre_experience = None
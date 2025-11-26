DEGATS_NORMAUX = 10
DEGATS_SPECIAUX = 25

class Combat:
    def __init__(self, attaquant, defenseur):
        self.attaquant = attaquant
        self.defenseur = defenseur
        self.type_attaque = None
    
    def attaque_normale(self):
        self.defenseur.points_de_vie -= DEGATS_NORMAUX
        print(f"{self.attaquant.nom} attaque {self.defenseur.nom} avec une attaque normale")

    def attaque_speciale(self):
        self.defenseur.points_de_vie -= DEGATS_SPECIAUX
        print(f"{self.attaquant.nom} attaque {self.defenseur.nom} avec une attaque spéciale")
        

    def attaquer(self):
        if self.attaquant.points_de_vie <= 0:
            print(f"{self.attaquant.nom} ne peut pas attaquer car il est KO.")
        
        if self.type_attaque == 'normale':
            self.attaque_normale()

        if self.type_attaque == 'speciale':
            self.attaque_speciale()

    def definir_type_attaque(self):
        choix = input("Choisissez le type d'attaque (normale/spéciale) : ").strip().lower()
        if choix in ['normale', 'spéciale']:
            self.type_attaque = choix
        return self.type_attaque
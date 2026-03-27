# 🎮 RPG Tactique - Protocole d'Utilisation

## 📋 Table des matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Lancement du jeu](#lancement-du-jeu)
- [Contrôles](#contrôles)
- [Mécaniques de jeu](#mécaniques-de-jeu)
- [Sauvegarde et chargement](#sauvegarde-et-chargement)

## 🔧 Prérequis

- Python 3.8 ou supérieur
- Pip (gestionnaire de paquets Python)

## 📦 Installation

### Étape 1 : Cloner le repository

```bash
git clone https://github.com/ThibaultGIRE/RPG_Trophe_NSI.git
cd RPG_Trophe_NSI
```

### Étape 2 : Créer un environnement virtuel (recommandé)

```bash
python -m venv .venv
```

### Étape 3 : Activer l'environnement virtuel

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### Étape 4 : Installer les dépendances

```bash
pip install -r Requirements.txt
```

Ou installez manuellement :
```bash
pip install arcade
```

## 🚀 Lancement du jeu

### Depuis le code source

```bash
cd sources
python main.py
```

### Depuis l'exécutable

Si vous disposez de l'exécutable `Jeu_RPG_Tactique.exe`, double-cliquez simplement dessus ou lancez-le depuis le terminal :

```bash
dist/Jeu_RPG_Tactique.exe
```

## 🎮 Contrôles

### Phase de menu principal

| Touche | Action |
|--------|--------|
| `ENTRÉE` | Démarrer une nouvelle partie |
| `L` | Accéder au menu de chargement |
| `ÉCHAP` | Quitter le jeu |

### Menu de chargement

| Touche | Action |
|--------|--------|
| `1`, `2`, `3` | Charger la sauvegarde correspondante |
| `N` | Nouvelle partie |
| `D` | Mode suppression de sauvegarde |
| `ÉCHAP` | Retour au menu principal |

### Contrôles en jeu

#### Phase d'exploration et combat

| Touche | Action |
|--------|--------|
| `M` | Sélectionner le mouvement |
| `A` | Sélectionner l'attaque |
| `H` | Utiliser une potion de soin |
| `E` | Finir le tour |
| `Flèches directionnelles` | Déplacer le curseur/héros |
| `Clic souris` | Sélectionner une case pour se déplacer ou attaquer |

#### Commandes générales

| Touche | Action |
|--------|--------|
| `S` | Sauvegarder la partie en cours |
| `L` | Charger une partie |
| `ÉCHAP` | Quitter le jeu |

## 🎯 Mécaniques de jeu

### Déroulement d'une partie

1. **Menu principal** : Choisissez de démarrer une nouvelle partie ou de charger une sauvegarde
2. **Phase d'exploration** : Déplacez votre héros sur la carte avec les flèches directionnelles
3. **Rencontre ennemie** : Des ennemis apparaissent et le combat commence
4. **Tour du joueur** :
   - Sélectionnez le mode Mouvement (`M`) et cliquez sur une case accessible (vert)
   - Sélectionnez le mode Attaque (`A`) et cliquez sur un ennemi à portée (rouge)
   - Utilisez une potion (`H`) si nécessaire
   - Terminez votre tour (`E`)
5. **Tour ennemi** : Les ennemis se déplacent vers vous et attaquent si à portée
6. **Victoire** : Tuez tous les ennemis pour gagner de l'expérience
7. **Progression** : Gagnez des niveaux pour augmenter vos statistiques

### Système de combat

- **Mouvement** : 5 cases maximum par tour
- **Attaque** : 1 attaque par tour
- **Précision** : Dépend de la vitesse de l'attaquant vs le défenseur
- **Critique** : Chance de coup critique augmentée avec le niveau
- **Dégâts** : Calculés avec la formule : `base_damage + attack - defense`

### Légende des icônes

- 🔴 **Cercle rouge** : Ennemi normal
- 🟣 **Cercle violet** : Boss (ennemi plus puissant)
- ⬜ **Carré gris** : Obstacle (impassable)
- 🟢 **Cercle vert** : Station de soin (restaure les potions)
- 🟦 **Carré bleu** : Héros (personnage jouable)
- 🟩 **Cases vertes** : Cases accessibles pour le mouvement
- 🟥 **Cases rouges** : Cases attaquables

## 💾 Sauvegarde et chargement

### Sauvegarder une partie

1. Appuyez sur `S` pendant le jeu (exploration ou combat)
2. Sélectionnez l'emplacement (1, 2 ou 3) avec les touches numériques
3. Confirmez la sauvegarde
4. Un message de confirmation apparaît

### Charger une partie

1. Au menu principal, appuyez sur `L`
2. Sélectionnez l'emplacement souhaité (1, 2 ou 3)
3. La partie se charge automatiquement

### Supprimer une sauvegarde

1. Dans le menu de chargement, appuyez sur `D`
2. Sélectionnez l'emplacement à supprimer (1, 2 ou 3)
3. Confirmez la suppression

## 📊 Interface

### Panneau d'information (en haut à gauche)

- **Nom du personnage**
- **Niveau** et **XP**
- **PV** (Points de Vie) actuels/max
- **Statistiques** : Attaque, Défense, Vitesse
- **Potions de soin** restantes

### Bannière de tour (en haut au centre)

- Affiche le tour actuel (Joueur ou Ennemi)
- Transition visuelle entre les tours

### Panneau de combat (en bas)

- Messages de combat (dégâts infligés, coups critiques, etc.)
- Instructions en fonction du mode actuel (Mouvement/Attaque)

## ⚠️ Résolution des problèmes

### Le jeu ne se lance pas

1. Vérifiez que Python 3.8+ est installé : `python --version`
2. Vérifiez que arcade est installé : `pip list | findstr arcade`
3. Réinstallez les dépendances : `pip install -r Requirements.txt`

### Erreur d'importation

Assurez-vous d'être dans le dossier `sources/` avant de lancer `python main.py`

### Problèmes d'affichage

- Vérifiez que vos pilotes graphiques sont à jour
- Assurez-vous que votre résolution d'écran est d'au moins 1280x720

## 📚 Documentation supplémentaire

Pour plus d'informations sur le projet :
- **Presentation.md** : Description détaillée du projet et de son architecture
- **Licence.txt** : Conditions d'utilisation et de redistribution

## 👨‍💻 Support

Pour toute question ou problème, n'hésitez pas à contacter les développeurs :

- Thibault GIRARD-REYDET
- Julie GANIER JOSSE
- Nathan KETTERER

---

**Bon jeu ! 🎮**
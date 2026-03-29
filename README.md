# 🎮 RPG Tactique - Combat au Tour par Tour

Un jeu de rôle tactique développé en Python utilisant la bibliothèque Arcade, avec un système de combat au tour par tour sur grille, une progression des personnages et des ennemis avec intelligence artificielle.

## 👨‍💻 Auteurs

- Thibault GIRARD-REYDET
- Julie GANIER JOSSE
- Nathan KETTERER

## 🔧 Installation / Prérequis

### Prérequis

- **Python 3.8 ou supérieur**

### Bibliothèques nécessaires

- `arcade>=2.6.0`

### Commande d'installation

```bash
pip install -r Requirements.txt
```

Ou installez manuellement :

```bash
pip install arcade
```

## 🚀 Utilisation

### Lancer le programme

Depuis le code source :

```bash
cd sources
python main.py
```

### Touches de contrôle

#### Phase de menu principal

| Touche | Action |
|--------|--------|
| `ENTRÉE` | Démarrer une nouvelle partie |
| `L` | Accéder au menu de chargement |
| `ÉCHAP` | Quitter le jeu |

#### Menu de chargement

| Touche | Action |
|--------|--------|
| `1`, `2`, `3` | Charger la sauvegarde correspondante |
| `N` | Nouvelle partie |
| `D` | Mode suppression de sauvegarde |
| `ÉCHAP` | Retour au menu principal |

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

## 📁 Structure du dépôt

```
RPG_Trophe_NSI/
├── Presentation.md         # Description technique du projet
├── README.md               # Protocole d'utilisation (ce fichier)
├── Licence.txt             # Licence du projet
├── Requirements.txt         # Dépendances Python
├── sources/                # Code source du jeu
│   ├── main.py             # Point d'entrée
│   ├── game.py             # Classe principale Game
│   ├── Combat/             # Système de combat
│   │   ├── tactical_combat.py
│   │   ├── combat_manager.py
│   │   └── action_manager.py
│   ├── Entities/           # Entités du jeu
│   │   ├── Character.py
│   │   ├── Player_character.py
│   │   ├── Ennemy.py
│   │   └── Attack.py
│   ├── Map/                # Système de carte
│   │   └── game_map.py
│   ├── system/             # Systèmes du jeu
│   │   ├── ai_controller.py
│   │   ├── enemy_spawner.py
│   │   ├── xp_system.py
│   │   └── exploration_phase.py
│   └── saves/              # Dossier des sauvegardes
│       ├── save_slot_1.json
│       ├── save_slot_2.json
│       └── save_slot_3.json
└── build/                  # Fichiers de compilation (optionnel)
```

## 📚 Documentation supplémentaire

Pour une description détaillée du projet, de son architecture et des choix techniques, consultez **Presentation.md**.

---

**Bon jeu ! 🎮**
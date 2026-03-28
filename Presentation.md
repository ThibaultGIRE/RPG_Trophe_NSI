# 🎮 RPG Tactique - Combat au Tour par Tour

Un jeu de rôle tactique développé en Python utilisant la bibliothèque Arcade, avec un système de combat au tour par tour sur grille, une progression des personnages et des ennemis avec intelligence artificielle.

## 📋 Description du projet

Ce projet est un jeu de rôle tactique inspiré des classiques du genre comme Fire Emblem ou Final Fantasy Tactics. Le joueur contrôle un héros qui explore une carte, combat des ennemis, gagne de l'expérience et progresse en niveaux.

### Aspects techniques majeurs

Le projet intègre plusieurs systèmes complexes qui ont bénéficié d'une assistance IA pour leur développement et leur optimisation :

1. **Système de combat tactique** : Gestion des tours, calculs de dégâts, système de mouvement sur grille
2. **Intelligence artificielle des ennemis** : Pathfinding, prise de décision tactique
3. **Système de sauvegarde/chargement** : Persistance des données avec JSON
4. **Génération procédurale de cartes** : Placement aléatoire d'obstacles et de points d'intérêt
5. **Interface utilisateur complexe** : Panneaux d'information, indicateurs visuels, menus

## ✨ Fonctionnalités

### Gameplay
- 🗺️ **Exploration** : Phase d'exploration avant chaque combat
- ⚔️ **Combat tactique** : Système au tour par tour avec grille
- 📈 **Progression** : Système d'expérience et de niveaux
- 💾 **Sauvegarde** : 3 emplacements de sauvegarde avec suppression
- 🧪 **Soin** : Stations de soin et potions de soin limitées

### Combat
- 🎯 **Mouvement stratégique** : Déplacement sur 5 cases par tour
- 💥 **Attaques variées** : Attaques de mêlée avec précision et critique
- 🤖 **IA ennemie** : Les ennemis poursuivent et attaquent intelligemment
- 🏆 **Boss** : Ennemis plus puissants avec statistiques augmentées

### Interface
- 📊 **Panneaux d'information** : Stats en temps réel du héros
- 🎨 **Indicateurs visuels** : Surbrillance des cases accessibles
- 📋 **Menus de sauvegarde/chargement** : Interface intuitive
- 🖼️ **Bannières de tour** : Affichage des transitions de tour

## 🏗️ Architecture du projet

```
RPG_Trophe_NSI/
├── Presentation.md         # Description du projet
├── README.md               # Protocole d'utilisation
├── Licence.txt             # Licence du projet
├── Requirements.txt         # Dépendances
├── sources/                # Code source
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
```

## 🤖 Contribution de l'IA au développement

Ce projet a bénéficié d'une assistance par intelligence artificielle pour plusieurs aspects complexes de son développement. L'IA a servi de catalyseur pour résoudre des problèmes algorithmiques et architecturaux, permettant une implémentation plus rapide et robuste.

### 1. Système de Pathfinding et de Mouvement

**Défi** : Implémenter un système de mouvement efficace sur grille avec gestion des obstacles et calcul de portée.

**Solution IA** :
- **Algorithme BFS (Breadth-First Search)** : Implémentation d'un parcours en largeur pour calculer les cases accessibles dans un rayon de mouvement donné
- **Optimisation de la file d'attente** : Utilisation de `collections.deque` pour une gestion efficace des positions à explorer
- **Gestion des états visités** : Éviter les boucles infinies et recalculs inutiles

```python
# Exemple dans tactical_combat.py - get_movement_tiles()
queue = deque([(self.player.position, 0)])
visited = {self.player.position}

while queue:
    (x, y), distance = queue.popleft()
    if distance <= self.movement_range:
        reachable.add((x, y))
    if distance < self.movement_range:
        for nx, ny in self.game_map.get_neighbors(x, y):
            if (nx, ny) not in visited and not self.game_map.is_occupied(nx, ny):
                visited.add((nx, ny))
                queue.append(((nx, ny), distance + 1))
```

**Complexité algorithmique** : O(n²) où n est le rayon de mouvement

### 2. Intelligence Artificielle des Ennemis

**Défi** : Créer une IA d'ennemis capable de prendre des décisions tactiques (poursuite, attaque, évitement).

**Solution IA** :
- **Heuristique de distance** : Priorisation des cibles les plus faibles en points de vie
- **Algorithme de poursuite** : Mouvement en direction du joueur avec gestion des obstacles
- **Arbre de décision simple** : Attaquer si à portée, sinon se rapprocher

```python
# Exemple dans ai_controller.py
@staticmethod
def get_best_target(enemy, players):
    """Sélectionne la cible optimale (plus faible)"""
    alive_players = [player for player in players if player.is_alive()]
    if not alive_players:
        return None
    return min(alive_players, key=lambda player: player.hp)

@staticmethod
def move_towards(enemy, target, game_map):
    """Calcul le mouvement optimal vers la cible"""
    ex, ey = enemy.position
    tx, ty = target.position

    if abs(tx - ex) > abs(ty - ey):
        new_x = ex + (1 if tx > ex else -1)
        new_y = ey
    else:
        new_x = ex
        new_y = ey + (1 if ty > ey else -1)

    if game_map.is_walkable(new_x, new_y):
        return (new_x, new_y)
    return enemy.position
```

### 3. Système de Calcul de Dégâts

**Défi** : Implémenter un système de combat équilibré avec précision, critique et dégâts variables.

**Solution IA** :
- **Formules probabilistes** : Calcul de chances de toucher et de critique basées sur les statistiques
- **Système de RNG** : Utilisation de générateurs aléatoires pour la variabilité
- **Équilibrage mathématique** : Formules de dégâts avec plafonds et planchers

```python
# Exemple dans tactical_combat.py
def _roll_hit(self, attacker, defender):
    """Calcule si l'attaque touche"""
    hit_chance = 90 - 2 * (defender.speed - attacker.speed)
    hit_chance = max(10, min(95, hit_chance))
    return random.randint(1, 100) <= hit_chance

def _roll_crit(self, attacker, defender):
    """Calcule si c'est un coup critique"""
    crit_chance = 5 + (attacker.level - defender.level)
    crit_chance = max(0, min(40, crit_chance))
    return random.randint(1, 100) <= crit_chance

def _calculate_damage(self, attacker, defender):
    """Calcule les dégâts de base"""
    base_damage = attacker.attacks[0].base_damage if attacker.attacks else 5
    raw_damage = base_damage + attacker.attack - defender.defense
    return max(1, raw_damage)
```

### 4. Gestion d'État Complexes

**Défi** : Gérer les transitions entre différentes phases du jeu (menu, exploration, combat, sauvegarde) avec préservation de l'état.

**Solution IA** :
- **Machine à états** : Implémentation claire des transitions entre phases
- **Pattern Observer** : Système de notifications pour les changements d'état
- **Gestion de l'historique** : Sauvegarde de la phase précédente pour les menus

```python
# Exemple dans game.py
self.phase = "menu"  # États possibles: "menu", "exploration", "combat", "load_menu", "save_menu", "victory", "defeat"
self.previous_phase = "exploration"

def on_key_press(self, key, modifiers):
    if key == arcade.key.S and self.phase in ["exploration", "combat"]:
        self.previous_phase = self.phase  # Sauvegarde de l'état
        self.phase = "save_menu"
```

### 5. Système de Rendu Adaptatif

**Défi** : Adapter l'affichage de la carte à différentes résolutions d'écran tout en maintenant la proportion.

**Solution IA** :
- **Calcul d'échelle automatique** : Détermination du facteur de zoom optimal
- **Centrage dynamique** : Calcul automatique des offsets pour centrer la carte
- **Gestion de l'espace** : Répartition intelligente de l'espace entre la carte et l'UI

```python
# Exemple dans game_map.py - get_draw_info()
scale_x = draw_width / (self.width * self.tile_width)
scale_y = draw_height / (total_rows * self.tile_height)
scale = min(scale_x, scale_y)  # Conserver le ratio d'aspect

tile_w = self.tile_width * scale
tile_h = self.tile_height * scale

# Centrage de la carte dans l'espace disponible
offset_x = origin_x + (draw_width - total_width) / 2
offset_y = origin_y + (draw_height - total_height) / 2
```

### 6. Système de Sauvegarde Robuste

**Défi** : Implémenter un système de sauvegarde/chargement fiable avec gestion des erreurs et validation.

**Solution IA** :
- **Sérialisation JSON** : Utilisation de JSON pour la persistance des données
- **Gestion d'erreurs** : Try/except pour les opérations de fichier
- **Validation de données** : Vérification de l'intégrité des sauvegardes
- **Fallbacks** : Valeurs par défaut en cas de données manquantes

```python
# Exemple dans game.py
def save_game(self, slot):
    save_data = {
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "player": {
            "name": self.player.name,
            "level": self.player.level,
            # ... autres statistiques
        },
    }
    try:
        with open(slot_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        self.save_message = f"Erreur lors de la sauvegarde: {e}"
```

### 7. Génération Procédurale de Carte

**Défi** : Générer des cartes jouables avec obstacles et points d'intérêt de manière aléatoire mais cohérente.

**Solution IA** :
- **Algorithme de placement aléatoire** : Génération d'obstacles avec vérification de collision
- **Heuristique de validité** : Tentatives multiples avec fallback
- **Équilibrage de densité** : Contrôle du nombre d'obstacles par rapport à la taille de la carte

```python
# Exemple dans game_map.py
def _generate_obstacles(self, obstacle_count):
    for _ in range(obstacle_count):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        if (x, y) not in self.obstacles:  # Éviter les doublons
            self.obstacles.add((x, y))

def _generate_heal_station(self):
    """Génération avec fallback intelligent"""
    for _ in range(100):  # 100 tentatives
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        if (x, y) not in self.obstacles:
            self.heal_station = (x, y)
            return
    # Fallback: centre de la carte
    self.heal_station = (self.width // 2, self.height // 2)
```

### Bénéfices de l'Assistance IA

1. **Rapidité de développement** : Les algorithmes complexes ont été implémentés plus rapidement avec des patterns éprouvés
2. **Robustesse** : Les solutions proposées incluent souvent la gestion des cas limites et des erreurs
3. **Optimisation** : Utilisation de structures de données et d'algorithmes optimaux (deque, BFS, etc.)
4. **Maintenabilité** : Code structuré et documenté, facilitant les futures modifications
5. **Apprentissage** : L'assistance IA a permis d'explorer des approches algorithmiques avancées

### Approche Collaborative

L'IA a servi de **guide et d'assistant** plutôt que de remplaçant :

- ✅ **Génération de code initial** pour les algorithmes complexes
- ✅ **Suggestions d'optimisation** et de refactoring
- ✅ **Documentation et explications** des concepts algorithmiques
- ✅ **Débogage assisté** pour identifier les problèmes logiques
- ❌ **Non** : Remplacement total du développement humain
- ❌ **Non** : Décisions de design sans validation humaine

Le développeur reste au contrôle de l'architecture, des décisions de design et de la validation des fonctionnalités, l'IA servant à accélérer l'implémentation et à proposer des solutions optimisées.

## 📚 Structure du code

### Classes principales

#### `Game` (sources/game.py)
Classe principale gérant la fenêtre du jeu et les boucles de rendu.

#### `TacticalCombat` (sources/Combat/tactical_combat.py)
Gère le système de combat au tour par tour, les calculs de dégâts et l'IA des ennemis.

#### `GameMap` (sources/Map/game_map.py)
Gère la carte, le rendu, les obstacles et les entités.

#### `PlayerCharacter` (sources/Entities/Player_character.py)
Représente le personnage jouable avec ses statistiques et capacités.

#### `Enemy` (sources/Entities/Ennemy.py)
Représente les ennemis avec leur propre IA.

#### `AIController` (sources/system/ai_controller.py)
Contient la logique de décision pour les ennemis.

### Systèmes auxiliaires

- `XpSystem` : Gestion de l'expérience et des niveaux
- `Ennemy_Spawner` : Génération des vagues d'ennemis
- `ExplorationPhase` : Phase d'exploration pré-combat

## 🚀 Améliorations futures

- [ ] Ajout de plus de types d'ennemis
- [ ] Système d'équipement et d'objets
- [ ] Plusieurs classes de personnages jouables
- [ ] Cartes plus grandes et plus variées
- [ ] Mode multijoueur
- [ ] Effets visuels améliorés
- [ ] Son et musique
- [ ] Système de quêtes

## 📝 Notes de développement

Ce projet a été développé dans le cadre du Trophée NSI (Numérique et Sciences Informatiques). Il démontre l'application de concepts avancés de programmation :

- Programmation orientée objet
- Algorithmes et structures de données
- Intelligence artificielle basique
- Gestion d'état et événements
- Persistance des données
- Interface graphique

## 👨‍💻 Auteurs

Développé par Thibault GIRARD-REYDET, Julie GANIER JOSSE et Nathan KETTERER avec l'assistance d'intelligence artificielle pour les aspects algorithmiques complexes.

---

**Note importante** : L'assistance IA utilisée dans ce projet sert de support technique et pédagogique, permettant de surmonter les défis algorithmiques tout en apprenant les concepts fondamentaux de la programmation de jeux vidéo.
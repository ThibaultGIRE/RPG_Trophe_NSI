# 🎮 RPG Tactique - Combat au Tour par Tour

Un jeu de rôle tactique développé en Python utilisant la bibliothèque Arcade, avec un système de combat au tour par tour sur grille, une progression des personnages et des ennemis avec intelligence artificielle.

## 📋 Description du projet

Ce projet est un jeu de rôle tactique inspiré des classiques du genre comme Fire Emblem ou Final Fantasy Tactics. Le joueur contrôle un héros qui explore une carte, combat des ennemis, gagne de l'expérience et progresse en niveaux.

**Objectif du projet :** Créer un jeu tactique complet avec une interface graphique fluide, un système de combat équilibré et une intelligence artificielle compétitive, tout en démontrant la maîtrise de concepts avancés de programmation (POO, algorithmes, structures de données).

## 👥 Répartition du travail

Le développement du projet a été réparti entre les trois membres de l'équipe selon leurs compétences et intérêts :

### Thibault GIRARD-REYDET
- **Gestion des sauvegarde** : Implémentation du système de persistance avec JSON, gestion des 3 slots de sauvegarde, interface de sauvegarde/chargement
- **Interface graphique** : Conception et implémentation de l'interface utilisateur, panneaux d'information, indicateurs visuels, menus interactifs, bannières de transition

### Nathan KETTERER
- **Système de niveau** : Création du système d'expérience et de progression, calcul des statistiques par niveau, équilibrage des courbes de progression
- **Spawn des mobs** : Implémentation du générateur d'ennemis, gestion des vagues, création des boss, algorithme de placement des ennemis
- **Évolution de l'XP** : Formules de calcul d'expérience, récompenses de victoire, gestion de la progression du joueur

### Julie GANIER JOSSE
- **Intelligence Artificielle** : Développement de l'IA des ennemis, implémentation du pathfinding, heuristiques de décision, algorithmes de poursuite et d'attaque
- **Génération de la carte** : Création procédurale des cartes, placement aléatoire des obstacles, génération des stations de soin, algorithme de validité des positions

### Collaboration
Bien que chaque membre ait eu des responsabilités principales, le développement a été collaborative avec :
- Revues de code régulières entre les membres
- Intégration et tests des différents systèmes
- Résolution conjointe des problèmes complexes
- Documentation partagée du code

## 🏗️ Architecture logicielle

### Structures de données

Le projet utilise plusieurs structures de données fondamentales :

1. **Listes** : Gestion des collections d'ennemis, attaques disponibles, statistiques
2. **Dictionnaires** : Sauvegarde/chargement des données, mapping des positions sur la carte
3. **Ensembles (Sets)** : Gestion des obstacles, cases visitées, positions occupées
4. **Tuples** : Représentation des positions (x, y), coordonnées sur la grille
5. **Files (deque)** : Algorithme BFS pour le pathfinding et le calcul de mouvement

### Algorithmes principaux

#### 1. Pathfinding et calcul de mouvement (BFS)

**Problème :** Calculer les cases accessibles dans un rayon de mouvement donné en évitant les obstacles.

**Solution :** Algorithme de parcours en largeur (Breadth-First Search)

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

**Complexité algorithmique :** O(n²) où n est le rayon de mouvement

#### 2. Intelligence Artificielle des ennemis

**Problème :** Créer une IA capable de prendre des décisions tactiques (poursuite, attaque, évitement).

**Solution :** Heuristique de distance + arbre de décision simple

```python
# Sélection de la cible optimale (plus faible en PV)
@staticmethod
def get_best_target(enemy, players):
    alive_players = [player for player in players if player.is_alive()]
    if not alive_players:
        return None
    return min(alive_players, key=lambda player: player.hp)

# Mouvement vers la cible avec gestion des obstacles
@staticmethod
def move_towards(enemy, target, game_map):
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

#### 3. Calcul de dégâts avec RNG

**Problème :** Implémenter un système de combat équilibré avec précision, critique et dégâts variables.

**Solution :** Formules probabilistes avec générateurs aléatoires

```python
# Calcul si l'attaque touche
def _roll_hit(self, attacker, defender):
    hit_chance = 90 - 2 * (defender.speed - attacker.speed)
    hit_chance = max(10, min(95, hit_chance))
    return random.randint(1, 100) <= hit_chance

# Calcul si c'est un coup critique
def _roll_crit(self, attacker, defender):
    crit_chance = 5 + (attacker.level - defender.level)
    crit_chance = max(0, min(40, crit_chance))
    return random.randint(1, 100) <= crit_chance

# Calcul des dégâts de base
def _calculate_damage(self, attacker, defender):
    base_damage = attacker.attacks[0].base_damage if attacker.attacks else 5
    raw_damage = base_damage + attacker.attack - defender.defense
    return max(1, raw_damage)
```

#### 4. Machine à états pour la gestion du jeu

**Problème :** Gérer les transitions entre différentes phases du jeu (menu, exploration, combat, sauvegarde) avec préservation de l'état.

**Solution :** Machine à états avec sauvegarde de l'état précédent

```python
# États possibles: "menu", "exploration", "combat", "load_menu", "save_menu", "victory", "defeat"
self.phase = "menu"
self.previous_phase = "exploration"

def on_key_press(self, key, modifiers):
    if key == arcade.key.S and self.phase in ["exploration", "combat"]:
        self.previous_phase = self.phase  # Sauvegarde de l'état
        self.phase = "save_menu"
```

#### 5. Génération procédurale de carte

**Problème :** Générer des cartes jouables avec obstacles et points d'intérêt de manière aléatoire mais cohérente.

**Solution :** Algorithme de placement aléatoire avec fallback intelligent

```python
# Génération d'obstacles
def _generate_obstacles(self, obstacle_count):
    for _ in range(obstacle_count):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        if (x, y) not in self.obstacles:
            self.obstacles.add((x, y))

# Génération avec fallback
def _generate_heal_station(self):
    for _ in range(100):  # 100 tentatives
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        if (x, y) not in self.obstacles:
            self.heal_station = (x, y)
            return
    # Fallback: centre de la carte
    self.heal_station = (self.width // 2, self.height // 2)
```

### Programmation Orientée Objet (POO)

Le projet utilise largement la POO avec une hiérarchie de classes claire :

#### Hiérarchie des classes

```
Character (classe abstraite)
├── PlayerCharacter
└── Enemy
```

#### Classes principales

1. **Game** (`sources/game.py`) : Classe principale gérant la fenêtre, les boucles de rendu et les événements
2. **TacticalCombat** (`sources/Combat/tactical_combat.py`) : Gère le système de combat au tour par tour
3. **GameMap** (`sources/Map/game_map.py`) : Gère la carte, le rendu, les obstacles et les entités
4. **Character** (`sources/Entities/Character.py`) : Classe de base pour les personnages
5. **PlayerCharacter** (`sources/Entities/Player_character.py`) : Spécialisation pour le héros
6. **Enemy** (`sources/Entities/Ennemy.py`) : Spécialisation pour les ennemis
7. **AIController** (`sources/system/ai_controller.py`) : Contient la logique de décision IA
8. **XpSystem** (`sources/system/xp_system.py`) : Gestion de l'expérience et des niveaux
9. **EnnemySpawner** (`sources/system/enemy_spawner.py`) : Génération des vagues d'ennemis

#### Principes POO appliqués

- **Encapsulation** : Attributs privés avec getters/setters
- **Héritage** : Character → PlayerCharacter et Enemy
- **Polymorphisme** : Méthodes redéfinies selon le type d'entité
- **Abstraction** : Classes abstraites pour définir des interfaces communes

## 💥 Difficultés rencontrées

### 1. Pathfinding sur grille avec obstacles

**Défi :** Implémenter un système de mouvement efficace permettant au joueur et à l'IA de se déplacer intelligemment sur une grille avec des obstacles.

**Problème initial :** Les premières implémentations utilisaient des itérations simples qui ne tenaient pas compte des obstacles, provoquant des déplacements impossibles et des bugs graphiques.

**Solution adoptée :** 
- Implémentation de l'algorithme BFS (Breadth-First Search)
- Utilisation d'un set pour les positions visitées afin d'éviter les boucles infinies
- Utilisation de `collections.deque` pour une gestion efficace de la file d'attente
- Séparation claire entre calcul de portée et affichage

**Ce qui a été appris :** L'importance de choisir le bon algorithme de pathfinding selon le contexte. BFS est optimal pour les graphes non pondérés comme une grille de mouvement.

### 2. Intelligence Artificielle des ennemis

**Défi :** Créer une IA d'ennemis capable de prendre des décisions tactiques crédibles sans être trop prévisible ni trop difficile.

**Problèmes rencontrés :**
- Les ennemis restaient bloqués derrière les obstacles
- L'IA attaquait systématiquement le joueur le plus proche, même s'il était trop puissant
- Les ennemis ne priorisaient pas les cases les plus stratégiques

**Solution adoptée :**
- Implémentation d'une heuristique de ciblage : attaquer le personnage avec le moins de PV
- Algorithme de poursuite simple mais efficace avec gestion des obstacles
- Arbre de décision : vérifier si attaque possible → sinon se rapprocher → sinon attendre
- Ajout d'une marge de randomisation pour éviter la prévisibilité totale

**Ce qui a été appris :** L'équilibre entre complexité et performance en IA. Une IA trop complexe peut rendre le jeu injouable, tandis qu'une IA trop simple le rend ennuyeux.

### 3. Gestion d'état complexe avec préservation

**Défi :** Gérer les nombreuses transitions entre phases du jeu (menu, exploration, combat, sauvegarde, chargement, victoire, défaite) tout en préservant l'état lors des interactions.

**Problèmes rencontrés :**
- Le jeu se figeait après être revenu d'un menu
- L'état du combat n'était pas préservé lors de la sauvegarde
- Les transitions entre phases créaient des bugs visuels et fonctionnels

**Solution adoptée :**
- Implémentation d'une machine à états avec sauvegarde de l'état précédent (`previous_phase`)
- Séparation claire des responsabilités entre phases
- Utilisation de flags pour gérer les transitions
- Tests approfondis de chaque transition possible

**Ce qui a été appris :** L'importance d'une architecture claire pour la gestion d'état. La machine à états permet de visualiser et de contrôler facilement les transitions.

### 4. Système de sauvegarde robuste

**Défi :** Implémenter un système de sauvegarde/chargement fiable capable de préserver tout l'état du jeu (position, statistiques, ennemis, phase).

**Problèmes rencontrés :**
- Les sauvegardes corrompues créaient des crashs du jeu
- Certaines données n'étaient pas sérialisables en JSON
- Le chargement ne restaure pas l'état exact (position des ennemis, phase de combat)

**Solution adoptée :**
- Utilisation de JSON pour la sérialisation (portabilité et lisibilité)
- Gestion d'erreurs avec try/except pour toutes les opérations de fichier
- Validation des données chargées avec valeurs par défaut en cas de données manquantes
- Sérialisation explicite de chaque attribut important
- Horodatage des sauvegardes pour information utilisateur

**Ce qui a été appris :** La robustesse est cruciale dans les systèmes de persistance. Il faut toujours anticiper les cas d'erreur et prévoir des fallbacks.

### 5. Rendu adaptatif à différentes résolutions

**Défi :** Adapter l'affichage de la carte à différentes résolutions d'écran tout en maintenant la proportion et la lisibilité.

**Problèmes rencontrés :**
- La carte était déformée sur certains écrans
- Les éléments de l'UI se chevauchaient ou sortaient de l'écran
- Le zoom n'était pas proportionnel

**Solution adoptée :**
- Calcul automatique du facteur de zoom optimal : `scale = min(scale_x, scale_y)`
- Centrage dynamique de la carte dans l'espace disponible
- Gestion intelligente de l'espace entre la carte et l'UI
- Utilisation de valeurs relatives (%) plutôt qu'absolues (pixels)

**Ce qui a été appris :** L'adaptabilité est essentielle pour les interfaces graphiques modernes. Le responsive design permet de garantir une bonne expérience utilisateur sur différents équipements.

### 6. Équilibrage du système de combat

**Défi :** Créer un système de combat équilibré qui ne soit ni trop facile ni trop difficile, avec une courbe de progression satisfaisante.

**Problèmes rencontrés :**
- Le joueur gagnait trop facilement les premiers combats
- Les ennemis devenaient trop forts trop vite
- Les formules de dégâts produisaient des résultats imprévisibles
- Les chances de critique étaient trop fréquentes ou trop rares

**Solution adoptée :**
- Tests itératifs avec ajustement progressif des paramètres
- Plafonds et planchers pour les formules (ex: hit_chance entre 10% et 95%)
- Courbe de progression non linéaire pour les statistiques
- Introduction des boss avec statistiques augmentées pour les combats clés

**Ce qui a été appris :** L'équilibrage de jeu est un processus itératif qui nécessite de nombreux tests et ajustements. Il n'y a pas de formule parfaite, mais un équilibre satisfaisant trouvé par l'expérience.

## 🤖 Contribution de l'Intelligence Artificielle au développement

Ce projet a bénéficié d'une assistance par intelligence artificielle pour plusieurs aspects complexes de son développement. L'IA a servi de catalyseur pour résoudre des problèmes algorithmiques et architecturaux.

### Outils et approche

L'IA a été utilisée de manière collaborative comme :
- **Guide technique** pour explorer des approches algorithmiques avancées
- **Assistant de débogage** pour identifier les problèmes logiques
- **Source de patterns** pour des solutions optimisées et éprouvées
- **Assistant de documentation** pour expliquer les concepts

### Bénéfices de l'assistance IA

1. **Rapidité de développement** : Les algorithmes complexes ont été implémentés plus rapidement
2. **Robustesse** : Les solutions incluent souvent la gestion des cas limites
3. **Optimisation** : Utilisation de structures de données et d'algorithmes optimaux (deque, BFS)
4. **Maintenabilité** : Code structuré facilitant les futures modifications
5. **Apprentissage** : Découverte de concepts algorithmiques avancés

### Limites et rôle humain

L'IA n'a pas remplacé le développement humain mais l'a assisté :
- ✅ Génération de code initial pour les algorithmes complexes
- ✅ Suggestions d'optimisation et de refactoring
- ✅ Documentation des concepts algorithmiques
- ❌ Non : Remplacement total du développement
- ❌ Non : Décisions de design sans validation humaine

Le développeur reste au contrôle de l'architecture, des décisions de design et de la validation des fonctionnalités.

## 📚 Structure du code détaillée

### Classes principales et leurs responsabilités

#### `Game` (sources/game.py)
Classe principale héritant de `arcade.Window`, gérant :
- La fenêtre et les boucles de rendu
- Les événements clavier et souris
- Les transitions entre phases
- L'affichage de l'interface utilisateur
- La coordination des différents systèmes

#### `TacticalCombat` (sources/Combat/tactical_combat.py)
Gère le système de combat :
- Calcul des dégâts (hit, crit, damage)
- Gestion des tours (joueur/ennemi)
- Pathfinding pour le mouvement
- Coordination avec l'IA ennemie

#### `GameMap` (sources/Map/game_map.py)
Gère la carte et le rendu :
- Génération procédurale des cartes
- Placement des obstacles et stations de soin
- Rendu adaptatif avec zoom automatique
- Gestion des entités sur la carte

#### `PlayerCharacter` (sources/Entities/Player_character.py)
Représente le héros :
- Statistiques (PV, attaque, défense, vitesse)
- Inventaire (potions de soin)
- Gestion de l'expérience et des niveaux
- Attaques disponibles

#### `Enemy` (sources/Entities/Ennemy.py)
Représente les ennemis :
- Statistiques individuelles
- Type (normal/boss)
- IA intégrée pour les décisions
- Gestion de la mort et des récompenses

#### `AIController` (sources/system/ai_controller.py)
Contient la logique de décision IA :
- Sélection de la cible optimale
- Calcul du mouvement vers la cible
- Prise de décision (attaquer/se déplacer)
- Gestion de la priorité des actions

#### `XpSystem` (sources/system/xp_system.py)
Gère la progression :
- Calcul de l'expérience gagnée
- Passage de niveau avec augmentation des stats
- Courbe de progression non linéaire
- Formules d'équilibre

#### `EnnemySpawner` (sources/system/enemy_spawner.py)
Génère les vagues d'ennemis :
- Création des ennemis normaux
- Génération des boss (plus puissants)
- Placement stratégique sur la carte
- Équilibrage des difficultés

## 🚀 Évolutions possibles

Si nous avions eu plus de temps, nous aurions souhaité implémenter :

### Fonctionnalités de gameplay
- **Plusieurs classes de personnages** : Guerrier, Mage, Archer avec compétences uniques
- **Système d'équipement** : Armes, armures, accessoires avec statistiques variables
- **Plusieurs types d'ennemis** : Variété dans les comportements et les capacités
- **Compétences spéciales** : Pouvoirs uniques avec cooldowns et effets
- **Éléments** : Feu, eau, terre avec interactions entre eux

### Cartes et environnement
- **Cartes plus grandes et plus variées** : Différents biomes (forêt, désert, donjon)
- **Environnements interactifs** : Pièges, téléporteurs, zones de bonus
- **Météo dynamique** : Conditions affectant les combats
- **Bâtiments et structures** : Points de contrôle, tours défensives

### Multijoueur
- **Mode multijoueur local** : 2 joueurs sur le même écran
- **Mode multijoueur en ligne** : Combats PVP ou coopératif
- **Système de classement** : Scoreboard et ladders

### Interface et expérience utilisateur
- **Effets visuels améliorés** : Animations d'attaque, particules, shake
- **Son et musique** : Bande-son dynamique et effets sonores
- **Interface personnalisable** : Options graphiques et contrôles
- **Tutoriel interactif** : Introduction guidée pour les nouveaux joueurs

### Systèmes avancés
- **Système de quêtes** : Missions secondaires avec récompenses
- **Histoire et narration** : Scénario avec dialogues et choix
- **Crafting** : Fabrication d'objets et d'équipement
- **Système de réputation** : Relations avec différentes factions

## 📝 Notes de développement

Ce projet a été développé dans le cadre du Trophée NSI (Numérique et Sciences Informatiques). Il démontre l'application de concepts avancés de programmation :

- **Programmation orientée objet** : Héritage, encapsulation, polymorphisme
- **Algorithmes et structures de données** : BFS, pathfinding, graphs, files
- **Intelligence artificielle basique** : Heuristiques, arbres de décision
- **Gestion d'état et événements** : Machine à états, observers
- **Persistance des données** : JSON, sérialisation
- **Interface graphique** : Arcade, rendu 2D, événements utilisateur

## 📞 Contact

Pour toute question ou problème concernant le projet :

- Thibault GIRARD-REYDET
- Julie GANIER JOSSE
- Nathan KETTERER

---

**Note importante** : L'assistance IA utilisée dans ce projet sert de support technique et pédagogique, permettant de surmonter les défis algorithmiques tout en apprenant les concepts fondamentaux de la programmation de jeux vidéo.
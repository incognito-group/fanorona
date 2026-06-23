# Fanoron-telo API Backend

Ce dossier contient le code backend du jeu **Fanoron-telo**, implémenté avec **FastAPI**. Il gère la logique de jeu, l'intelligence artificielle (Minimax, Alpha-Beta, Réseau de Neurones MLP) et fournit une API RESTful complète.

## Table des Matières
- [Architecture du Backend](#architecture-du-backend)
- [Installation et Lancement](#installation-et-lancement)
- [Fonctionnement de l'IA](#fonctionnement-de-lia)
- [Documentation de l'API](#documentation-de-lapi)
- [Comment Intégrer avec un Frontend Personnalisé](#comment-intégrer-avec-un-frontend-personnalisé)
- [Comment Intégrer un Modèle IA Personnalisé](#comment-intégrer-un-modèle-ia-personnalisé)

## Architecture du Backend

Le backend est structuré de manière modulaire :

```text
backend/
├── main.py                     # Point d'entrée FastAPI (endpoints REST)
├── game_logic.py               # Moteur du jeu, validation des coups, bitboards
├── train.py                    # Génération de dataset (self-play) et entraînement du MLP
├── ai/                         # Module d'Intelligence Artificielle
│   ├── minimax/
│   │   ├── alphabeta.py        # Alpha-Beta Pruning avec Table de Transposition
│   │   ├── minimax.py          # Minimax standard (profondeur fixe)
│   │   ├── evaluation.py       # Heuristiques d'évaluation du plateau
│   │   └── cache.py            # Implémentation de la Table de Transposition
├── models/                     # Modèles entraînés et métriques
│   ├── fanoron.joblib          # Modèle MLP scikit-learn sauvegardé
│   └── metrics.json            # Statistiques d'entraînement
├── data/                       # Données générées
│   ├── dataset.json            # Historique des parties générées
│   └── dataset.csv             # Dataset formaté pour l'entraînement
└── test_*.py                   # Fichiers de tests unitaires et d'intégration
```

## Installation et Lancement

1. **Prérequis** : Python 3.9+ recommandé.
2. **Installation des dépendances** :
   ```bash
   pip install -r requirements.txt
   ```
3. **Lancement du serveur** :
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```
4. Au premier lancement, si aucun modèle n'est trouvé dans `models/`, le serveur lancera automatiquement une génération de données et un entraînement.

## Fonctionnement de l'IA

Le backend propose 3 niveaux de difficulté :

1. **Facile (Random)** : Sélectionne un coup légal au hasard.
2. **Moyen (Minimax)** : Utilise l'algorithme Minimax standard à profondeur 3.
3. **Difficile (MLP + Alpha-Beta)** : 
   - Utilise en priorité un Réseau de Neurones Perceptron Multicouche (MLPClassifier de scikit-learn) entraîné par "Behavioral Cloning" sur des parties générées par auto-apprentissage.
   - En cas d'échec du modèle, bascule sur une recherche approfondie via **Alpha-Beta Pruning** (profondeur 8) optimisée avec un cache (Transposition Table) et Iterative Deepening.

L'évaluation des plateaux (`evaluation.py`) prend en compte l'alignement des pièces, le contrôle du centre, et la mobilité (nombre de coups possibles). Le moteur de jeu (`game_logic.py`) est optimisé en utilisant des opérations bit-à-bit (Bitboards) pour accélérer considérablement la recherche.

## Documentation de l'API

L'API complète avec schémas est disponible via Swagger UI à l'adresse : `http://127.0.0.1:8000/docs` (lorsque le serveur est lancé).

### Principaux Endpoints :

#### 1. Gestion de Partie
- **`GET /game/state`** : Renvoie l'état actuel de la partie.
- **`POST /game/new`** : Démarre une nouvelle partie.
- **`POST /game/play`** : Joue un coup.
  - *Payload Phase 1* : `{"cell": int}`
  - *Payload Phase 2* : `{"from_cell": int, "to_cell": int}` (ou simplement `{"cell": int}` comme destination, l'origine est déduite si possible).
- **`POST /game/undo`** / **`POST /game/redo`** : Annule ou rétablit le dernier coup.

#### 2. Intelligence Artificielle
- **`POST /ai/move`** : Demande à l'IA de choisir le meilleur coup.
  - *Payload* : `{"difficulty": "easy" | "medium" | "hard"}`
  - *Réponse* : Contient le coup choisi, le temps de calcul, la profondeur atteinte et la confiance (si réseau de neurones).

#### 3. Entraînement et Modèles
- **`POST /train`** : Lance l'entraînement du modèle IA.
  - *Payload* : `{"episodes": int}` (par défaut 5000)
- **`GET /train/status`** : Récupère l'état d'avancement de l'entraînement en cours.
- **`POST /model/load`** : Force le rechargement du modèle `.joblib` depuis le disque.

## Comment Intégrer avec un Frontend Personnalisé

Pour construire votre propre interface par-dessus ce backend, voici le workflow classique :

1. **Initialisation** : Au chargement, appelez `POST /game/new` ou `GET /game/state` pour récupérer la structure initiale de la partie :
   ```json
   {
       "board": [0, 0, 0, 0, 0, 0, 0, 0, 0], // 0: Vide, 1: P1, 2: P2
       "current_player": 1,
       "phase": "placement", // "placement" ou "movement"
       "winner": null,       // 1, 2, ou -1 (nul)
       "legal_moves": [...]
   }
   ```
2. **Coups Joueur** : Lorsqu'un joueur interagit, envoyez le coup via `POST /game/play`. Mettez à jour votre UI avec l'état renvoyé.
3. **Coups IA** : Si l'IA doit jouer (ex: `current_player == 2` en PvE) :
   - Appelez `POST /ai/move` avec la difficulté choisie.
   - Attendez la réponse qui vous donne le coup (`move`, `from_cell`, `to_cell`).
   - Appelez `POST /game/play` avec les données reçues pour appliquer officiellement le coup sur le serveur.
4. **Fin de partie** : Surveillez la valeur `winner` dans la réponse de chaque coup. Si `winner !== null`, affichez le résultat.

## Comment Intégrer un Modèle IA Personnalisé

L'architecture est conçue pour permettre facilement le remplacement de l'IA difficile (Réseau MLP) par votre propre modèle (PyTorch, TensorFlow, un autre arbre de décision, etc.).

### Étapes :

1. **Modifier `load_local_model()` dans `main.py`** :
   Actuellement, il charge un fichier `.joblib` via `scikit-learn`. Remplacez cette fonction pour charger votre modèle :
   ```python
   def load_local_model() -> bool:
       global my_custom_model
       # ... logique pour charger votre modèle (ex: torch.load())
       return True
   ```

2. **Adapter l'endpoint `/ai/move` (Difficulté "hard")** :
   Dans `main.py`, cherchez `elif difficulty == "hard":`. C'est là que l'inférence se produit.
   Le modèle reçoit l'état du plateau normalisé. Adaptez cette partie pour générer des prédictions avec votre modèle :
   ```python
   # ...
   elif difficulty == "hard":
       if my_custom_model is not None:
           # 1. Préparer les données (ex: formatage tenseur)
           x = normalize_board(active_game.board, active_game.current_player)
           
           # 2. Obtenir les probabilités depuis votre modèle
           probs = my_custom_model.predict(x)
           
           # 3. Filtrer et trouver le meilleur coup légal parmi legal_moves
           # ...
   ```

3. **(Optionnel) Adapter le pipeline d'entraînement dans `train.py`** :
   Si vous voulez que l'endpoint `/train` entraîne *votre* modèle, modifiez la fonction `train_model()` dans `train.py`.
   - Utilisez le fichier `data/dataset.csv` généré par le self-play (Alpha-Beta).
   - Entraînez votre modèle (ex: boucle d'entraînement PyTorch).
   - Sauvegardez le résultat dans le dossier `models/`.

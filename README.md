# Section 1 : En-tête Institutionnel et Identification

* **Institut :** [Institut Supérieur Polytechnique de Madagascar](https://www.ispm-edu.com)
* **Nom du groupe de projet :** Incognito

| Nom Complet | Numéro d'étudiant | Classe | Rôle précis pour ce Hackathon |
| :--- | :--- | :--- | :--- |
| RAKOTOMALALA Princy | N° 04 | IGGLIA 4A | Lead AI |
| RANDRIATAHINARIMANANA Tendry Ny Avo Gabriel | N° 18 | IGGLIA 4A | Backend Architect |
| NOMENJANAHARY Nambinintsoa Gilbert | N° 21 | Master 1 | Expert règles du jeu |
| RABENJARISON Fenomalala Safidy | N° 23 | IGGLIA 4A | Expert optimisation Alpha-Beta |
| SAROBIDINIRINA Tsizehena Bienvenue | N° 58 | IGGLIA 4A | Frontend / Lead DevOps |

---

# Section 2 : Description du Travail Réalisé

Nous avons développé une application web interactive de **Fanoron-telo**, jouable sur un plateau 3x3 avec les deux phases officielles : placement des 6 pions, puis déplacement vers les intersections adjacentes libres. La partie se termine immédiatement lorsqu'un joueur aligne ses 3 pions sur une ligne, une colonne ou une diagonale.

Fonctionnalités implémentées :

* Mode **Humain vs Humain** en local.
* Mode **Humain vs IA** avec trois niveaux : facile, moyenne et difficile.
* Mode **IA vs IA** pour démontrer automatiquement les décisions de l'IA.
* Gestion robuste des règles : placement, mouvement adjacent, changement de phase, détection de victoire.
* Options bonus : **Undo/Redo**, animations légères, affichage du temps de réponse de l'IA.

Architecture et pile technologique :

* **Frontend :** React avec Vite.
* **Interface :** Tailwind CSS via CDN pour un rendu rapide, clair et responsive.
* **IA locale :** JavaScript, utilisé comme fallback afin que le jeu reste jouable avec `npm run dev`.
* **IA déployée :** fonction Python FastAPI dans `api/`, compatible Vercel Serverless.

**Lien vers la version hébergée :** https://fanorona-wheat.vercel.app/

---

# Section 3 : Guide d'Installation Rapide (3 Commandes Max)

```bash
git clone https://github.com/incognito-group/fanorona
npm install
npm run dev
```

---

# Section 4 : Outils d'Aide IA Utilisés

L'équipe a utilisé des assistants IA comme ChatGPT et GitHub Copilot pour accélérer les parties répétitives du hackathon, tout en gardant la validation humaine sur les règles du Fanoron-telo.

Utilisations principales :

* Génération rapide de structures React et composants d'interface.
* Aide à la formulation du Minimax, de l'Alpha-Beta et de la fonction d'évaluation.
* Débogage des transitions entre phase de placement et phase de mouvement.
* Génération de tests mentaux et de scénarios de victoire.
* Rédaction et amélioration de la documentation du projet.

Le gain principal a été la réduction du temps passé sur le boilerplate et les explications, ce qui a permis de concentrer l'équipe sur la jouabilité, les règles et l'IA.

---

# Section 5 : Modélisation et Algorithmes de l'IA du Jeu

**Représentation de l'état du plateau :** le frontend représente le plateau par un tableau 1D de 9 cases (`P1`, `P2` ou `null`). L'API Python convertit ce tableau en matrice 3x3 pour faciliter les calculs de coordonnées. Les lignes gagnantes sont stockées dans une liste de 8 combinaisons : 3 lignes, 3 colonnes et 2 diagonales.

**Validation des mouvements :** en phase de placement, toute case libre est valide. En phase de mouvement, un pion ne peut aller que vers une intersection adjacente libre. Les connexions du plateau sont représentées par une table d'adjacence côté React et par une fonction géométrique côté Python.

**Niveaux d'IA :**

* **Facile :** sélection aléatoire parmi les coups légaux.
* **Moyenne :** joue un coup gagnant immédiat si possible, bloque une menace adverse, prend le centre en ouverture, sinon choisit un coup légal.
* **Difficile :** utilise Minimax avec élagage Alpha-Beta, priorité au centre en opening book, et une fonction d'évaluation tactique.

**Fonction d'évaluation :**

* `+1000` si l'IA gagne.
* `-1000` si l'adversaire gagne.
* Bonus pour deux pions alignés avec une case vide.
* Malus si l'adversaire possède une menace directe.
* Bonus de contrôle du centre.
* Bonus/malus de mobilité en phase de mouvement.

Techniques avancées utilisées :

* **Alpha-Beta pruning :** coupe les branches inutiles de l'arbre de recherche.
* **Opening book :** l'IA difficile prend le centre si disponible.
* **Table de transposition :** mémorisation des états évalués côté Python.
* **Sérialisation compacte :** représentation textuelle légère du plateau pour indexer les états.

---

# Section 6 : Analyses de Performances

Mesures réalisées sur les coups IA pendant le développement :

| Niveau IA | Technique principale | Temps de réponse moyen observé |
| :--- | :--- | :---: |
| Facile | Aléatoire | < 1 ms |
| Moyenne | Heuristique victoire/blocage | < 1 ms |
| Difficile | Minimax + Alpha-Beta | 1 à 15 ms selon la phase |

Résultats qualitatifs en mode IA vs IA :

* L'IA facile joue légalement mais rate souvent les menaces directes.
* L'IA moyenne bloque les victoires immédiates et gagne régulièrement contre l'IA facile.
* L'IA difficile est plus stable en phase de mouvement grâce à la recherche Alpha-Beta.

Autres métriques :

* Profondeur utilisée côté React : jusqu'à 6 demi-coups en placement et 8 demi-coups en mouvement.
* Le mode démo permet de vérifier rapidement la cohérence des règles et la stabilité des décisions IA.
* Undo/Redo permet de rejouer des branches de partie et de tester les réponses de l'IA sur un même état.

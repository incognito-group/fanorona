# Section 1 : En-tête Institutionnel et Identification

* **Institut :** [Institut Supérieur Polytechnique de Madagascar](https://www.ispm-edu.com)
* **Nom du groupe de projet :** Incognito

| Nom Complet | Numéro d'étudiant | Classe | Rôle précis pour ce Hackathon |
| :--- | :--- | :--- | :--- |
| RAKOTOMALALA Princy | N° 04 | IGGLIA 4A | Backend / Algo |
| RANDRIATAHINARIMANANA Tendry Ny Avo Gabriel | N° 18 | IGGLIA 4A | Backend / Algo |
| NOMENJANAHARY Nambinintsoa Gilbert | N° 21 | Master 1 | Backend / Algo |
| RABENJARISON Fenomalala Safidy | N° 23 | IGGLIA 4A | Backend / Algo |
| SAROBIDINIRINA Tsizehena Bienvenue | N° 58 | IGGLIA 4A | Frontend / DevOps |

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

L'équipe a utilisé des assistants IA comme ChatGPT et Gemini pour accélérer les parties répétitives du hackathon, tout en gardant la validation humaine sur les règles du Fanoron-telo.

Utilisations principales :

* Génération rapide de structures React et composants d'interface.
* Débogage des transitions entre phase de placement et phase de mouvement.
* Génération de tests mentaux et de scénarios de victoire.
* Rédaction et amélioration de la documentation du projet.

Le gain principal a été la réduction du temps passé sur le boilerplate et les explications, ce qui a permis de concentrer l'équipe sur la jouabilité, les règles et l'IA.

---

# Section 5 : Modélisation et Algorithmes

* **Représentation de l'état du plateau**:
Nous avons choisi une approche matricielle (grille matricielle 3×3) où chaque intersection est repérée par ses coordonnées (i,j) avec i,j ∈ {0,1,2}. Cette approche correspond fidèlement à la géométrie réelle du plateau et permet des calculs mathématiques directs pour les règles de déplacement, évitant ainsi l'utilisation de listes simples ou de structures de données lourdes.

* **Validation géométrique des mouvements**:
Au lieu d'utiliser un dictionnaire statique écrit à la main, les connexions physiques du Fanoron-telo sont calculées dynamiquement par l'algorithme. Celui-ci vérifie les distances de Manhattan et de Tchebychev pour s'assurer que le déplacement ne dépasse pas une case.

Cette vérification est combinée à une condition de parité mathématique : un déplacement diagonal n'est autorisé que si la somme des coordonnées de la case de départ respecte la condition (i + j) mod 2 == 0. Cela restreint géométriquement et automatiquement les diagonales au centre (1,1) et aux quatre coins, conformément au dessin traditionnel du jeu.

* **Fonction d'évaluation du Minimax**:
Notre fonction d'évaluation mathématique attribue un score numérique à chaque état final ou intermédiaire du plateau :

* Plus 1000 (Gain maximum) : Si l'état mène à un alignement de 3 pions de l'IA (Victoire).
* Moins 1000 (Pénalité maximum) : Si l'état permet un alignement de 3 pions de l'adversaire humain (Défaite).
* 0 (Neutre) : Si la configuration actuelle ne présente aucun alignement gagnant à ce stade de l'arbre.
L'objectif du Minimax est de maximiser ce score pour l'IA tout en supposant que l'adversaire cherchera à le minimiser.

* **Techniques Avancées Implémentées**:

* Table de Transposition et Rote Learning : Afin d'optimiser l'exploration de l'arbre de décision du Minimax, nous avons implémenté une table de transposition globale sous forme de dictionnaire de hachage. Dès qu'un état du plateau est évalué, son score est stocké en mémoire. Si l'algorithme rencontre une transposition (un état identique atteint par un chemin différent), il extrait directement la valeur numérique par "rote learning" sans réexplorer les sous-branches.
* Bitboard / Bit-by-bit léger : L'état de la grille matricielle est sérialisé sous forme de chaîne de caractères unidimensionnelle compacte . Cette chaîne agit comme une clé d'identification unique et ultra-légère pour accélérer les opérations de lecture et d'écriture dans la table de transposition.
* Opening Book (Bibliothèque d'ouvertures) : Pour la phase initiale de placement, l'IA intègre une stratégie d'ouverture prédéfinie qui priorise immédiatement l'occupation des cases stratégiques majeures (comme le centre du plateau en 1,1) sans déclencher l'algorithme Minimax, économisant ainsi les ressources processeur au coup d'envoi.

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

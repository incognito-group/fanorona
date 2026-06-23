# Section 1 : En-tête Institutionnel et Identification
* **Lien hypertexte :** [Institut Supérieur Polytechnique de Madagascar](https://www.ispm-edu.com)
* **Nom du groupe de projet :** Incognito

### Tableau des membres de l'équipe :
| Nom complet | Numéro | Classe | Rôle |
| :--- | :--- | :--- | :--- |
| RAKOTOMALALA Princy | N° 04 | IGGLIA 4A | Machine Learning |
| RANDRIATAHINARIMANANA Tendry Ny Avo Gabriel | N° 18 | IGGLIA 4A | Backend |
| NOMENJANAHARY Nambinintsoa Gilbert | N° 21 | Master 1 | Backend |
| RABENJARISON Fenomalala Safidy | N° 23 | IGGLIA 4A | Machine Learning |
| SAROBIDINIRINA Tsizehena Bienvenue | N° 58 | IGGLIA 4A | Frontend / DevOps |

---

# Section 2 : Description du Travail Réalisé
* **Présentation globale :** Application web interactive permettant de jouer au **Fanoron-telo**, un jeu de société traditionnel originaire de Madagascar. L'interface gère l'état du jeu sur un plateau de 3x3 intersections connectées, incluant la Phase 1 (Placement alterné des 6 pions) et la Phase 2 (Déplacement vers les intersections adjacentes libres).
* **Architecture et Pile (Stack) technologique :**
  * **Frontend :** React.js (initialisé avec Vite) pour une interface réactive et performante.
  * **Styling :** Tailwind CSS (via CDN) pour un design épuré, minimaliste et rigoureux.
  * **Algorithme / Moteur d'IA :** Python (FastAPI).
* **Lien vers la version hébergée :** https://fanorona-wheat.vercel.app/

---

# Section 3 : Guide d'Installation Rapide (3 Commandes Max)
Procédure pas-à-pas pour cloner, installer les dépendances et lancer l'application en local.

```bash
git clone https://github.com/incognito-group/fanorona
npm install
npm run dev
```

# Section 5 : Modélisation et Algorithmes de l'IA du Jeu

* **Représentation de l'état du plateau :** Nous avons choisi une approche matricielle (grille matricielle 3×3) où chaque intersection est repérée par ses coordonnées $(i, j)$ avec $i, j \in \{0, 1, 2\}$. Cette approche correspond fidèlement à la géométrie réelle du plateau et permet des calculs mathématiques directs pour les règles de déplacement, évitant ainsi l'utilisation de listes simples ou de structures de données lourdes.

* **Validation géométrique des mouvements :**
  Au lieu d'utiliser un dictionnaire statique écrit à la main, les connexions physiques du Fanoron-telo sont calculées dynamiquement par l'algorithme. Celui-ci vérifie les distances de Manhattan et de Tchebychev pour s'assurer que le déplacement ne dépasse pas une case.
  Cette vérification est combinée à une condition de parité mathématique : un déplacement diagonal n'est autorisé que si la somme des coordonnées de la case de départ respecte la condition $(i1 + j1) \pmod 2 == 0$. Cela restreint géométriquement et automatiquement les diagonales au centre $(1,1)$ et aux quatre coins, conformément au dessin traditionnel du jeu.

* **Fonctionnement du Minimax et fonction d'évaluation :**
  Notre fonction d'évaluation mathématique attribue un score numérique à chaque état final ou intermédiaire du plateau :
  * **Score +1000 (Gain maximum) :** Si l'état mène à un alignement de 3 pions de l'IA (Victoire).
  * **Score -1000 (Pénalité maximum) :** Si l'état permet un alignement de 3 pions de l'adversaire humain (Défaite).
  * **Score 0 (Neutre) :** Si la configuration actuelle ne présente aucun alignement gagnant à ce stade de l'arbre.
  L'objectif de l'algorithme Minimax est de maximiser ce score pour l'IA tout en supposant que l'adversaire cherchera à le minimiser.

* **Techniques avancées implémentées :**
  * [x] **Élagage Alpha-Beta :** Optimisation de la recherche en coupant l'exploration des branches qui n'influencent pas la décision finale du Minimax.
  * [x] **Table de Transposition et Rote Learning :** Utilisation d'un dictionnaire de hachage global pour stocker les scores des états déjà évalués, évitant la réexploration des sous-branches lors des transpositions.
  * [x] **Bitboard / Serialization légère :** L'état de la grille matricielle est sérialisé sous forme de chaîne de caractères unidimensionnelle compacte agissant comme une clé d'identification unique et ultra-rapide pour la table de transposition.
  * [x] **Opening Book (Bibliothèque d'ouvertures) :** Pour la phase de placement (Phase 1), l'IA intègre une stratégie prédéfinie qui priorise immédiatement l'occupation des cases stratégiques majeures, notamment le centre du plateau $(1,1)$, sans déclencher le Minimax pour économiser les ressources processeur.
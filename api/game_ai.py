import random

# Table de transposition globale pour le Rote Learning
TABLE_TRANSPOSITION = {}

def sont_voisins_legaux(i1, j1, i2, j2):
    diff_i = abs(i1 - i2)
    diff_j = abs(j1 - j2)
    
    # Distance de Manhattan / Tchebychev : interdiction de bouger de plus d'une case
    if diff_i > 1 or diff_j > 1 or (diff_i == 0 and diff_j == 0):
        return False
        
    # Mouvement vertical et horizontal
    if diff_i == 0 or diff_j == 0:
        return True
        
    # Validation géométrique par condition de parité mathématique pour les diagonales
    if (i1 + j1) % 2 == 0:
        return True
        
    return False

def verifier_victoire(plateau, joueur):
    # Verification des lignes et des colonnes
    for k in range(3):
        if all(plateau[k][j] == joueur for j in range(3)): return True
        if all(plateau[i][k] == joueur for i in range(3)): return True
        
    # Verification des diagonales géométriques
    if plateau[0][0] == joueur and plateau[1][1] == joueur and plateau[2][2] == joueur:
        return True
    if plateau[0][2] == joueur and plateau[1][1] == joueur and plateau[2][0] == joueur:
        return True
        
    return False

def serialiser_plateau(plateau):
    # Bitboard / Sérialisation légère sous forme de chaîne compacte 1D pour clé de hachage
    return "".join(str(cellule) for ligne in plateau for cellule in ligne)

def generer_coups_legaux(plateau, joueur, phase):
    coups = []
    if phase == 1:
        for i in range(3):
            for j in range(3):
                if plateau[i][j] == 0:
                    coups.append((i, j))
    elif phase == 2:
        for i1 in range(3):
            for j1 in range(3):
                if plateau[i1][j1] == joueur:
                    for i2 in range(3):
                        for j2 in range(3):
                            if plateau[i2][j2] == 0 and sont_voisins_legaux(i1, j1, i2, j2):
                                coups.append(((i1, j1), (i2, j2)))
    return coups

def simuler_coup(plateau, coup, joueur, phase):
    copie = [ligne[:] for ligne in plateau]
    if phase == 1:
        i, j = coup 
        copie[i][j] = joueur
    elif phase == 2:
        (i1, j1), (i2, j2) = coup
        copie[i1][j1] = 0
        copie[i2][j2] = joueur
    return copie

def evaluer_plateau(plateau, joueur_ia):
    joueur_adv = 1 if joueur_ia == 2 else 2
    if verifier_victoire(plateau, joueur_ia): return 1000
    if verifier_victoire(plateau, joueur_adv): return -1000
    return 0

def minimax_alpha_beta(plateau, profondeur, alpha, beta, est_max, joueur_ia, phase):
    joueur_adv = 1 if joueur_ia == 2 else 2
    joueur_actuel = joueur_ia if est_max else joueur_adv
    
    # Rote Learning : Vérification de la Table de Transposition via sérialisation légère
    cle_etat = serialiser_plateau(plateau)
    if cle_etat in TABLE_TRANSPOSITION:
        return TABLE_TRANSPOSITION[cle_etat]

    if profondeur == 0 or verifier_victoire(plateau, joueur_ia) or verifier_victoire(plateau, joueur_adv):
        score = evaluer_plateau(plateau, joueur_ia)
        TABLE_TRANSPOSITION[cle_etat] = score
        return score

    coups_possibles = generer_coups_legaux(plateau, joueur_actuel, phase)
    if not coups_possibles: return 0

    if est_max:
        max_eval = float('-inf')
        for coup in coups_possibles: 
            plateau_simule = simuler_coup(plateau, coup, joueur_ia, phase)
            evaluation = minimax_alpha_beta(plateau_simule, profondeur - 1, alpha, beta, False, joueur_ia, phase)
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha: break
        TABLE_TRANSPOSITION[cle_etat] = max_eval
        return max_eval
    else: 
        min_eval = float('inf')
        for coup in coups_possibles:
            plateau_simule = simuler_coup(plateau, coup, joueur_adv, phase)
            evaluation = minimax_alpha_beta(plateau_simule, profondeur - 1, alpha, beta, True, joueur_ia, phase)
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha: break
        TABLE_TRANSPOSITION[cle_etat] = min_eval
        return min_eval

def facile(plateau, joueur_ia, phase):
    coups = generer_coups_legaux(plateau, joueur_ia, phase)
    if not coups: return None
    return random.choice(coups)

def moyenne(plateau, joueur_ia, phase):
    coups = generer_coups_legaux(plateau, joueur_ia, phase)
    if not coups: return None
    joueur_adv = 1 if joueur_ia == 2 else 2
    
    for c in coups:
        if verifier_victoire(simuler_coup(plateau, c, joueur_ia, phase), joueur_ia):
            return c
            
    if phase == 1:
        coups_adv = generer_coups_legaux(plateau, joueur_adv, phase)
        for c_adv in coups_adv:
            if verifier_victoire(simuler_coup(plateau, c_adv, joueur_adv, phase), joueur_adv):
                if c_adv in coups:
                    return c_adv
                    
    return random.choice(coups)

def difficile(plateau, joueur_ia, phase):
    # Opening Book : Priorité absolue à l'occupation du centre (1,1) en phase de placement
    if phase == 1 and plateau[1][1] == 0:
        return (1, 1)

    coups_possible = generer_coups_legaux(plateau, joueur_ia, phase)
    if not coups_possible: return None
    
    meilleur_coup = None
    meilleur_score = float('-inf')
    profondeur_max = 6
    
    for coup in coups_possible:
        plateau_simule = simuler_coup(plateau, coup, joueur_ia, phase)
        score = minimax_alpha_beta(plateau_simule, profondeur_max - 1, float('-inf'), float('inf'), False, joueur_ia, phase)
        if score > meilleur_score:
            meilleur_score = score
            meilleur_coup = coup
            
    return meilleur_coup if meilleur_coup is not None else coups_possible[0]
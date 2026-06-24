import random

TABLE_TRANSPOSITION = {}

WINNING_LINES = (
    ((0, 0), (0, 1), (0, 2)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    ((0, 0), (1, 0), (2, 0)),
    ((0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 2), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
)


def adversaire(joueur):
    return 1 if joueur == 2 else 2


def compter_pions(plateau):
    return sum(1 for ligne in plateau for cellule in ligne if cellule != 0)


def prochaine_phase(plateau, phase):
    return 2 if phase == 1 and compter_pions(plateau) >= 6 else phase


def sont_voisins_legaux(i1, j1, i2, j2):
    diff_i = abs(i1 - i2)
    diff_j = abs(j1 - j2)

    if diff_i > 1 or diff_j > 1 or (diff_i == 0 and diff_j == 0):
        return False

    if diff_i == 0 or diff_j == 0:
        return True

    return (i1 + j1) % 2 == 0


def verifier_victoire(plateau, joueur):
    return any(all(plateau[i][j] == joueur for i, j in ligne) for ligne in WINNING_LINES)


def serialiser_plateau(plateau, joueur, phase, profondeur, est_max):
    cellules = "".join(str(cellule) for ligne in plateau for cellule in ligne)
    return f"{cellules}:{joueur}:{phase}:{profondeur}:{int(est_max)}"


def generer_coups_legaux(plateau, joueur, phase):
    coups = []

    if phase == 1:
        for i in range(3):
            for j in range(3):
                if plateau[i][j] == 0:
                    coups.append((i, j))
        return coups

    for i1 in range(3):
        for j1 in range(3):
            if plateau[i1][j1] != joueur:
                continue

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
    else:
        (i1, j1), (i2, j2) = coup
        copie[i1][j1] = 0
        copie[i2][j2] = joueur

    return copie


def score_ligne(plateau, ligne, joueur_ia):
    joueur_adv = adversaire(joueur_ia)
    nb_ia = sum(1 for i, j in ligne if plateau[i][j] == joueur_ia)
    nb_adv = sum(1 for i, j in ligne if plateau[i][j] == joueur_adv)
    nb_vide = sum(1 for i, j in ligne if plateau[i][j] == 0)

    if nb_ia == 3:
        return 1000
    if nb_adv == 3:
        return -1000
    if nb_ia == 2 and nb_vide == 1:
        return 60
    if nb_adv == 2 and nb_vide == 1:
        return -70
    if nb_ia == 1 and nb_vide == 2:
        return 8
    if nb_adv == 1 and nb_vide == 2:
        return -8
    return 0


def evaluer_plateau(plateau, joueur_ia, phase):
    joueur_adv = adversaire(joueur_ia)

    if verifier_victoire(plateau, joueur_ia):
        return 1000
    if verifier_victoire(plateau, joueur_adv):
        return -1000

    score = sum(score_ligne(plateau, ligne, joueur_ia) for ligne in WINNING_LINES)

    if plateau[1][1] == joueur_ia:
        score += 20
    elif plateau[1][1] == joueur_adv:
        score -= 20

    if phase == 2:
        score += (
            len(generer_coups_legaux(plateau, joueur_ia, phase))
            - len(generer_coups_legaux(plateau, joueur_adv, phase))
        ) * 4

    return score


def trouver_coup_gagnant(plateau, joueur, phase):
    for coup in generer_coups_legaux(plateau, joueur, phase):
        if verifier_victoire(simuler_coup(plateau, coup, joueur, phase), joueur):
            return coup
    return None


def minimax_alpha_beta(plateau, profondeur, alpha, beta, est_max, joueur_ia, phase):
    joueur_adv = adversaire(joueur_ia)
    joueur_actuel = joueur_ia if est_max else joueur_adv
    cle_etat = serialiser_plateau(plateau, joueur_actuel, phase, profondeur, est_max)

    if cle_etat in TABLE_TRANSPOSITION:
        return TABLE_TRANSPOSITION[cle_etat]

    if (
        profondeur == 0
        or verifier_victoire(plateau, joueur_ia)
        or verifier_victoire(plateau, joueur_adv)
    ):
        score = evaluer_plateau(plateau, joueur_ia, phase)
        TABLE_TRANSPOSITION[cle_etat] = score
        return score

    coups_possibles = generer_coups_legaux(plateau, joueur_actuel, phase)
    if not coups_possibles:
        return evaluer_plateau(plateau, joueur_ia, phase)

    if est_max:
        meilleur_score = float("-inf")
        for coup in coups_possibles:
            plateau_simule = simuler_coup(plateau, coup, joueur_actuel, phase)
            phase_suivante = prochaine_phase(plateau_simule, phase)
            score = minimax_alpha_beta(
                plateau_simule,
                profondeur - 1,
                alpha,
                beta,
                False,
                joueur_ia,
                phase_suivante,
            )
            meilleur_score = max(meilleur_score, score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
    else:
        meilleur_score = float("inf")
        for coup in coups_possibles:
            plateau_simule = simuler_coup(plateau, coup, joueur_actuel, phase)
            phase_suivante = prochaine_phase(plateau_simule, phase)
            score = minimax_alpha_beta(
                plateau_simule,
                profondeur - 1,
                alpha,
                beta,
                True,
                joueur_ia,
                phase_suivante,
            )
            meilleur_score = min(meilleur_score, score)
            beta = min(beta, score)
            if beta <= alpha:
                break

    TABLE_TRANSPOSITION[cle_etat] = meilleur_score
    return meilleur_score


def facile(plateau, joueur_ia, phase):
    coups = generer_coups_legaux(plateau, joueur_ia, phase)
    if not coups:
        return None
    return random.choice(coups)


def moyenne(plateau, joueur_ia, phase):
    coups = generer_coups_legaux(plateau, joueur_ia, phase)
    if not coups:
        return None

    coup_gagnant = trouver_coup_gagnant(plateau, joueur_ia, phase)
    if coup_gagnant:
        return coup_gagnant

    coup_adverse = trouver_coup_gagnant(plateau, adversaire(joueur_ia), phase)
    if coup_adverse and phase == 1 and coup_adverse in coups:
        return coup_adverse

    if phase == 2 and coup_adverse:
        destination_adverse = coup_adverse[1]
        for coup in coups:
            if coup[1] == destination_adverse:
                return coup

    if phase == 1 and plateau[1][1] == 0:
        return (1, 1)

    return random.choice(coups)


def difficile(plateau, joueur_ia, phase):
    if phase == 1 and plateau[1][1] == 0:
        return (1, 1)

    TABLE_TRANSPOSITION.clear()
    coups_possibles = generer_coups_legaux(plateau, joueur_ia, phase)
    if not coups_possibles:
        return None

    meilleur_coup = coups_possibles[0]
    meilleur_score = float("-inf")
    profondeur_max = 6 if phase == 1 else 8

    for coup in coups_possibles:
        plateau_simule = simuler_coup(plateau, coup, joueur_ia, phase)
        phase_suivante = prochaine_phase(plateau_simule, phase)
        score = minimax_alpha_beta(
            plateau_simule,
            profondeur_max - 1,
            float("-inf"),
            float("inf"),
            False,
            joueur_ia,
            phase_suivante,
        )
        if score > meilleur_score:
            meilleur_score = score
            meilleur_coup = coup

    return meilleur_coup

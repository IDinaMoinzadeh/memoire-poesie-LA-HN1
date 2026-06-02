# -*- coding: utf-8 -*-
"""
================================================================================
VISUALISATION 1 — Top du canon local : AVEC vs SANS le prix de poète lauréat
================================================================================
INPUT   : input_poetes_LA_canon_local_scored.csv   (canon local scoré, 618 poètes)
OUTPUT  : viz1_top_local_avec_sans_laureat.png      (figure : slope chart)
          viz1_classements_avec_sans_laureat.csv     (tableau de contrôle)

OBJECTIF : analyse de robustesse. Le prix de poète lauréat (créé en 2011) pèse
3 points dans le score local et avantage des poètes récents. On compare donc le
classement officiel (avec lauréat) au classement obtenu si on retire ce critère,
pour voir si le haut du canon local est stable ou non.

POUR RELANCER : ajustez uniquement le bloc PARAMÈTRES ci-dessous, puis
    python3 01_viz_canon_local_avec_sans_laureat.py
================================================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES — tout ce qui se règle est ici
# ---------------------------------------------------------------------------
INPUT   = "input_poetes_LA_canon_local_scored.csv"   # fichier d'entrée
OUT_PNG = "viz1_top_local_avec_sans_laureat.png"
OUT_CSV = "viz1_classements_avec_sans_laureat.csv"

TOP_N         = 15        # taille du top à comparer (mettez 20 si vous préférez)
POIDS_LAUREAT = 3         # poids du statut de lauréat dans le score local

# Les 13 anthologies locales + LAPL + blog Mohr servent à mesurer la "largeur"
# de présence d'un poète (dans combien de listes il figure). On l'utilise UNIQUEMENT
# pour départager les ex aequo, de façon identique dans les deux classements,
# afin que les mouvements observés viennent du lauréat et non du tri.
COLS_PRESENCE = [
    'anth_Buk_Vang_1972', 'streets_inside_1978', 'poetry_loves_poetry_1985',
    'invocation_LA_1989', 'grand_passion_1995', 'stand_up_1990', 'stand_up_2002',
    'leimert_park_2006', 'wide_awake_2015', 'cross_strokes_2015', 'coiled_serpent_2016',
    'leimert_park_redux_2017', 'workshop_beyond_baroque_2018', 'lapl_list',
    'mohr_blog_absents',
]


# ---------------------------------------------------------------------------
# 2. FONCTIONS
# ---------------------------------------------------------------------------
def charger_donnees(chemin):
    """Charge le CSV et ajoute l'indicateur binaire est_laureat (texte -> 0/1)."""
    df = pd.read_csv(chemin)
    df['est_laureat'] = df['laureat'].notna().astype(int)
    return df


def calculer_scores(df):
    """Calcule les deux scores (avec / sans lauréat) et la largeur de présence."""
    # Score AVEC lauréat = celui déjà calculé dans votre fichier.
    df['score_avec'] = df['score_canon_local']
    # Score SANS lauréat = on retire simplement les 3 points du statut de lauréat.
    df['score_sans'] = df['score_canon_local'] - POIDS_LAUREAT * df['est_laureat']
    # Largeur de présence (sert seulement de départage des ex aequo).
    df['largeur_presence'] = df[COLS_PRESENCE].sum(axis=1)
    return df


def classer(data, col_score):
    """Classement : score décroissant, puis largeur de présence, puis alphabétique."""
    ordre = data.sort_values(
        by=[col_score, 'largeur_presence', 'nom_famille', 'nom_canonique'],
        ascending=[False, False, True, True]
    ).reset_index(drop=True)
    ordre['rang'] = ordre.index + 1
    return ordre[['nom_canonique', col_score, 'est_laureat', 'rang']]


def statut(r):
    """Statut de mouvement d'un poète entre les deux tops (pour la couleur)."""
    in_avec = r['rang_avec'] <= TOP_N
    in_sans = r['rang_sans'] <= TOP_N
    if in_avec and in_sans:
        return 'stable'
    if in_avec and not in_sans:
        return 'sort'      # dépend du lauréat : sort du top sans le prix
    return 'entre'         # promu : entre dans le top quand on retire le prix


def construire_classements(df):
    """Construit la table de comparaison des deux classements et garde les tops."""
    cl_avec = classer(df, 'score_avec').rename(columns={'score_avec': 'score', 'rang': 'rang_avec'})
    cl_sans = classer(df, 'score_sans').rename(columns={'score_sans': 'score_sans', 'rang': 'rang_sans'})

    # Table de comparaison fusionnée
    comp = cl_avec.merge(
        cl_sans[['nom_canonique', 'score_sans', 'rang_sans']],
        on='nom_canonique'
    )

    # On garde les poètes présents dans le top N de l'un OU l'autre classement
    masque_top = (comp['rang_avec'] <= TOP_N) | (comp['rang_sans'] <= TOP_N)
    top = comp[masque_top].copy().sort_values('rang_avec').reset_index(drop=True)
    top['statut'] = top.apply(statut, axis=1)
    return top


def tracer_figure(top):
    """Slope chart : deux colonnes (avec / sans) reliées par des lignes."""
    HORS = TOP_N + 2          # début de la zone "hors du top N"
    PAS  = 0.85               # espacement vertical entre poètes hors-top
    couleurs = {'stable': '#9aa0a6', 'sort': '#c0392b', 'entre': '#1e8449'}

    # Les poètes "hors top" d'un côté doivent être espacés verticalement, sinon
    # leurs libellés se superposent. On les empile, triés par leur rang réel.
    # Côté gauche (avec) : occupants hors-top = ceux dont rang_avec > TOP_N (les "promus").
    # Côté droit (sans)  : occupants hors-top = ceux dont rang_sans > TOP_N (ceux qui sortent).
    hors_g = top[top['rang_avec'] > TOP_N].sort_values('rang_avec')['nom_canonique'].tolist()
    hors_d = top[top['rang_sans'] > TOP_N].sort_values('rang_sans')['nom_canonique'].tolist()
    y_hors_g = {nom: HORS + i * PAS for i, nom in enumerate(hors_g)}
    y_hors_d = {nom: HORS + i * PAS for i, nom in enumerate(hors_d)}

    def y_gauche(r):
        return r['rang_avec'] if r['rang_avec'] <= TOP_N else y_hors_g[r['nom_canonique']]
    def y_droite(r):
        return r['rang_sans'] if r['rang_sans'] <= TOP_N else y_hors_d[r['nom_canonique']]

    bas = HORS + max(len(hors_g), len(hors_d)) * PAS   # borne basse de la figure
    fig, ax = plt.subplots(figsize=(11, 0.55 * bas + 2))

    for _, r in top.iterrows():
        y_g = y_gauche(r)      # gauche = avec
        y_d = y_droite(r)      # droite = sans
        coul = couleurs[r['statut']]
        ax.plot([0, 1], [y_g, y_d], '-', color=coul, lw=1.8, alpha=0.8, zorder=1)
        ax.scatter([0, 1], [y_g, y_d], color=coul, s=30, zorder=2)

        etoile = ' \u2605' if r['est_laureat'] == 1 else ''   # ★ = lauréat
        # libellé à gauche : si hors-top à gauche, on rappelle le rang réel
        lg = f"{r['nom_canonique']} ({int(r['score'])}){etoile}"
        if r['rang_avec'] > TOP_N:
            lg += f" · rang {int(r['rang_avec'])}"
        ax.text(-0.03, y_g, lg, ha='right', va='center', fontsize=9, color=coul)
        # libellé à droite : idem si hors-top à droite
        ld = f"{r['nom_canonique']} ({int(r['score_sans'])}){etoile}"
        if r['rang_sans'] > TOP_N:
            ld += f" · rang {int(r['rang_sans'])}"
        ax.text(1.03, y_d, ld, ha='left', va='center', fontsize=9, color=coul)

    # Axes et habillage
    ax.set_xlim(-0.62, 1.62)
    ax.set_ylim(bas + 0.8, 0.2)         # rang 1 en haut, "hors top" en bas
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Score AVEC lauréat", "Score SANS lauréat"], fontsize=11, fontweight='bold')
    ax.set_yticks(list(range(1, TOP_N + 1)) + [HORS])
    ax.set_yticklabels([str(i) for i in range(1, TOP_N + 1)] + [f"hors top {TOP_N}"], fontsize=8)
    ax.set_ylabel("Rang", fontsize=10)
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.axhline(TOP_N + 0.5, color='lightgray', ls='--', lw=0.8)

    # Légende
    leg = [
        Line2D([0], [0], color=couleurs['stable'], lw=2, label='Reste dans le top'),
        Line2D([0], [0], color=couleurs['sort'],   lw=2, label='Sort du top (dépend du lauréat)'),
        Line2D([0], [0], color=couleurs['entre'],  lw=2, label='Entre dans le top (promu)'),
    ]
    ax.legend(handles=leg, loc='lower center', bbox_to_anchor=(0.5, -0.12),
              ncol=3, frameon=False, fontsize=8)

    ax.set_title(f"Canon local de LA — top {TOP_N} avec et sans le prix de poète lauréat\n"
                 f"(\u2605 = poète lauréat ; score entre parenthèses)", fontsize=12, pad=15)

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=150, bbox_inches='tight')


def verifier_formule(df):
    """Contrôle : reconstitue le score à partir des poids supposés et compare."""
    poids = {c: 1 for c in COLS_PRESENCE}
    poids['lapl_list'] = 2                      # LAPL pèse 2
    recon = sum(df[c] * w for c, w in poids.items()) + POIDS_LAUREAT * df['est_laureat']
    ok = bool((recon == df['score_canon_local']).all())
    print("Vérification formule du score (doit être True) :", ok)


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    df = charger_donnees(INPUT)
    df = calculer_scores(df)
    top = construire_classements(df)

    # Sauvegarde du tableau de contrôle (les données derrière la figure)
    top_export = top[['nom_canonique', 'est_laureat',
                      'score', 'rang_avec', 'score_sans', 'rang_sans', 'statut']]
    top_export = top_export.rename(columns={'score': 'score_avec'})
    top_export.to_csv(OUT_CSV, index=False, encoding='utf-8')

    tracer_figure(top)
    print("Figure  ->", OUT_PNG)
    print("Données ->", OUT_CSV)

    verifier_formule(df)


if __name__ == "__main__":
    main()

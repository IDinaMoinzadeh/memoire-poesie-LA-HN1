# -*- coding: utf-8 -*-
"""
================================================================================
VISUALISATION 2 — Canon national : VOLUME vs PRÉSENCE
================================================================================
INPUT   : input_poetes_LA_canon_national_FINAL.csv   (canon national, 618 poètes)
OUTPUT  : viz2_volume_vs_presence.png                 (figure : nuage de points)
          viz2_comparaison_volume_presence.csv         (données : 122 poètes actifs)

OBJECTIF : décider si les deux façons de mesurer la canonisation nationale disent
la même chose. Si oui, on n'en gardera qu'une pour le futur nuage local/national.

Rappel des formules (vérifiées sur les 618 lignes) :
  - PRÉSENCE = nb de revues où le poète figure (0-4) + 2 x nb d'anthologies nat (0-2)
  - VOLUME   = total de poèmes publiés dans les 4 revues (illimité) + 2 x nb d'anthologies nat
Les deux partagent la brique "anthologies" ; elles ne diffèrent que sur les revues
(présence = chaque revue compte 1 fois ; volume = chaque publication compte).

POUR RELANCER : ajustez le bloc PARAMÈTRES ci-dessous, puis
    python3 02_viz_canon_national_volume_vs_presence.py
NB : nécessite scipy et adjustText  ->  pip install scipy adjustText
================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from adjustText import adjust_text

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES
# ---------------------------------------------------------------------------
INPUT    = "input_poetes_LA_canon_national_FINAL.csv"
OUT_PNG  = "viz2_volume_vs_presence.png"
OUT_CSV  = "viz2_comparaison_volume_presence.csv"

N_LABELS = 5          # nombre de poètes divergents à étiqueter de chaque côté

# Seuil d'étiquetage : on nomme les poètes "nationalement présents" (présence >= 3
# OU volume >= 5). En deçà, c'est la longue traîne des poètes publiés une seule fois,
# qu'on n'étiquette pas pour rester lisible.
SEUIL_PRESENCE = 3
SEUIL_VOLUME   = 5

GRAINE_JITTER  = 42   # graine fixe -> jitter (et donc figure) reproductible


# ---------------------------------------------------------------------------
# 2. FONCTIONS
# ---------------------------------------------------------------------------
def charger_actifs(chemin):
    """Charge le CSV et ne garde que les poètes actifs au national (présence > 0)."""
    df = pd.read_csv(chemin)
    a = df[df['score_national_presence'] > 0].copy()
    print(f"Poètes avec une présence nationale : {len(a)} sur {len(df)}")
    return a


def calculer_rangs_divergence(a):
    """Calcule les rangs (volume / présence), l'écart de rang, et le Spearman."""
    # method='min' : les ex aequo partagent le meilleur rang (rang "compétition")
    a['rang_volume']   = a['score_national_volume'].rank(ascending=False, method='min')
    a['rang_presence'] = a['score_national_presence'].rank(ascending=False, method='min')
    # Écart de rang : positif = bien mieux classé en volume qu'en présence
    a['ecart_rang'] = a['rang_presence'] - a['rang_volume']

    # Corrélation de rang (Spearman) : mesure si les deux classent pareil
    rho, p = spearmanr(a['score_national_volume'], a['score_national_presence'])
    print(f"Spearman volume / presence (actifs) : rho = {rho:.3f}")
    return a, rho, p


def sauvegarder_donnees(a):
    """Exporte le tableau de contrôle (données derrière la figure)."""
    export = a[['nom_canonique', 'score_national_volume', 'score_national_presence',
                'rang_volume', 'rang_presence', 'ecart_rang']].sort_values(
                'score_national_volume', ascending=False)
    export.to_csv(OUT_CSV, index=False, encoding='utf-8')


def tracer_figure(a, rho):
    """Nuage de points volume (x) vs présence (y), coloré par l'écart de rang."""
    rng = np.random.default_rng(GRAINE_JITTER)      # graine fixe -> jitter reproductible
    # Jitter plus large : les poètes qui partagent un même point (scores entiers) sont
    # ainsi écartés et chacun peut recevoir son étiquette.
    a['x_plot'] = a['score_national_volume']   + rng.uniform(-0.30, 0.30, len(a))
    a['y_plot'] = a['score_national_presence'] + rng.uniform(-0.22, 0.22, len(a))

    fig, ax = plt.subplots(figsize=(15, 10))

    # Couleur = écart de rang. Bleu = mieux classé en volume ; rouge = mieux classé en présence.
    lim = a['ecart_rang'].abs().max()
    sc = ax.scatter(a['x_plot'], a['y_plot'], c=a['ecart_rang'], cmap='coolwarm_r',
                    vmin=-lim, vmax=lim, s=45, alpha=0.85,
                    edgecolor='white', linewidth=0.4, zorder=2)
    cb = fig.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label("Écart de rang (bleu = volume favorise ; rouge = présence favorise)", fontsize=9)

    # Poètes à étiqueter
    a_lab = a[(a['score_national_presence'] >= SEUIL_PRESENCE) |
              (a['score_national_volume']   >= SEUIL_VOLUME)].copy()
    print(f"Poètes étiquetés : {len(a_lab)}")

    # Les 5 leaders (plus fort volume) en gras pour les repérer
    leaders = set(a.sort_values('score_national_volume', ascending=False).head(5)['nom_canonique'])

    textes = []
    for _, r in a_lab.iterrows():
        gras = 'bold' if r['nom_canonique'] in leaders else 'normal'
        textes.append(ax.text(r['x_plot'], r['y_plot'], r['nom_canonique'],
                              fontsize=8, color='#222', fontweight=gras))

    # adjustText écarte les étiquettes entre elles et les relie à leur point par un trait fin
    adjust_text(textes, ax=ax,
                arrowprops=dict(arrowstyle='-', color='gray', lw=0.5, alpha=0.6),
                expand=(1.1, 1.3), force_text=(0.4, 0.6))

    # Habillage
    ax.set_xlabel("Score VOLUME national (poèmes publiés + anthologies)", fontsize=11)
    ax.set_ylabel("Score PRÉSENCE national (sources distinctes)", fontsize=11)
    ax.set_title("Canon national : volume vs présence (122 poètes actifs)\n"
                 f"Corrélation de rang (Spearman) \u03c1 = {rho:.2f}  —  "
                 f"noms affichés : présence \u2265 {SEUIL_PRESENCE} ou volume \u2265 {SEUIL_VOLUME}",
                 fontsize=12, pad=12)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.grid(True, ls=':', alpha=0.4)

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=150, bbox_inches='tight')


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    a = charger_actifs(INPUT)
    a, rho, p = calculer_rangs_divergence(a)
    sauvegarder_donnees(a)
    tracer_figure(a, rho)
    print("Figure  ->", OUT_PNG)
    print("Données ->", OUT_CSV)


if __name__ == "__main__":
    main()

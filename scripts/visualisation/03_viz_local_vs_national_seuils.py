# -*- coding: utf-8 -*-
"""
================================================================================
VISUALISATION 3 — Canon LOCAL vs NATIONAL (PRÉSENCE), coloré par configuration
                  TEST DE ROBUSTESSE : seuil local = 5, puis = 6
================================================================================
INPUT   : input_poetes_LA_canon_local_scored.csv     (canon local scoré)
          input_poetes_LA_canon_national_FINAL.csv    (canon national)
OUTPUT  : viz3b_local_vs_national_couleurs.png         (figure, seuil local = 5)
          viz3b_local_vs_national_categories.csv        (données, seuil local = 5)
          viz3c_local_vs_national_seuil6.png            (figure, seuil local = 6)
          viz3c_local_vs_national_categories_seuil6.csv (données, seuil local = 6)

OBJECTIF : situer chaque poète selon sa double configuration (fort/faible en local,
fort/faible en national, mesuré en PRÉSENCE). On teste DEUX seuils de "fort en local"
(5 et 6) pour vérifier que la lecture en quatre groupes ne dépend pas d'un choix
arbitraire de seuil. Chaque poète est coloré selon son groupe :
  - double canonisation : fort en local ET fort en national
  - plutôt local        : fort en local, faible en national
  - plutôt national     : faible en local, fort en national
  - périphérie          : faible des deux côtés

POUR RELANCER : ajustez le bloc PARAMÈTRES ci-dessous, puis
    python3 03_viz_local_vs_national_seuils.py
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
INPUT_LOCAL    = "input_poetes_LA_canon_local_scored.csv"
INPUT_NATIONAL = "input_poetes_LA_canon_national_FINAL.csv"

SEUIL_NATIONAL      = 3     # frontière "fort en national" (commune aux deux versions)
N_PERIPHERIE_NOMMES = 18    # nb de poètes de la périphérie nommés à titre d'exemple
GRAINE_JITTER       = 42    # graine fixe -> jitter (et figure) reproductibles

# Couleur et libellé de chaque catégorie
COULEURS = {'double': '#6a3d9a', 'local': '#e66101', 'national': '#2166ac', 'peripherie': '#bdbdbd'}
LIBELLES = {
    'double':     'Double canonisation',
    'local':      'Plutôt local',
    'national':   'Plutôt national',
    'peripherie': 'Périphérie',
}

# Les DEUX versions testées. Seul "seuil_local" change ; tout le reste est commun.
# (Noms de sortie conservés à l'identique pour ne pas casser les renvois du mémoire.)
CONFIGS = [
    {
        "seuil_local": 5,
        "out_png": "viz3b_local_vs_national_couleurs.png",
        "out_csv": "viz3b_local_vs_national_categories.csv",
        "titre": "Canon local vs canon national (mesuré en PRÉSENCE)\n"
                 "618 poètes, colorés par configuration — Spearman \u03c1 = {rho:.2f}",
    },
    {
        "seuil_local": 6,
        "out_png": "viz3c_local_vs_national_seuil6.png",
        "out_csv": "viz3c_local_vs_national_categories_seuil6.csv",
        "titre": "Canon local vs canon national (PRÉSENCE) — seuil LOCAL relevé à 6 (au lieu de 5)\n"
                 "618 poètes, colorés par configuration — Spearman \u03c1 = {rho:.2f}",
    },
]


# ---------------------------------------------------------------------------
# 2. FONCTIONS
# ---------------------------------------------------------------------------
def charger_fusion():
    """Charge les deux fichiers et les fusionne sur poet_id."""
    local    = pd.read_csv(INPUT_LOCAL)
    national = pd.read_csv(INPUT_NATIONAL)
    df = local[['poet_id', 'nom_canonique', 'score_canon_local']].merge(
         national[['poet_id', 'score_national_presence']], on='poet_id')
    return df


def calculer_spearman(df):
    """Corrélation de rang local / national (ne dépend pas du seuil)."""
    rho, p = spearmanr(df['score_canon_local'], df['score_national_presence'])
    print(f"Spearman local / national(présence) : rho = {rho:.3f}")
    return rho


def categoriser(df, seuil_local, seuil_national):
    """Attribue à chaque poète sa configuration selon les deux seuils."""
    def categorie(r):
        fl = r['score_canon_local']      >= seuil_local
        fn = r['score_national_presence'] >= seuil_national
        if fl and fn:       return 'double'
        if fl and not fn:   return 'local'
        if fn and not fl:   return 'national'
        return 'peripherie'
    df = df.copy()
    df['categorie'] = df.apply(categorie, axis=1)
    return df


def sauvegarder_donnees(df, out_csv):
    """Exporte la table des poètes avec leur catégorie (triée)."""
    df.sort_values(['score_national_presence', 'score_canon_local'], ascending=False) \
      .to_csv(out_csv, index=False, encoding='utf-8')


def tracer_figure(df, rho, out_png, titre):
    """Nuage local (x) vs national-présence (y), coloré par catégorie."""
    compte = df['categorie'].value_counts()

    rng = np.random.default_rng(GRAINE_JITTER)      # graine fixe = reproductible
    df['x'] = df['score_canon_local']       + rng.uniform(-0.22, 0.22, len(df))
    df['y'] = df['score_national_presence'] + rng.uniform(-0.22, 0.22, len(df))

    fig, ax = plt.subplots(figsize=(15, 10))

    # Un nuage par catégorie (pour avoir une couleur + une légende par groupe)
    for cat in ['peripherie', 'local', 'national', 'double']:   # périphérie d'abord (dessous)
        sous = df[df['categorie'] == cat]
        ax.scatter(sous['x'], sous['y'], s=38, color=COULEURS[cat], alpha=0.65,
                   edgecolor='white', linewidth=0.3,
                   label=f"{LIBELLES[cat]} ({compte.get(cat, 0)})")

    # --- Noms ---
    # (a) tous les poètes "forts" (hors périphérie)
    a_nommer = df[df['categorie'] != 'peripherie']
    # (b) un échantillon de la périphérie, à titre d'exemple (bas à gauche)
    peri = df[df['categorie'] == 'peripherie']
    echantillon = peri.sample(n=min(N_PERIPHERIE_NOMMES, len(peri)), random_state=42)

    textes = []
    for _, r in a_nommer.iterrows():
        textes.append(ax.text(r['x'], r['y'], r['nom_canonique'], fontsize=8,
                              color=COULEURS[r['categorie']], fontweight='bold'))
    for _, r in echantillon.iterrows():
        textes.append(ax.text(r['x'], r['y'], r['nom_canonique'], fontsize=7, color='#777'))

    adjust_text(textes, ax=ax,
                arrowprops=dict(arrowstyle='-', color='gray', lw=0.4, alpha=0.5))

    # Habillage
    ax.set_xlabel("Score canon LOCAL (anthologies de LA, LAPL, poète lauréat)", fontsize=11)
    ax.set_ylabel("Score canon NATIONAL — PRÉSENCE (nombre de sources nationales)", fontsize=11)
    ax.set_title(titre.format(rho=rho), fontsize=13, pad=12)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=4, frameon=False, fontsize=10)
    for cote in ['top', 'right']:
        ax.spines[cote].set_visible(False)
    ax.grid(True, ls=':', alpha=0.4)

    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches='tight')
    print(f"  Périphérie : {N_PERIPHERIE_NOMMES} noms affichés sur {len(peri)} poètes")


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    df = charger_fusion()
    rho = calculer_spearman(df)

    for cfg in CONFIGS:
        print(f"\n--- Seuil local = {cfg['seuil_local']} ---")
        dfc = categoriser(df, cfg['seuil_local'], SEUIL_NATIONAL)
        sauvegarder_donnees(dfc, cfg['out_csv'])
        tracer_figure(dfc, rho, cfg['out_png'], cfg['titre'])
        print("Figure  ->", cfg['out_png'])
        print("Données ->", cfg['out_csv'])


if __name__ == "__main__":
    main()

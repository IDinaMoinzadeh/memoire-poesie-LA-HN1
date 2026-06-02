# -*- coding: utf-8 -*-
"""
================================================================================
VISUALISATION 4 — Le QUADRANT : quatre configurations de canonisation
================================================================================
INPUT   : input_poetes_LA_canon_local_scored.csv     (canon local scoré)
          input_poetes_LA_canon_national_FINAL.csv    (canon national)
OUTPUT  : viz4_quadrant.png                            (figure)
          viz4_quadrant_categories.csv                  (données)

OBJECTIF : reprendre le nuage local (X) vs national-PRÉSENCE (Y) et le découper en
quatre zones avec deux traits (seuils local = 5, national = 3). Chaque zone est
nommée et accompagnée du nombre de poètes qu'elle contient. Version pensée pour un
lecteur non spécialiste : peu de noms individuels, des étiquettes de zone claires.

POUR RELANCER : ajustez le bloc PARAMÈTRES ci-dessous, puis
    python3 04_viz_quadrant.py
NB : nécessite adjustText  ->  pip install adjustText
================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from adjustText import adjust_text

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES
# ---------------------------------------------------------------------------
INPUT_LOCAL    = "input_poetes_LA_canon_local_scored.csv"
INPUT_NATIONAL = "input_poetes_LA_canon_national_FINAL.csv"
OUT_PNG = "viz4_quadrant.png"
OUT_CSV = "viz4_quadrant_categories.csv"

SEUIL_LOCAL    = 5      # -> trait VERTICAL (frontière "fort en local")
SEUIL_NATIONAL = 3      # -> trait HORIZONTAL (frontière "fort en national")

# Nombre de noms repères affichés par zone (8 = tous les doubles)
N_ANCRES = {'double': 8, 'local': 10, 'national': 6}
# Noms qu'on veut afficher à coup sûr, même s'ils dépassent la limite ci-dessus
NOMS_FORCES = ['Suzanne Lummis']

GRAINE_JITTER = 42      # graine fixe -> jitter (et figure) reproductibles

COULEURS = {'double': '#6a3d9a', 'local': '#e66101', 'national': '#2166ac', 'peripherie': '#bdbdbd'}


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


def categoriser(df):
    """Attribue à chaque poète sa configuration selon les deux seuils."""
    def categorie(r):
        fl = r['score_canon_local']      >= SEUIL_LOCAL
        fn = r['score_national_presence'] >= SEUIL_NATIONAL
        if fl and fn:     return 'double'
        if fl and not fn: return 'local'
        if fn and not fl: return 'national'
        return 'peripherie'
    df['categorie'] = df.apply(categorie, axis=1)
    return df


def sauvegarder_donnees(df):
    """Exporte la table des poètes avec leur catégorie (triée)."""
    df.sort_values(['score_national_presence', 'score_canon_local'], ascending=False) \
      .to_csv(OUT_CSV, index=False, encoding='utf-8')


def tracer_figure(df):
    """Nuage découpé en quatre zones par deux traits, avec étiquettes de zone."""
    compte = df['categorie'].value_counts()

    rng = np.random.default_rng(GRAINE_JITTER)
    df['x'] = df['score_canon_local']       + rng.uniform(-0.22, 0.22, len(df))
    df['y'] = df['score_national_presence'] + rng.uniform(-0.22, 0.22, len(df))

    fig, ax = plt.subplots(figsize=(14, 10))

    # les points, colorés par zone
    for cat in ['peripherie', 'local', 'national', 'double']:
        sous = df[df['categorie'] == cat]
        ax.scatter(sous['x'], sous['y'], s=36, color=COULEURS[cat], alpha=0.6,
                   edgecolor='white', linewidth=0.3)

    # --- LES DEUX TRAITS QUI FONT LE QUADRANT ---
    # La frontière "local >= 5" se situe ENTRE 4 et 5, donc à 4,5. On trace le trait
    # à SEUIL - 0.5 pour que les poètes au score pile égal au seuil soient bien DANS la case
    # (et non coupés en deux par le trait).
    ax.axvline(x=SEUIL_LOCAL - 0.5,    color='#444', ls='--', lw=1.3)   # trait vertical
    ax.axhline(y=SEUIL_NATIONAL - 0.5, color='#444', ls='--', lw=1.3)   # trait horizontal

    # --- LE NOM ET LE COMPTE DE CHAQUE ZONE ---
    # (x, y, texte, alignement) ; placés vers les coins pour ne pas gêner les points
    xmax = df['x'].max() + 0.6
    ymax = df['y'].max() + 0.6
    zones = [
        (xmax, ymax, f"DOUBLE CANONISATION\n{compte.get('double',0)} poètes",   'right', 'top',    '#6a3d9a'),
        (-0.3, ymax, f"NATIONAUX SANS ANCRAGE LOCAL\n{compte.get('national',0)} poètes", 'left', 'top', '#2166ac'),
        (xmax, -0.5, f"ICÔNES LOCALES\n{compte.get('local',0)} poètes",         'right', 'bottom', '#e66101'),
        (-0.3, -0.5, f"PÉRIPHÉRIE\n{compte.get('peripherie',0)} poètes",        'left',  'bottom', '#777'),
    ]
    for x, y, txt, ha, va, coul in zones:
        ax.text(x, y, txt, ha=ha, va=va, fontsize=13, fontweight='bold', color=coul,
                bbox=dict(boxstyle='round,pad=0.4', fc='white', ec=coul, alpha=0.9))

    # --- quelques noms repères par zone (les plus marquants), pas tous ---
    ancres = []
    # double + local : on prend les plus forts en LOCAL ; national : les plus forts en NATIONAL
    for cat, tri in [('double', 'score_canon_local'),
                     ('local', 'score_canon_local'),
                     ('national', 'score_national_presence')]:
        sous = df[df['categorie'] == cat].sort_values(tri, ascending=False).head(N_ANCRES[cat])
        ancres.append(sous)
    # on ajoute les noms forcés (épinglés quoi qu'il arrive)
    ancres.append(df[df['nom_canonique'].isin(NOMS_FORCES)])
    ancres = pd.concat(ancres).drop_duplicates(subset='poet_id')

    textes = [ax.text(r['x'], r['y'], r['nom_canonique'], fontsize=9,
                      color=COULEURS[r['categorie']]) for _, r in ancres.iterrows()]
    adjust_text(textes, ax=ax, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5, alpha=0.6))

    # Habillage
    ax.set_xlabel("Score canon LOCAL (anthologies de LA, LAPL, poète lauréat)", fontsize=11)
    ax.set_ylabel("Score canon NATIONAL — PRÉSENCE (nombre de sources nationales)", fontsize=11)
    ax.set_title(f"Les quatre configurations de canonisation (seuils : local = {SEUIL_LOCAL}, national = {SEUIL_NATIONAL})",
                 fontsize=14, pad=12)
    for cote in ['top', 'right']:
        ax.spines[cote].set_visible(False)
    ax.grid(True, ls=':', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=150, bbox_inches='tight')
    print("Comptes par zone :")
    print(compte.to_string())


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    df = charger_fusion()
    df = categoriser(df)
    sauvegarder_donnees(df)
    tracer_figure(df)
    print("Figure  ->", OUT_PNG)
    print("Données ->", OUT_CSV)


if __name__ == "__main__":
    main()

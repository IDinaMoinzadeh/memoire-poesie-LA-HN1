# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT 10 — Scoring canon local → poetes_LA_canon_local_scored.csv
================================================================================
INPUT   : poetes_LA_canon_local.csv        (618 poètes, produit par le pipeline
                                             d'acquisition Canon_LA.ipynb →
                                             Nettoyage_Canon_LA.ipynb →
                                             Nettoyage_index_final.ipynb)
OUTPUT  : poetes_LA_canon_local_scored.csv  (618 poètes, mêmes colonnes +
                                             score_canon_local)

POIDS APPLIQUÉS (hiérarchie institutionnelle croissante) :
  - 13 anthologies locales           : 1 pt chacune
  - mohr_blog_absents                : 1 pt
  - holdouts (Hold-Outs, Bill Mohr)  : 0 pt — exclu délibérément
    (source biographique, pas de sélection éditoriale)
  - lapl_list                        : 2 pts (sélection éditoriale institution publique)
  - laureat                          : 3 pts (consécration institutionnelle locale)

NOTE SUR L'ACQUISITION (pipeline amont) :
  Canon_LA.ipynb (~90 cellules) construit poetes_LA.csv depuis
  poetes_LA_liste_definitive.txt, en ajoutant chaque anthologie source par
  source avec corrections de noms. Ce carnet de construction constitue la
  trace de l'acquisition manuelle ; il n'est pas automatisable mais est
  conservé dans notebooks/ comme documentation des décisions d'harmonisation.

POUR RELANCER :
    python3 10_score_canon_local.py
================================================================================
"""

import pandas as pd

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES
# ---------------------------------------------------------------------------
INPUT  = "poetes_LA_canon_local.csv"
OUTPUT = "poetes_LA_canon_local_scored.csv"

POIDS = {
    "anth_Buk_Vang_1972"          : 1,
    "streets_inside_1978"         : 1,
    "poetry_loves_poetry_1985"    : 1,
    "invocation_LA_1989"          : 1,
    "grand_passion_1995"          : 1,
    "stand_up_1990"               : 1,
    "stand_up_2002"               : 1,
    "leimert_park_2006"           : 1,
    "wide_awake_2015"             : 1,
    "cross_strokes_2015"          : 1,
    "coiled_serpent_2016"         : 1,
    "leimert_park_redux_2017"     : 1,
    "workshop_beyond_baroque_2018": 1,
    "mohr_blog_absents"           : 1,
    "holdouts"                    : 0,   # exclu : source biographique, pas sélection
    "lapl_list"                   : 2,
    # laureat : traité séparément (colonne texte → binaire)
}

POIDS_LAUREAT = 3


# ---------------------------------------------------------------------------
# 2. FONCTIONS
# ---------------------------------------------------------------------------
def calculer_score(df):
    """Calcule score_canon_local à partir des colonnes pondérées."""
    df = df.copy()
    df["score_canon_local"] = 0

    for col, poids in POIDS.items():
        if poids == 0:
            continue
        df["score_canon_local"] += df[col].fillna(0).astype(int) * poids

    # Lauréat : présence = 1 × 3 pts
    df["score_canon_local"] += df["laureat"].notna().astype(int) * POIDS_LAUREAT
    return df


def afficher_stats(df):
    print("\n── Statistiques du score_canon_local ──")
    print(df["score_canon_local"].describe().round(2))
    print(f"\nPoètes avec score = 0 : {(df['score_canon_local'] == 0).sum()}")
    print(f"Poètes avec score > 0 : {(df['score_canon_local'] > 0).sum()}")
    print(f"Score maximum         : {df['score_canon_local'].max()}")
    print("\nTop 20 poètes par score_canon_local :")
    top20 = (df[["nom_canonique", "score_canon_local"]]
             .sort_values("score_canon_local", ascending=False).head(20))
    print(top20.to_string(index=False))


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    df = pd.read_csv(INPUT)
    print(f"Fichier chargé : {len(df)} poètes, {len(df.columns)} colonnes")

    cols_manquantes = [c for c in list(POIDS.keys()) + ["laureat"] if c not in df.columns]
    if cols_manquantes:
        raise ValueError(f"Colonnes manquantes : {cols_manquantes}")

    df = calculer_score(df)
    df.to_csv(OUTPUT, index=False)
    print(f"\n✓ CSV écrit : {OUTPUT}  ({len(df)} lignes)")
    afficher_stats(df)
    return df


if __name__ == "__main__":
    df = main()

    # ── VÉRIFICATIONS ──
    print("\n── Vérifications ──")
    assert len(df) == 618, f"ERREUR : {len(df)} lignes au lieu de 618"
    assert (df["score_canon_local"] < 0).sum() == 0, "ERREUR : scores négatifs"
    assert df["score_canon_local"].max() == 11, \
        f"ERREUR : score max {df['score_canon_local'].max()} ≠ 11"
    # Vérification poids lauréat : un lauréat sans autre source = score ≥ 3
    laureats = df[df["laureat"].notna()]
    assert (laureats["score_canon_local"] >= 3).all(), "ERREUR : poids lauréat"
    print(f"  Lauréats dans le corpus : {len(laureats)} ✓")

    # Test d'acceptation
    ref = pd.read_csv(OUTPUT)
    from pandas.testing import assert_frame_equal
    assert_frame_equal(df.reset_index(drop=True), ref.reset_index(drop=True))
    print("Test d'acceptation : sortie identique à poetes_LA_canon_local_scored.csv ✓")

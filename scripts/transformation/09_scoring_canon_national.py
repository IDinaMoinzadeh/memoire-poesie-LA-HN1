# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT 09 — Scoring canon national → poetes_LA_canon_national_FINAL.csv
================================================================================
INPUT   : revues_nationales_FINAL.csv       (618 poètes, produit par 08b)
          anthologies_nationales_FINAL.csv  (618 poètes, présence Norton/Penguin/BAP)
OUTPUT  : poetes_LA_canon_national_FINAL.csv (618 poètes, scores nationaux complets)

TRANSFORMATIONS :
  1. Fusion des deux CSV sur poet_id.
  2. score_bap : binaire (1 si le poète est dans au moins un volume BAP, 0 sinon).
     Le BAP est traité en présence et non en volume car sa nature annuelle
     le rend incomparable aux anthologies à volume unique.
  3. _bin : colonnes binaires de présence pour chacune des 4 revues.
  4. score_revues_presence : nombre de revues distinctes où le poète apparaît (0-4).
  5. score_anthologies : 2 pts par anthologie (Norton, Penguin, BAP binaire).
     Le poids 2 reflète la hiérarchie canonisation > circulation.
  6. score_national_volume   = score_revues_volume   + score_anthologies
     score_national_presence = score_revues_presence + score_anthologies

NOTE SUR LES DEUX SCORES NATIONAUX :
  - score_national_volume   : composante revues en volume (nb publications cumulées)
  - score_national_presence : composante revues en présence (nb revues distinctes)
  Les deux sont conservés comme dispositif analytique comparatif ; ils ne diffèrent
  que par la composante revues, la composante anthologies étant identique.

POUR RELANCER :
    python3 09_scoring_canon_national.py
================================================================================
"""

import pandas as pd

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES
# ---------------------------------------------------------------------------
INPUT_REVUES      = "revues_nationales_FINAL.csv"
INPUT_ANTHOLOGIES = "anthologies_nationales_FINAL.csv"
OUTPUT_CSV        = "poetes_LA_canon_national_FINAL.csv"

COLONNES_REVUES = [
    "poetry_magazine",
    "american_poetry_review",
    "kenyon_review",
    "prairie_schooner",
]

POIDS_ANTHOLOGIE = 2   # Norton, Penguin et BAP (binaire) valent chacun 2 pts


# ---------------------------------------------------------------------------
# 2. FONCTIONS
# ---------------------------------------------------------------------------
def fusionner(revues_csv, anth_csv):
    """Fusionne les deux CSV sur poet_id."""
    rev  = pd.read_csv(revues_csv)
    anth = pd.read_csv(anth_csv)
    df = pd.merge(
        rev,
        anth[["poet_id", "in_norton", "in_penguin", "nb_bap", "annees_bap", "in_bap"]],
        on="poet_id"
    )
    print(f"  revues      : {len(rev)} lignes")
    print(f"  anthologies : {len(anth)} lignes")
    print(f"  fusionné    : {len(df)} lignes")
    return df


def calculer_scores(df):
    """Ajoute toutes les colonnes de score."""
    # BAP binaire
    df["score_bap"] = df["in_bap"].astype(int)

    # Présence binaire dans chaque revue
    for col in COLONNES_REVUES:
        df[col + "_bin"] = (df[col] != "[]").astype(int)

    # Présence revues = nb de revues distinctes
    df["score_revues_presence"] = df[[c + "_bin" for c in COLONNES_REVUES]].sum(axis=1)

    # Anthologies : 2 pts chacune (Norton, Penguin, BAP binaire)
    df["score_anthologies"] = (
        df["in_norton"] + df["in_penguin"] + df["score_bap"]
    ) * POIDS_ANTHOLOGIE

    # Scores nationaux
    df["score_national_volume"]   = df["score_revues_volume"]   + df["score_anthologies"]
    df["score_national_presence"] = df["score_revues_presence"] + df["score_anthologies"]

    return df


def reordonner(df):
    cols = (
        ["poet_id", "nom_canonique"] +
        [c for pair in [(col, col + "_nb_pub") for col in COLONNES_REVUES] for c in pair] +
        ["score_revues_volume", "in_norton", "in_penguin", "nb_bap", "annees_bap",
         "score_bap"] +
        [col + "_bin" for col in COLONNES_REVUES] +
        ["score_revues_presence", "score_anthologies",
         "score_national_volume", "score_national_presence"]
    )
    return df[cols]


def afficher_stats(df):
    print(f"\nPoètes avec score_national_volume > 0 : {(df['score_national_volume'] > 0).sum()}")
    print(f"Score national max (volume)           : {df['score_national_volume'].max()}")
    print(f"\nTOP 10 (score_national_volume) :")
    top = (df[df["score_national_volume"] > 0]
           .sort_values("score_national_volume", ascending=False)
           .head(10)[["nom_canonique", "score_revues_volume", "score_anthologies",
                       "score_national_volume", "score_national_presence"]])
    print(top.to_string(index=False))


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    print("Chargement et fusion...")
    df = fusionner(INPUT_REVUES, INPUT_ANTHOLOGIES)
    df = calculer_scores(df)
    df = reordonner(df)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✓ CSV écrit : {OUTPUT_CSV}  ({len(df)} lignes)")
    afficher_stats(df)
    return df


if __name__ == "__main__":
    df = main()

    # ── VÉRIFICATIONS ──
    print("\n── Vérifications ──")
    assert len(df) == 618, f"ERREUR : {len(df)} lignes au lieu de 618"
    assert (df["score_bap"] > 1).sum() == 0,         "ERREUR : score_bap non binaire"
    assert (df["score_national_volume"] < 0).sum() == 0, "ERREUR : scores négatifs"
    # Spot-check David St. John (top du classement national)
    dsj = df[df["nom_canonique"] == "David St. John"].iloc[0]
    assert dsj["score_national_volume"] > 0, "ERREUR : David St. John absent"
    print(f"  David St. John — score_national_volume : {dsj['score_national_volume']} ✓")

    # Test d'acceptation contre le CSV final de référence
    ref = pd.read_csv("poetes_LA_canon_national_FINAL.csv")
    from pandas.testing import assert_frame_equal
    assert_frame_equal(df.reset_index(drop=True), ref.reset_index(drop=True),
                       check_dtype=False)
    print("Test d'acceptation : sortie identique à poetes_LA_canon_national_FINAL.csv ✓")

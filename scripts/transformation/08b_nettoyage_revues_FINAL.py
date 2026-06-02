# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT 08b — Nettoyage du corpus + enrichissement → revues_nationales_FINAL.csv
================================================================================
INPUT   : revues_nationales.csv         (622 lignes, produit par 08a)
OUTPUT  : revues_nationales_FINAL.csv   (618 lignes)

TRANSFORMATIONS :
  1. Retrait de 4 poètes identifiés comme cas limites après vérification
     qualitative (voir bloc RETRAITS ci-dessous et commentaires du notebook
     SCORES_canon_NATIONAL.ipynb pour la justification de chaque cas).
  2. Ajout de colonnes _nb_pub (nombre de publications = longueur de la liste
     d'années) pour chacune des 4 revues.
  3. Calcul du score_revues_volume = somme des 4 nb_pub.
  4. Réordonnancement des colonnes.

POUR RELANCER :
    python3 08b_nettoyage_revues_FINAL.py
================================================================================
"""

import ast
import pandas as pd

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES
# ---------------------------------------------------------------------------
INPUT_CSV  = "revues_nationales.csv"
OUTPUT_CSV = "revues_nationales_FINAL.csv"

# Poètes retirés après vérification qualitative des cas limites :
#   Clayton Eshleman  : holdout sans ancrage local, carrière Detroit/NY/France
#   Diane Wakoski     : née à Whittier (LA) mais partie dès les années 1960,
#                       carrière à East Lansing (Michigan), zéro source locale
#   Edward Field      : inclus via Stand Up Poetry (1990) uniquement,
#                       poète principalement new-yorkais
#   Tara Betts        : une seule anthologie (Leimert Park Redux 2017),
#                       profil Chicago
RETRAITS = [
    "Clayton Eshleman",
    "Diane Wakoski",
    "Edward Field",
    "Tara Betts",
]

COLONNES_REVUES = [
    "poetry_magazine",
    "american_poetry_review",
    "kenyon_review",
    "prairie_schooner",
]


# ---------------------------------------------------------------------------
# 2. FONCTIONS
# ---------------------------------------------------------------------------
def nb_publications(valeur):
    """Longueur d'une colonne stockée comme liste d'années (chaîne)."""
    if pd.isna(valeur) or str(valeur).strip() in ("", "[]"):
        return 0
    try:
        return len(ast.literal_eval(str(valeur)))
    except (ValueError, SyntaxError):
        return 0


def enrichir(df):
    """Ajoute les colonnes _nb_pub et score_revues_volume."""
    for col in COLONNES_REVUES:
        df[col + "_nb_pub"] = df[col].apply(nb_publications)
    df["score_revues_volume"] = sum(df[col + "_nb_pub"] for col in COLONNES_REVUES)
    return df


def reordonner(df):
    cols = (["poet_id", "nom_canonique"] +
            COLONNES_REVUES +
            ["score_revues_volume"] +
            [col + "_nb_pub" for col in COLONNES_REVUES])
    return df[cols]


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
    print(f"Corpus initial : {len(df)} poètes")

    # Retrait des cas limites
    masque = df["nom_canonique"].isin(RETRAITS)
    print(f"\nPoètes retirés :")
    for nom in df[masque]["nom_canonique"].values:
        print(f"  - {nom}")
    df = df[~masque].copy().reset_index(drop=True)
    print(f"\nCorpus après nettoyage : {len(df)} poètes")

    df = enrichir(df)
    df = reordonner(df)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n✓ CSV écrit : {OUTPUT_CSV}  ({len(df)} lignes)")

    # Résumé
    print(f"\nPoètes avec au moins 1 publication nationale : "
          f"{(df['score_revues_volume'] > 0).sum()}")
    print(f"Score max (publications cumulées) : {df['score_revues_volume'].max()}")
    return df


if __name__ == "__main__":
    df = main()

    # ── VÉRIFICATIONS ──
    print("\n── Vérifications ──")
    assert len(df) == 618, f"ERREUR : {len(df)} lignes au lieu de 618"
    for nom in ["Clayton Eshleman", "Diane Wakoski", "Edward Field", "Tara Betts"]:
        assert nom not in df["nom_canonique"].values, f"ERREUR : {nom} toujours présent"
    assert (df["score_revues_volume"] < 0).sum() == 0, "ERREUR : scores négatifs"
    assert list(df.columns[:2]) == ["poet_id", "nom_canonique"], "ERREUR : colonnes"

    # Test d'acceptation contre le CSV final de référence
    ref = pd.read_csv("revues_nationales_FINAL.csv", encoding="utf-8-sig")
    from pandas.testing import assert_frame_equal
    assert_frame_equal(df.reset_index(drop=True), ref.reset_index(drop=True))
    print("Test d'acceptation : sortie identique à revues_nationales_FINAL.csv ✓")

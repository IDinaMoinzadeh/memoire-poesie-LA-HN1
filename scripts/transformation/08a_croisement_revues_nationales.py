# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT 08a — Croisement JSTOR × corpus LA → revues_nationales.csv
================================================================================
INPUT   : jstor_auteurs_revues.json     (produit par l'étape d'acquisition :
                                          croisement_revues-nationales.ipynb, cellule 1 ;
                                          lit le fichier JSTOR de 1.29 Go et extrait
                                          les publications par poète et par revue)
          poetes_LA.csv                 (corpus de 622 poètes, version pré-nettoyage)
OUTPUT  : revues_nationales.csv         (622 lignes : listes d'années de publication
                                          par revue pour chaque poète)

ÉTAPE SUIVANTE : 08b_nettoyage_revues_FINAL.py
  → produit revues_nationales_FINAL.csv (618 lignes) en retirant 4 cas limites
    et en ajoutant les colonnes _nb_pub et score_revues_volume.

NOTE sur l'acquisition (non reproductible à l'identique) :
  La cellule 1 de croisement_revues-nationales.ipynb lit le fichier
  jstor_metadata_2026-05-03.jsonl.gz (1.29 Go, ~5 min), croise les auteurs
  avec le corpus et écrit jstor_auteurs_revues.json. Cette étape dépend du
  fichier JSTOR figé ; pour reproduire, relancer la cellule 1 du notebook
  avec le fichier .jsonl.gz en place.

CORRECTION MANUELLE intégrée :
  Xochitl-Julisa Bermejo : APR 2015 (publication vérifiée manuellement,
  absente de JSTOR à cause d'une graphie du nom différente dans les métadonnées).

POUR RELANCER :
    python3 08a_croisement_revues_nationales.py
================================================================================
"""

import json
import pandas as pd

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES
# ---------------------------------------------------------------------------
INPUT_JSON   = "jstor_auteurs_revues.json"
INPUT_POETES = "poetes_LA.csv"
OUTPUT_CSV   = "revues_nationales.csv"

REVUES = {
    "poetry":                    "poetry_magazine",
    "the american poetry review": "american_poetry_review",
    "the kenyon review":          "kenyon_review",
    "prairie schooner":           "prairie_schooner",
}

# Corrections manuelles : {revue_jstor: {nom_canonique: [années]}}
CORRECTIONS = {
    "the american poetry review": {
        "Xochitl-Julisa Bermejo": [2015],
    }
}


# ---------------------------------------------------------------------------
# 2. FONCTIONS
# ---------------------------------------------------------------------------
def charger_et_corriger_json(chemin, corrections):
    """Charge le JSON JSTOR et applique les corrections manuelles."""
    with open(chemin, "r", encoding="utf-8") as f:
        jstor = json.load(f)
    for revue, auteurs in corrections.items():
        for auteur, annees in auteurs.items():
            if auteur not in jstor[revue]:
                jstor[revue][auteur] = annees
            else:
                for a in annees:
                    if a not in jstor[revue][auteur]:
                        jstor[revue][auteur].append(a)
            print(f"✓ Correction appliquée : {auteur} — {revue} {annees}")
    return jstor


def croiser(df_poetes, jstor, revues):
    """Pour chaque poète, récupère les années de publication dans chaque revue."""
    rows = []
    for _, row in df_poetes.iterrows():
        nom = str(row["nom_canonique"])
        nom_lower = nom.lower()
        entry = {"poet_id": int(row["poet_id"]), "nom_canonique": nom}
        for revue_jstor, col in revues.items():
            annees = []
            for auteur_jstor, annees_jstor in jstor.get(revue_jstor, {}).items():
                if auteur_jstor.lower() == nom_lower:
                    annees = sorted(annees_jstor)
                    break
            entry[col] = str(annees) if annees else "[]"
        rows.append(entry)
    return pd.DataFrame(rows, columns=["poet_id", "nom_canonique"] + list(revues.values()))


def afficher_stats(df, revues):
    """Résumé : présences par revue et top 10."""
    print("\n── Présences dans les revues nationales ──")
    for col in revues.values():
        n = (df[col] != "[]").sum()
        print(f"  {col:30s} : {n} poètes")
    df2 = df.copy()
    df2["nb_revues"] = df2[list(revues.values())].apply(
        lambda r: sum(1 for v in r if v != "[]"), axis=1)
    top = (df2[df2["nb_revues"] > 0]
           .sort_values("nb_revues", ascending=False)
           .head(10)[["nom_canonique", "nb_revues"] + list(revues.values())])
    print("\n── Top 10 poètes (présences cumulées) ──")
    print(top.to_string(index=False))


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    jstor = charger_et_corriger_json(INPUT_JSON, CORRECTIONS)
    df_poetes = pd.read_csv(INPUT_POETES, encoding="utf-8-sig")
    print(f"\n{len(df_poetes)} poètes chargés depuis {INPUT_POETES}")
    df_out = croiser(df_poetes, jstor, REVUES)
    df_out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n✓ CSV écrit : {OUTPUT_CSV}  ({len(df_out)} lignes)")
    afficher_stats(df_out, REVUES)
    return df_out


if __name__ == "__main__":
    df = main()

    # ── VÉRIFICATIONS ──
    print("\n── Vérifications ──")
    print("Lignes :", len(df), "(attendu : 622)")
    assert len(df) == 622, f"ERREUR : {len(df)} lignes au lieu de 622"
    assert (df["poetry_magazine"] != "[]").sum() == 67,   "ERREUR : Poetry Magazine"
    assert (df["american_poetry_review"] != "[]").sum() == 50, "ERREUR : APR"
    assert (df["kenyon_review"] != "[]").sum() == 33,     "ERREUR : Kenyon Review"
    assert (df["prairie_schooner"] != "[]").sum() == 56,  "ERREUR : Prairie Schooner"
    # Vérification Xochitl-Julisa Bermejo (correction manuelle)
    row = df[df["nom_canonique"] == "Xochitl-Julisa Bermejo"].iloc[0]
    assert "2015" in row["american_poetry_review"], "ERREUR : correction Bermejo absente"
    print("Tous les contrôles passent ✓")

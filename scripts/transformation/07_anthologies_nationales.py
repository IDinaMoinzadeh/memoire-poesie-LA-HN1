# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT 07 — Croisement anthologies nationales → anthologies_nationales_FINAL.csv
================================================================================
INPUT   : poetes_LA_canon_local.csv       (618 poètes, index de base)
          bap_poetes_clean.csv             (Best American Poetry 1988-2024, scraping)
          input_norton_gioia_raw.txt        (table des matières Norton Anthology of
                                             Poetry, éd. Gioia, collée manuellement)
          + liste Penguin écrite en dur ci-dessous (OCR manuel)
OUTPUT  : anthologies_nationales_FINAL.csv (618 poètes, présence dans 3 anthologies)

COLONNES PRODUITES :
  in_norton  : 1 si le poète figure dans le Norton Anthology of Poetry (Gioia)
  in_penguin : 1 si le poète figure dans le Penguin (Dove, 2011)
  in_bap     : 1 si le poète a été sélectionné au moins une fois dans le BAP
  annees_bap : années de sélection dans le BAP (chaîne CSV triée)
  nb_bap     : nombre d'années de sélection dans le BAP
  score_anthologies_presence : in_norton + in_penguin + in_bap (0-3)

MÉTHODE D'APPARIEMENT :
  - Norton Gioia : correspondance par SOUS-CHAÎNE dans le texte collé,
    après normalisation (minuscules, ponctuation → espaces, espaces compactés).
    Cohérent avec la méthode de viz7.
  - Penguin      : correspondance EXACTE sur le nom normalisé
    (minuscules, caractères non-alphabétiques supprimés, espaces compactés).
  - BAP          : même normalisation que Penguin.

NOTE SUR LES COMPTES (voir note de bas de page du mémoire) :
  Les comptes automatiques (Norton=1, Penguin=3, BAP=41) correspondent aux
  comptes manuels de référence. La méthode de normalisation plus stricte
  ici (suppression des apostrophes, tirets, accents) évite le faux positif
  qui apparaissait avec la normalisation plus permissive de viz7 (Penguin=4).

POUR RELANCER :
    python3 07_anthologies_nationales.py
================================================================================
"""

import re
import pandas as pd

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES
# ---------------------------------------------------------------------------
INPUT_LOCAL        = "poetes_LA_canon_local.csv"
INPUT_BAP          = "bap_poetes_clean.csv"
INPUT_NORTON_GIOIA = "input_norton_gioia_raw.txt"
OUTPUT_CSV         = "anthologies_nationales_FINAL.csv"

# Penguin Anthology of Twentieth-Century American Poetry, éd. Rita Dove (2011)
# Source : OCR manuel du sommaire
PENGUIN = [
    "Edgar Lee Masters","Edwin Arlington Robinson","James Weldon Johnson",
    "Paul Laurence Dunbar","Robert Frost","Amy Lowell","Gertrude Stein",
    "Alice Moore Dunbar-Nelson","Carl Sandburg","Wallace Stevens",
    "Angelina Weld Grimke","William Carlos Williams","Sara Teasdale",
    "Ezra Pound","Hilda Doolittle","Robinson Jeffers","Marianne Moore",
    "T. S. Eliot","Claude McKay","Archibald MacLeish","Edna St. Vincent Millay",
    "E. E. Cummings","Jean Toomer","Louise Bogan","Melvin B. Tolson",
    "Hart Crane","Robert Francis","Langston Hughes","Countee Cullen",
    "Stanley Kunitz","W. H. Auden","Theodore Roethke","Charles Olson",
    "Elizabeth Bishop","Robert Hayden","Muriel Rukeyser","Delmore Schwartz",
    "John Berryman","Randall Jarrell","Weldon Kees","Dudley Randall",
    "William Stafford","Ruth Stone","Margaret Walker","Gwendolyn Brooks",
    "Robert Lowell","Robert Duncan","Lawrence Ferlinghetti","William Meredith",
    "Howard Nemerov","Richard Wilbur","James Dickey","Alan Dugan",
    "Anthony Hecht","Richard Hugo","Denise Levertov","Louis Simpson",
    "Carolyn Kizer","Kenneth Koch","Maxine Kumin","Gerald Stern",
    "A. R. Ammons","Robert Bly","Robert Creeley","James Merrill",
    "Frank O'Hara","John Ashbery","Galway Kinnell","W. S. Merwin",
    "James Wright","Donald Hall","Philip Levine","Michael S. Harper",
    "Charles Simic","Paula Gunn Allen","Frank Bidart","Carl Dennis",
    "Stephen Dunn","Robert Pinsky","James Welch","Billy Collins",
    "Toi Derricotte","Stephen Dobyns","Robert Hass","Lyn Hejinian",
    "B. H. Fairchild","Haki R. Madhubuti","William Matthews","Sharon Olds",
    "Henry Taylor","Tess Gallagher","Michael Palmer","James Tate",
    "Norman Dubie","Carol Muske-Dukes","Mary Oliver","Charles Wright",
    "Lucille Clifton","June Jordan","Frederick Seidel","C. K. Williams",
    "Diane Wakoski","Miller Williams","Etheridge Knight","Amiri Baraka",
    "Ted Berrigan","Audre Lorde","Sonia Sanchez","Mark Strand",
    "Russell Edson","Nathaniel Mackey","Gregory Orr","Roberta Hill Whiteman",
    "Albert Goldbarth","Heather McHugh","Leslie Marmon Silko","Olga Broumas",
    "Victor Hernandez Cruz","Jane Miller","David St. John","C. D. Wright",
    "Carolyn Forche","Jorie Graham","Marie Howe","Joy Harjo",
    "Garrett Hongo","Andrew Hudgins","Brigit Pegeen Kelly","Paul Muldoon",
    "Judith Ortiz Cofer","Rita Dove","Alice Fulton","Barbara Hamby",
    "Mark Jarman","Naomi Shihab Nye","Alberto Rios","Laurie Sheck",
    "Gary Soto","Susan Stewart","Mark Doty","Harryette Mullen",
    "Franz Wright","Lorna Dee Cervantes","Sandra Cisneros","Cornelius Eady",
    "Louise Erdrich","David Mason","Marilyn Chin","Cathy Song",
    "Annie Finch","Li-Young Lee","Carl Phillips","Nick Flynn",
    "Elizabeth Alexander","Reetika Vazirani","Sherman Alexie",
    "Natasha Trethewey","A. E. Stallings","Joanna Klink",
    "Brenda Shaughnessy","Kevin Young","Terrance Hayes",
]


# ---------------------------------------------------------------------------
# 2. FONCTIONS
# ---------------------------------------------------------------------------
def normaliser(nom):
    """Normalisation stricte : minuscules, caractères non-alpha supprimés."""
    if not isinstance(nom, str):
        return ""
    nom = nom.lower().strip()
    nom = re.sub(r"[^a-z\s]", "", nom)
    return re.sub(r"\s+", " ", nom).strip()


def norm_gioia(s):
    """Normalisation viz7 : minuscules, ponctuation → espaces."""
    s = str(s).lower().strip()
    s = s.replace(".", " ").replace(",", " ").replace("-", " ")
    return re.sub(r"\s+", " ", s).strip()


def croiser_norton_gioia(df, chemin_gioia):
    """Correspondance par sous-chaîne dans le texte Norton/Gioia."""
    blob = norm_gioia(open(chemin_gioia, encoding="utf-8").read())
    df["in_norton"] = df["nom_canonique"].apply(
        lambda n: int(norm_gioia(n) in blob)
    )
    return df


def croiser_penguin(df, penguin):
    """Correspondance exacte sur nom normalisé (normalisation stricte)."""
    penguin_norms = set(normaliser(n) for n in penguin)
    df["in_penguin"] = df["nom_norm"].apply(lambda n: int(n in penguin_norms))
    return df


def croiser_bap(df, chemin_bap):
    """Correspondance exacte sur nom normalisé ; résumé par poète."""
    df_bap = pd.read_csv(chemin_bap)
    df_bap["nom_norm"] = df_bap["nom_poete"].apply(normaliser)
    matches = df_bap.merge(df[["nom_canonique", "nom_norm"]], on="nom_norm", how="inner")
    resume = matches.groupby("nom_canonique").agg(
        annees_bap=("annee", lambda x: ",".join(map(str, sorted(x.unique())))),
        nb_bap=("annee", "nunique"),
    ).reset_index()
    df = df.merge(resume, on="nom_canonique", how="left")
    df["annees_bap"] = df["annees_bap"].where(df["annees_bap"].notna(), other=pd.NA)
    df["nb_bap"] = df["nb_bap"].fillna(0).astype(int)
    df["in_bap"] = (df["nb_bap"] > 0).astype(int)
    return df


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    df = pd.read_csv(INPUT_LOCAL)
    df["nom_norm"] = df["nom_canonique"].apply(normaliser)
    print(f"Corpus : {len(df)} poètes")

    df = croiser_norton_gioia(df, INPUT_NORTON_GIOIA)
    df = croiser_penguin(df, PENGUIN)
    df = croiser_bap(df, INPUT_BAP)

    df["score_anthologies_presence"] = df["in_norton"] + df["in_penguin"] + df["in_bap"]

    cols = ["poet_id", "nom_canonique", "in_norton", "in_penguin",
            "in_bap", "annees_bap", "nb_bap", "score_anthologies_presence"]
    df_out = df[cols]
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✓ CSV écrit : {OUTPUT_CSV}  ({len(df_out)} lignes)")
    print(f"  in_norton  : {df_out['in_norton'].sum()} (Dana Gioia)")
    print(f"  in_penguin : {df_out['in_penguin'].sum()} (Paula Gunn Allen, David St. John, Carol Muske-Dukes)")
    print(f"  in_bap     : {df_out['in_bap'].sum()} poètes")
    print(f"  nb_bap max : {df_out['nb_bap'].max()} (David St. John)")
    return df_out


if __name__ == "__main__":
    df = main()

    # ── VÉRIFICATIONS ──
    print("\n── Vérifications ──")
    assert len(df) == 618,               "ERREUR : nombre de poètes"
    assert df["in_norton"].sum() == 1,   "ERREUR : in_norton"
    assert df["in_penguin"].sum() == 3,  "ERREUR : in_penguin"
    assert df["in_bap"].sum() == 41,     "ERREUR : in_bap"
    assert df[df["nom_canonique"] == "Dana Gioia"]["in_norton"].iloc[0] == 1
    assert df[df["nom_canonique"] == "David St. John"]["in_penguin"].iloc[0] == 1

    # Test d'acceptation
    ref = pd.read_csv(OUTPUT_CSV)
    from pandas.testing import assert_frame_equal
    assert_frame_equal(df.reset_index(drop=True), ref.reset_index(drop=True),
                       check_dtype=False)
    print("Test d'acceptation : sortie identique à anthologies_nationales_FINAL.csv ✓")

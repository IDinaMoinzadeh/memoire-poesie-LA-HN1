# -*- coding: utf-8 -*-
"""
================================================================================
VISUALISATION 7 — Présence dans les anthologies nationales : SF vs LA
================================================================================
INPUT   : input_poetes_LA_canon_local_scored.csv   (les 618 poètes de LA)
          bap_poetes_clean.csv                        (Best American Poetry 1988-2024)
          input_norton_gioia_raw.txt                  (table des matières Norton/Gioia collée)
          + deux listes écrites en dur ci-dessous : Norton Moderne & Contemporaine, Penguin
OUTPUT  : viz7_anthologies_SF_vs_LA.png               (figure : barres groupées en %)
          viz7_anthologies_SF_vs_LA.csv                (% et effectifs par anthologie)
          viz7_anthologies_detail_noms.csv             (noms exacts trouvés, par anthologie)

OBJECTIF : pour chaque anthologie, comparer le POURCENTAGE de chaque scène présent.
  - SF : les 12 poètes canoniques de la SF Renaissance (poets.org)
  - LA : les 618 poètes du corpus
On affiche un % (et non un effectif brut) pour neutraliser la différence de taille
des deux listes (12 vs 618). Comparaison symétrique : le même ouvrage filtre les
deux scènes.

NOTE (assumée, voir note de bas de page du mémoire) : les comptes LA Penguin (4) et
BAP (42) sont ceux de l'appariement automatique de noms ; ils diffèrent des comptes
manuels de référence (3 et 41) à cause d'un faux positif de chaque côté. On les
conserve ici pour préserver la symétrie de méthode entre SF et LA.

Anthologies et méthode d'appariement :
  - Norton Moderne & Contemporaine (liste collée, Wikipedia)        [exact]
  - Norton Anthology of Poetry / "Gioia" (table des matières collée) [sous-chaîne]
  - Penguin (Dove, 2011, OCR)                                        [exact]
  - Best American Poetry 1988-2024 (scraping)                        [exact]

POUR RELANCER : ajustez le bloc PARAMÈTRES ci-dessous, puis
    python3 07_viz_anthologies_SF_vs_LA.py
================================================================================
"""

import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES
# ---------------------------------------------------------------------------
INPUT_LOCAL        = "input_poetes_LA_canon_local_scored.csv"
INPUT_BAP          = "bap_poetes_clean.csv"
INPUT_NORTON_GIOIA = "input_norton_gioia_raw.txt"
OUT_PNG    = "viz7_anthologies_SF_vs_LA.png"
OUT_CSV    = "viz7_anthologies_SF_vs_LA.csv"
OUT_DETAIL = "viz7_anthologies_detail_noms.csv"

COUL_SF = "#2166ac"   # bleu
COUL_LA = "#e66101"   # orange

# Les 12 poètes canoniques de la SF Renaissance (poets.org)
SF12 = ["Q. R. Hand, Jr.", "Madeline Gleason", "John Wieners", "Helen Adam", "James Merrill",
        "Gary Snyder", "Allen Ginsberg", "David Meltzer", "Jack Spicer", "Kenneth Rexroth",
        "Robert Duncan", "Thom Gunn"]

# (a) Norton Moderne & Contemporaine — liste collée (Wikipedia)
NORTON_MC = """Walt Whitman; Emily Dickinson; Thomas Hardy; Gerard Manley Hopkins; A. E. Housman; William Butler Yeats; Rudyard Kipling; Edgar Lee Masters; Edwin Arlington Robinson; Gertrude Stein; Amy Lowell; Robert Frost; Carl Sandburg; Edward Thomas; Wallace Stevens; Mina Loy; William Carlos Williams; Elinor Wylie; D. H. Lawrence; Ezra Pound; Siegfried Sassoon; H.D.; Robinson Jeffers; Edwin Muir; Edith Sitwell; Marianne Moore; John Crowe Ransom; T. S. Eliot; Ivor Gurney; Claude McKay; Isaac Rosenberg; Edna St. Vincent Millay; Archibald MacLeish; Hugh MacDiarmid; Wilfred Owen; Dorothy Parker; Charles Reznikoff; E. E. Cummings; Jean Toomer; Robert Graves; David Jones; Austin Clarke; Louise Bogan; Melvin Tolson; Hart Crane; Allen Tate; Basil Bunting; Yvor Winters; Laura Riding; Sterling Brown; Langston Hughes; Stevie Smith; Lorine Niedecker; Countee Cullen; Louis Zukofsky; Richard Eberhart; C. Day-Lewis; Patrick Kavanagh; Robert Penn Warren; Stanley Kunitz; Kenneth Rexroth; John Betjeman; William Empson; W. H. Auden; A. D. Hope; Louis MacNeice; George Oppen; Theodore Roethke; Stephen Spender; Keith Douglas; Charles Olson; Elizabeth Bishop; May Swenson; Robert Hayden; Karl Shapiro; Delmore Schwartz; Muriel Rukeyser; William Stafford; Randall Jarrell; John Berryman; Dylan Thomas; Judith Wright; P. K. Page; Robert Lowell; Gwendolyn Brooks; Robert Duncan; William Meredith; Lawrence Ferlinghetti; Louise Bennett; Howard Nemerov; Amy Clampitt; Richard Wilbur; Kingsley Amis; Donald Davie; Philip Larkin; Anthony Hecht; James Dickey; Alan Dugan; Louis Simpson; Denise Levertov; Richard Hugo; Kenneth Koch; Maxine Kumin; Donald Justice; W. D. Snodgrass; A. R. Ammons; James Merrill; Robert Creeley; Allen Ginsberg; Frank O'Hara; Robert Bly; Charles Tomlinson; Galway Kinnell; John Ashbery; W. S. Merwin; James Wright; Philip Levine; Thomas Kinsella; Anne Sexton; A. K. Ramanujan; Richard Howard; Adrienne Rich; Thom Gunn; John Hollander; Derek Walcott; Gary Snyder; Kamau Brathwaite; Christopher Okigbo; Ted Hughes; Okot p'Bitek; Geoffrey Hill; Sylvia Plath; Mark Strand; Wole Soyinka; Amiri Baraka; Charles Wright; Mary Oliver; Marge Piercy; Lucille Clifton; June Jordan; Tony Harrison; Susan Howe; Michael S. Harper; Charles Simic; Les Murray; Seamus Heaney; Frank Bidart; Michael Longley; Margaret Atwood; Eunice De Souza; Robert Pinsky; Robert Hass; Lyn Hejinian; Derek Mahon; Sharon Olds; Marilyn Hacker; Dave Smith; Louise Gluck; Michael Palmer; Michael Ondaatje; James Tate; Eavan Boland; Craig Raine; Norman Dubie; Yusef Komunyakaa; Lorna Goodison; Ai; Leslie Marmon Silko; Agha Shahid Ali; James Fenton; Grace Nichols; Charles Bernstein; Carolyn Forche; Jorie Graham; Anne Carson; Medbh McGuckian; Joy Harjo; Paul Muldoon; Gary Soto; Rita Dove; Alberto Rios; Mark Doty; Thylias Moss; Louise Erdrich; Lorna Dee Cervantes; Marilyn Chin; Cathy Song; Carol Ann Duffy; Dionisio D. Martinez; Henri Cole; Li-Young Lee; Sherman Alexie"""

# (b) Penguin (Dove, 2011) — liste OCR
PENGUIN = ["Edgar Lee Masters","Edwin Arlington Robinson","James Weldon Johnson","Paul Laurence Dunbar","Robert Frost","Amy Lowell","Gertrude Stein","Alice Moore Dunbar-Nelson","Carl Sandburg","Wallace Stevens","Angelina Weld Grimké","William Carlos Williams","Sara Teasdale","Ezra Pound","Hilda Doolittle","Robinson Jeffers","Marianne Moore","T. S. Eliot","Claude McKay","Archibald MacLeish","Edna St. Vincent Millay","E. E. Cummings","Jean Toomer","Louise Bogan","Melvin B. Tolson","Hart Crane","Robert Francis","Langston Hughes","Countee Cullen","Stanley Kunitz","W. H. Auden","Theodore Roethke","Charles Olson","Elizabeth Bishop","Robert Hayden","Muriel Rukeyser","Delmore Schwartz","John Berryman","Randall Jarrell","Weldon Kees","Dudley Randall","William Stafford","Ruth Stone","Margaret Walker","Gwendolyn Brooks","Robert Lowell","Robert Duncan","Lawrence Ferlinghetti","William Meredith","Howard Nemerov","Richard Wilbur","James Dickey","Alan Dugan","Anthony Hecht","Richard Hugo","Denise Levertov","Louis Simpson","Carolyn Kizer","Kenneth Koch","Maxine Kumin","Gerald Stern","A. R. Ammons","Robert Bly","Robert Creeley","James Merrill","Frank O'Hara","John Ashbery","Galway Kinnell","W. S. Merwin","James Wright","Donald Hall","Philip Levine","Michael S. Harper","Charles Simic","Paula Gunn Allen","Frank Bidart","Carl Dennis","Stephen Dunn","Robert Pinsky","James Welch","Billy Collins","Toi Derricotte","Stephen Dobyns","Robert Hass","Lyn Hejinian","B. H. Fairchild","Haki R. Madhubuti","William Matthews","Sharon Olds","Henry Taylor","Tess Gallagher","Michael Palmer","James Tate","Norman Dubie","Carol Muske-Dukes","Mary Oliver","Charles Wright","Lucille Clifton","June Jordan","Frederick Seidel","C. K. Williams","Diane Wakoski","Miller Williams","Etheridge Knight","Amiri Baraka","Ted Berrigan","Audre Lorde","Sonia Sanchez","Mark Strand","Russell Edson","Nathaniel Mackey","Gregory Orr","Roberta Hill Whiteman","Albert Goldbarth","Heather McHugh","Leslie Marmon Silko","Olga Broumas","Victor Hernández Cruz","Jane Miller","David St. John","C. D. Wright","Carolyn Forché","Jorie Graham","Marie Howe","Joy Harjo","Garrett Hongo","Andrew Hudgins","Brigit Pegeen Kelly","Paul Muldoon","Judith Ortiz Cofer","Rita Dove","Alice Fulton","Barbara Hamby","Mark Jarman","Naomi Shihab Nye","Alberto Ríos","Laurie Sheck","Gary Soto","Susan Stewart","Mark Doty","Harryette Mullen","Lorna Dee Cervantes","Sandra Cisneros","Cornelius Eady","Louise Erdrich","David Mason","Marilyn Chin","Cathy Song","Annie Finch","Li-Young Lee","Carl Phillips","Nick Flynn","Elizabeth Alexander","Reetika Vazirani","Sherman Alexie","Natasha Trethewey","A. E. Stallings","Joanna Klink","Brenda Shaughnessy","Kevin Young","Terrance Hayes"]


# ---------------------------------------------------------------------------
# 2. FONCTIONS
# ---------------------------------------------------------------------------
def norm(s):
    """Normalise un nom : minuscules, ponctuation retirée, espaces compactés."""
    s = str(s).lower().strip().replace('.', ' ').replace(',', ' ').replace('-', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def charger_groupes():
    """Renvoie les 618 noms LA (les 12 SF sont dans la constante SF12)."""
    la = pd.read_csv(INPUT_LOCAL)[['nom_canonique']]
    return la


def charger_anthologies():
    """Construit les quatre sources d'appariement (deux ensembles exacts, un set BAP, un blob Gioia)."""
    norton_mc_set = set(norm(n) for n in NORTON_MC.split(";") if n.strip())
    penguin_set   = set(norm(p) for p in PENGUIN)
    bap = pd.read_csv(INPUT_BAP)
    bap_set = set(bap['nom_poete'].apply(norm))
    # Norton Anthology of Poetry ("Gioia") : on cherche chaque nom comme SOUS-CHAÎNE du texte collé.
    gioia_blob = norm(open(INPUT_NORTON_GIOIA).read())
    return norton_mc_set, penguin_set, bap_set, gioia_blob


def presents_exact(noms, ensemble):
    return [n for n in noms if norm(n) in ensemble]


def presents_souschaine(noms, blob):
    return [n for n in noms if norm(n) in blob]


def calculer_presence(la, norton_mc_set, penguin_set, bap_set, gioia_blob):
    """Pour chaque anthologie, compte SF et LA présents (% sur 12 et sur 618)."""
    la_noms = la['nom_canonique'].tolist()
    config = [
        ("Norton Moderne\n& Contemporaine", "exact", norton_mc_set, False),
        ("Norton Anthology\nof Poetry (Gioia)", "souschaine", gioia_blob, True),
        ("Penguin\n(Dove, 2011)", "exact", penguin_set, False),
        ("Best American\nPoetry (1988-2024)", "exact", bap_set, False),
    ]
    resultats, detail = [], []
    for nom_anth, methode, source, est_general in config:
        if methode == "exact":
            sf_p = presents_exact(SF12, source); la_p = presents_exact(la_noms, source)
        else:
            sf_p = presents_souschaine(SF12, source); la_p = presents_souschaine(la_noms, source)
        resultats.append({'anthologie': nom_anth.replace("\n", " "),
                          'SF_presents': len(sf_p), 'SF_pct': 100*len(sf_p)/12,
                          'LA_presents': len(la_p), 'LA_pct': 100*len(la_p)/618,
                          'general_anglophone': est_general})
        for p in sf_p: detail.append({'anthologie': nom_anth.replace("\n", " "), 'groupe': 'SF', 'poete': p})
        for p in la_p: detail.append({'anthologie': nom_anth.replace("\n", " "), 'groupe': 'LA', 'poete': p})
    return pd.DataFrame(resultats), pd.DataFrame(detail), config


def sauvegarder_donnees(res, detail):
    res.to_csv(OUT_CSV, index=False, encoding='utf-8')
    detail.to_csv(OUT_DETAIL, index=False, encoding='utf-8')


def tracer_figure(res, config):
    """Barres groupées en %, Gioia hachuré (anthologie générale anglophone)."""
    labels = [c[0] for c in config]
    x = np.arange(len(labels)); largeur = 0.38
    fig, ax = plt.subplots(figsize=(13, 7))

    for i, r in res.iterrows():
        # SF (bleu), LA (orange) ; Gioia hachuré pour rappeler la source/format différent
        hatch = '//' if r['general_anglophone'] else None
        ax.bar(i - largeur/2, r['SF_pct'], largeur, color='#2166ac', hatch=hatch, edgecolor='white')
        ax.bar(i + largeur/2, r['LA_pct'], largeur, color='#e66101', hatch=hatch, edgecolor='white')
        ax.text(i - largeur/2, r['SF_pct'] + 1, f"{r['SF_presents']}/12", ha='center', fontsize=9, color='#2166ac', fontweight='bold')
        ax.text(i + largeur/2, r['LA_pct'] + 1, f"{r['LA_presents']}/618", ha='center', fontsize=9, color='#e66101', fontweight='bold')

    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("% du groupe présent dans l'anthologie")
    ax.set_ylim(0, max(res['SF_pct'].max(), res['LA_pct'].max()) + 12)
    ax.set_title("Présence dans les anthologies nationales : SF Renaissance vs Los Angeles\n"
                 "(en % de chaque groupe ; effectifs présents indiqués sur les barres)", fontsize=13, pad=12)
    leg = [mpatches.Patch(color='#2166ac', label='SF Renaissance (12)'),
           mpatches.Patch(color='#e66101', label='Los Angeles (618)'),
           mpatches.Patch(facecolor='white', edgecolor='gray', hatch='//', label='anthologie générale anglophone (hachuré)')]
    ax.legend(handles=leg, frameon=False, fontsize=9, loc='upper right')
    for c in ['top', 'right']:
        ax.spines[c].set_visible(False)
    ax.grid(True, axis='y', ls=':', alpha=0.4)
    ax.text(0.5, -0.17,
            "Note : le BAP est contemporain (1988-2024) ; la SF Renaissance, mouvement des années 1950-60, y est mécaniquement peu présente.\n"
            "Les deux Norton incluent aussi des poètes britanniques/irlandais ; le Norton Anthology of Poetry est repris d'une table des matières collée (partie moderne).",
            transform=ax.transAxes, ha='center', va='top', fontsize=8, color='#555', style='italic')

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=150, bbox_inches='tight')


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    la = charger_groupes()
    norton_mc_set, penguin_set, bap_set, gioia_blob = charger_anthologies()
    res, detail, config = calculer_presence(la, norton_mc_set, penguin_set, bap_set, gioia_blob)
    print(res[['anthologie', 'SF_presents', 'SF_pct', 'LA_presents', 'LA_pct']].to_string(index=False))
    sauvegarder_donnees(res, detail)
    tracer_figure(res, config)
    print("\nFigure  ->", OUT_PNG)
    print("Données ->", OUT_CSV, "+", OUT_DETAIL)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
================================================================================
VISUALISATION 6 — SF Renaissance vs canon LOCAL de LA (sans le prix de lauréat)
================================================================================
INPUT   : input_jstor_auteurs_revues_poesie_v2.csv   (dépouillement JSTOR, 4 revues)
          input_poetes_LA_canon_local_scored.csv       (canon local scoré)
OUTPUT  : viz6_SF_vs_LA_local.png                       (figure : deux panneaux)
          viz6_SF_vs_LA_local_volumes.csv                (données : 12 + 12 poètes)

OBJECTIF : comparaison la plus défendable. De chaque côté, on prend les poètes
consacrés par leur SCÈNE, puis on mesure leur présence dans les revues nationales.
  - SF : les 12 poètes canoniques de la SF Renaissance (poets.org)
  - LA : les 12 plus canoniques AU LOCAL, le prix de poète lauréat étant retiré
         (ce prix, créé en 2011, gonfle des poètes récents et fausserait la
          comparaison temporelle avec un mouvement des années 1950-70).
On ne sélectionne donc PLUS les poètes de LA sur leur succès national (biais de la
figure précédente) : on les sélectionne sur le local, puis on regarde le national.

MÉTHODE de comptage (identique des deux côtés) : doublons JSTOR retirés +
correspondance exacte prénom+nom.

POUR RELANCER : ajustez le bloc PARAMÈTRES ci-dessous, puis
    python3 06_viz_SF_vs_LA_revues.py
================================================================================
"""

import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. PARAMÈTRES
# ---------------------------------------------------------------------------
INPUT_JSTOR = "input_jstor_auteurs_revues_poesie_v2.csv"
INPUT_LOCAL = "input_poetes_LA_canon_local_scored.csv"
OUT_PNG = "viz6_SF_vs_LA_local.png"
OUT_CSV = "viz6_SF_vs_LA_local_volumes.csv"

POETES_SF = ["Q. R. Hand, Jr.", "Madeline Gleason", "John Wieners", "Helen Adam",
             "James Merrill", "Gary Snyder", "Allen Ginsberg", "David Meltzer",
             "Jack Spicer", "Kenneth Rexroth", "Robert Duncan", "Thom Gunn"]

POIDS_LAUREAT = 3
COUL_SF = "#2166ac"   # bleu
COUL_LA = "#e66101"   # orange

# colonnes de présence locale (pour départager les ex aequo)
COLS_PRESENCE = ['anth_Buk_Vang_1972','streets_inside_1978','poetry_loves_poetry_1985',
    'invocation_LA_1989','grand_passion_1995','stand_up_1990','stand_up_2002','leimert_park_2006',
    'wide_awake_2015','cross_strokes_2015','coiled_serpent_2016','leimert_park_redux_2017',
    'workshop_beyond_baroque_2018','lapl_list','mohr_blog_absents']


# ---------------------------------------------------------------------------
# 2. FONCTIONS
# ---------------------------------------------------------------------------
def charger_jstor(chemin):
    """Charge JSTOR, retire les doublons, prépare la clé prénom+nom normalisée."""
    j = pd.read_csv(chemin).drop_duplicates(
        subset=['revue', 'annee', 'titre', 'auteur_complet']).copy()
    j['pn_norm'] = (j['prenom'].fillna('').astype(str).str.strip() + ' ' +
                    j['nom'].fillna('').astype(str).str.strip()).str.lower().str.strip()
    return j


def faire_compteur(j):
    """Renvoie une fonction volume(nom) = nb de publications JSTOR (appariement exact)."""
    def volume(nom):
        return int((j['pn_norm'] == str(nom).lower().strip()).sum())
    return volume


def liste_sf(volume):
    """Les 12 SF + leur volume national."""
    sf = pd.DataFrame({'poete': POETES_SF})
    sf['volume'] = sf['poete'].apply(volume)
    return sf


def liste_la(chemin_local, volume):
    """Les 12 plus canoniques AU LOCAL (hors lauréat) + leur volume national."""
    loc = pd.read_csv(chemin_local)
    loc['est_laureat'] = loc['laureat'].notna().astype(int)
    loc['score_local_sans_laureat'] = loc['score_canon_local'] - POIDS_LAUREAT * loc['est_laureat']
    loc['largeur'] = loc[COLS_PRESENCE].sum(axis=1)
    top12 = loc.sort_values(['score_local_sans_laureat', 'largeur', 'nom_famille'],
                            ascending=[False, False, True]).head(12)
    la = pd.DataFrame({'poete': top12['nom_canonique'].values})
    la['volume'] = la['poete'].apply(volume)
    return la


def sauvegarder_donnees(sf, la):
    """Concatène les deux groupes (avec leur étiquette) et sauvegarde."""
    sf2 = sf.copy(); sf2['groupe'] = 'SF Renaissance'
    la2 = la.copy(); la2['groupe'] = 'LA canon local (sans lauréat)'
    pd.concat([sf2, la2]).to_csv(OUT_CSV, index=False, encoding='utf-8')


def tracer_figure(sf, la, tot_sf, moy_sf, tot_la, moy_la):
    """Deux panneaux horizontaux à la MÊME échelle."""
    xmax = max(sf['volume'].max(), la['volume'].max()) + 8
    fig, (axSF, axLA) = plt.subplots(1, 2, figsize=(14, 6.5), sharex=True)

    def panneau(ax, data, couleur, titre, total, moyenne):
        d = data.sort_values('volume')
        y = range(len(d))
        ax.barh(y, d['volume'], color=couleur, alpha=0.85)
        ax.set_yticks(y); ax.set_yticklabels(d['poete'], fontsize=9)
        for i, v in enumerate(d['volume']):
            ax.text(v + 1, i, str(int(v)), va='center', fontsize=8.5, color='#333')
        ax.set_xlim(0, xmax)
        ax.set_title(f"{titre}\nTotal {int(total)} publications — moyenne {moyenne:.1f}/poète",
                     fontsize=11, color=couleur, fontweight='bold')
        ax.set_xlabel("Nombre de publications (4 revues nationales)")
        for c in ['top', 'right']:
            ax.spines[c].set_visible(False)
        ax.grid(True, axis='x', ls=':', alpha=0.4)

    panneau(axSF, sf, COUL_SF, "SF Renaissance (12 canoniques, poets.org)", tot_sf, moy_sf)
    panneau(axLA, la, COUL_LA, "LA — 12 plus canoniques AU LOCAL (hors lauréat)", tot_la, moy_la)

    fig.suptitle("Présence dans les revues nationales : scène SF vs scène LA\n"
                 "(poètes sélectionnés par leur consécration locale, puis mesurés au national)",
                 fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=150, bbox_inches='tight')


# ---------------------------------------------------------------------------
# 3. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    j = charger_jstor(INPUT_JSTOR)
    volume = faire_compteur(j)

    sf = liste_sf(volume)
    la = liste_la(INPUT_LOCAL, volume)
    sauvegarder_donnees(sf, la)

    tot_sf, moy_sf = sf['volume'].sum(), sf['volume'].mean()
    tot_la, moy_la = la['volume'].sum(), la['volume'].mean()
    print(f"SF : total {tot_sf}, moyenne {moy_sf:.1f}")
    print(f"LA local (sans lauréat) : total {tot_la}, moyenne {moy_la:.1f}")

    tracer_figure(sf, la, tot_sf, moy_sf, tot_la, moy_la)
    print("Figure  ->", OUT_PNG)
    print("Données ->", OUT_CSV)


if __name__ == "__main__":
    main()

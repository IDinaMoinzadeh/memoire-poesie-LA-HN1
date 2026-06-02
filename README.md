# Canonicité et géographie littéraire : la poésie de Los Angeles (1948-2024)

Annexes numériques du mémoire de master « Humanités numériques »,
École nationale des chartes / EHESS / PSL.

**Autrice :** Irandokht Dina Moinzadeh
**Direction :** «Jean Barré / Dinah Ribard»
**Année :** 2025-2026

Ce dépôt rassemble les données, les scripts et la documentation permettant de **reproduire et
vérifier** les analyses du mémoire, conformément aux normes des annexes numériques de l'École.

---

## 1. Résumé du projet

Le mémoire mesure l'émergence et la canonisation des poètes de Los Angeles dans le champ
littéraire américain, à partir d'une approche quantitative sur trois niveaux de canonicité :
le canon **local** (anthologies de Los Angeles), la **circulation nationale** (revues), et la
consécration **nationale** (anthologies de référence). Le corpus compte **618 poètes**.Une comparaison systématique avec la **SF Renaissance** (12 poètes canoniques) permet de situer la scène angeleno dans le champ national et d'évaluer le degré de sa visibilité institutionnelle.

---

## 2. Structure du dépôt

```
.
├── README.md                  ← ce fichier
├── donnees/
│   ├── brutes/                ← entrées figées (snapshots, exports, OCR) — voir §5
│   ├── intermediaires/        ← fichiers produits en cours de chaîne
│   └── finales/               ← les CSV d'analyse (les fichiers *_FINAL)
├── scripts/
│   ├── acquisition/           ← scraping, OCR, export JSTOR (NON déterministe)
│   ├── transformation/        ← scoring local, scoring national, comptage JSTOR (déterministe)
│   └── visualisation/         ← figures du mémoire
├── notebooks/                 ← notebooks d'origine (provenance : version réellement exécutée)
├── figures/                   ← sorties des visualisations (PNG/SVG/PDF)
└── documentation/             ← documentation technique complémentaire si besoin
```

---

## 3. Environnement et installation

- Python 3.14, distribution Miniconda
- Environnement conda : `poetes_LA`
- Bibliothèques : `pandas`, `requests`, `beautifulsoup4`, `matplotlib`, `scipy`, `adjustText`

Reconstituer l'environnement :

```bash
conda create -n poetes_LA python=3.14
conda activate poetes_LA
pip install pandas requests beautifulsoup4 matplotlib scipy adjustText
```

---

## 4. Pipelines : entrée → script → sortie

Chaque chaîne est documentée par son entrée, le script qui la traite, et sa sortie.
Les chaînes d'**acquisition** ne se rejouent pas à l'identique (sources en ligne / OCR) :
leur trace est l'**entrée figée** sauvegardée. Les chaînes de **transformation** sont
déterministes et reproductibles.

### 4.1 Transformations (déterministes, reproductibles)

| Script | Entrée(s) | Sortie | Rôle |
|--------|-----------|--------|------|
| `transformation/07_anthologies_nationales.py` | `poetes_LA_canon_local.csv` · `bap_poetes_clean.csv` · `input_norton_gioia_raw.txt` | `anthologies_nationales_FINAL.csv` | Croise Norton (Gioia, sous-chaîne), Penguin (exact normalisé) et BAP avec le corpus ; produit les colonnes `in_norton`, `in_penguin`, `in_bap`, `nb_bap`, `annees_bap` |
| `transformation/08a_croisement_revues_nationales.py` | `jstor_auteurs_revues.json` · `poetes_LA.csv` | `revues_nationales.csv` | Croise le JSON JSTOR avec le corpus (622 poètes) ; produit les listes d'années de publication par revue |
| `transformation/08b_nettoyage_revues_FINAL.py` | `revues_nationales.csv` | `revues_nationales_FINAL.csv` | Retire 4 poètes hors-corpus (622→618) ; ajoute les colonnes `_nb_pub` et `score_revues_volume` |
| `transformation/09_scoring_canon_national.py` | `revues_nationales_FINAL.csv` · `anthologies_nationales_FINAL.csv` | `poetes_LA_canon_national_FINAL.csv` | Fusionne revues et anthologies ; calcule `score_national_volume` et `score_national_presence` |
| `transformation/10_score_canon_local.py` | `poetes_LA_canon_local.csv` | `poetes_LA_canon_local_scored.csv` | Calcule `score_canon_local` par application des poids sur les 14 anthologies locales, la liste LAPL et les lauréats |

### 4.2 Acquisitions (non déterministes, documentées par l'entrée figée)

| Notebook / script | Entrée figée | Sortie | Note |
|-------------------|--------------|--------|------|
| `notebooks/Canon_LA.ipynb` | `poetes_LA_liste_definitive.txt` + 14 listes d'anthologies (OCR/saisie) | `poetes_LA_canon_local.csv` | Construction du corpus : ~90 cellules, corrections de noms au fil de l'eau ; carnet de construction conservé comme trace de l'acquisition manuelle |
| `notebooks/croisement_revues-nationales.ipynb` (cellule 1) | `jstor_metadata_2026-05-03.jsonl.gz` (1,29 Go, export JSTOR Data for Research, 2026-05-03) | `jstor_auteurs_revues.json` | Lit le fichier JSTOR (~5 min), croise les auteurs avec le corpus, produit le JSON de croisement utilisé par `08a` |
| `notebooks/bap_scraping.ipynb` | snapshot Wayback Machine `20250420030249` de `bestamericanpoetry.com/archive/` | `bap_poetes_clean.csv` | Scraping itératif des tables BAP 1988-2024 ; fonction `extraire_poetes_v2` |
| (manuel) | OCR captures d'écran du sommaire Penguin (Dove, 2011) | liste en dur dans `07_anthologies_nationales.py` | Saisie manuelle ligne par ligne |
| (manuel / OCR) | index *Hold-Outs* (Mohr, 2011) | colonne `holdouts` dans `poetes_LA_canon_local.csv` | OCR + correction manuelle sur 203 noms |

### 4.3 Visualisations

Les scripts de visualisation lisent leurs entrées dans le **répertoire courant**. Pour relancer
une figure, placer le script et ses entrées dans le même dossier, puis `python3 <nom_script>.py`.
Les sorties (PNG + CSV de contrôle) sont générées dans ce même dossier.

Dépendances supplémentaires (viz 02, 03, 06) : `pip install scipy adjustText --break-system-packages`

| Script | Entrée(s) | Sorties | Rôle |
|--------|-----------|---------|------|
| `visualisation/01_viz_canon_local_avec_sans_laureat.py` | `input_poetes_LA_canon_local_scored.csv` | `viz1_top_local_avec_sans_laureat.png` · `viz1_classements_avec_sans_laureat.csv` | Slope chart : top 19 poètes du canon local avec et sans le prix de lauréat |
| `visualisation/02_viz_canon_national_volume_vs_presence.py` | `input_poetes_LA_canon_national_FINAL.csv` | `viz2_volume_vs_presence.png` · `viz2_comparaison_volume_presence.csv` | Nuage de points : score volume vs score présence ; ρ de Spearman |
| `visualisation/03_viz_local_vs_national_seuils.py` | `input_poetes_LA_canon_local_scored.csv` · `input_poetes_LA_canon_national_FINAL.csv` | `viz3b_local_vs_national_couleurs.png/.csv` · `viz3c_local_vs_national_seuil6.png/.csv` | Scatter local vs national, deux seuils (5 et 6) — robustesse de la quasi-indépendance |
| `visualisation/04_viz_quadrant.py` | `input_poetes_LA_canon_local_scored.csv` · `input_poetes_LA_canon_national_FINAL.csv` | `viz4_quadrant.png` · `viz4_quadrant_categories.csv` | Quadrant (fort/faible local × fort/faible national) |
| `visualisation/06_viz_SF_vs_LA_revues.py` | `input_poetes_LA_canon_local_scored.csv` · `input_jstor_auteurs_revues_poesie_v2.csv` | `viz6_SF_vs_LA_local.png` · `viz6_SF_vs_LA_local_volumes.csv` | Barres comparées SF Renaissance vs LA (12 canoniques de chaque côté) dans les revues nationales |
| `visualisation/07_viz_anthologies_SF_vs_LA.py` | `input_poetes_LA_canon_local_scored.csv` · `bap_poetes_clean.csv` · `input_norton_gioia_raw.txt` (+ listes Norton M&C et Penguin en dur) | `viz7_anthologies_SF_vs_LA.png` · `viz7_anthologies_SF_vs_LA.csv` · `viz7_anthologies_detail_noms.csv` | Barres groupées en % : présence SF vs LA dans les 4 anthologies nationales |

---

## 5. Jeux de données

### 5.1 Fichiers finaux (`donnees/finales/`)

- **`poetes_LA_canon_local_scored.csv`** (618 poètes) : présence dans les 14 anthologies
  locales, le blog Mohr, le workshop Beyond Baroque, la liste LAPL et les lauréats ;
  colonne finale `score_canon_local`.
- **`poetes_LA_canon_national_FINAL.csv`** (618 poètes) : scores de canon national.
  `score_national_volume` (anthologies + revues en volume) et `score_national_presence`
  (anthologies + revues en présence).
- **`revues_nationales_FINAL.csv`** : présence et nombre de publications par revue.
- **`anthologies_nationales_FINAL.csv`** : présence dans Norton, Penguin, BAP.

### 5.2 Sources de référence

- Bill Mohr, *Hold-Outs* (source primaire de l'index)
- 14 anthologies locales de Los Angeles (1972-2017)
- *Norton Anthology of Modern and Contemporary Poetry* (2003) — utilisée dans la comparaison SF/LA (viz7, barres Norton M&C)
- *Norton Anthology of Poetry*, éd. Gioia et al. (table des matières partielle, partie moderne) — utilisée pour la colonne `in_norton` du corpus LA
- *Penguin Anthology of Twentieth-Century American Poetry*, éd. Rita Dove (2011)
- *Best American Poetry* (1988-2024)
- 4 revues via JSTOR : *Poetry*, *American Poetry Review*, *Kenyon Review*, *Prairie Schooner*

### 5.3 Conventions de scoring

**Canon local** (`score_canon_local`) : 13 anthologies locales × 1 pt + `mohr_blog_absents` × 1 pt + `lapl_list` × 2 pts + lauréat × 3 pts. La colonne `holdouts` (index *Hold-Outs*, Mohr) est exclue du score : source biographique sans sélection éditoriale, elle documente la présence dans la scène sans constituer une consécration. Score max observé : 11.

**Canon national** : deux scores sont maintenus en parallèle comme dispositif analytique. `score_national_volume` : composante revues en volume cumulé (1 pt par publication) + anthologies. `score_national_presence` : composante revues en présence binaire (1 pt par revue distincte) + anthologies. Les deux scores ne diffèrent que par la composante revues. Anthologies : 2 pts chacune (Norton/Gioia, Penguin, BAP) — le poids 2 reflète la hiérarchie canonisation > circulation. Le BAP est traité en présence binaire (0/1) : sa nature annuelle le rend incomparable aux anthologies à volume unique.

---

## 6. Licence et citation

Licence à préciser. Pour toute question d'usage ou de réutilisation, contacter l'autrice.

Pour citer ces annexes : Irandokht Dina Moinzadeh, *Canonicité et géographie littéraire :
la poésie de Los Angeles (1948-2024)*, annexes numériques, 2026, «https://github.com/IDinaMoinzadeh/memoire-poesie-LA-HN1/».

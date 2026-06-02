# Canonicité et géographie littéraire : la poésie de Los Angeles (1948-2024)

Annexes numériques du mémoire de master « Humanités numériques »,
École nationale des chartes / EHESS / PSL.

**Autrice :** Irandokht Dina Moinzadeh
**Direction :** Jean Barré et Dinah Ribard
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

| Script | Entrée | Sortie | Rôle |
|--------|--------|--------|------|
| `transformation/«À COMPLÉTER».py` | anthologies + revues nationales | `poetes_LA_canon_national_FINAL.csv` | Calcule les scores de canon national (volume et présence) |
| `transformation/«À COMPLÉTER».py` | listes des 14 anthologies locales + index + LAPL/lauréats | `poetes_LA_canon_local_scored.csv` | Calcule le score de canon local |
| `transformation/«À COMPLÉTER».py` | `jstor_metadata_2026-05-03.jsonl.gz` | `revues_nationales_FINAL.csv` | Compte les publications par revue (Poetry, APR, Kenyon Review, Prairie Schooner) |

### 4.2 Acquisitions (non déterministes, documentées par l'entrée figée)

| Script | Entrée figée | Sortie | Note |
|--------|--------------|--------|------|
| `acquisition/«À COMPLÉTER».py` | snapshot Wayback `«À COMPLÉTER»` | liste BAP | Scraping itératif |
| `acquisition/«À COMPLÉTER».py` | page Wikipedia (Norton) | liste Norton | BeautifulSoup |
| (manuel) | OCR Penguin | liste Penguin | Saisie manuelle |
| (manuel / OCR) | index *Hold-Outs* (Mohr) | liste ~200 poètes | OCR + correction manuelle |

«À COMPLÉTER : remplacer les noms de fichiers réels et compléter les lignes manquantes.»

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
- *Norton Anthology of Modern and Contemporary Poetry* (2003)
- *Penguin Anthology of Twentieth-Century American Poetry*, éd. Rita Dove (2011)
- *Best American Poetry* (1988-2024)
- 4 revues via JSTOR : *Poetry*, *American Poetry Review*, *Kenyon Review*, *Prairie Schooner*

### 5.3 Conventions de scoring

«À COMPLÉTER (optionnel mais recommandé) : rappeler ici en 3-4 lignes les choix de pondération,
par ex. BAP en binaire, anthologies pondérées à 2 points, revues en deux variantes volume/présence.»

---

## 6. Licence et citation

«À COMPLÉTER : licence choisie pour le code et les données, par ex. MIT pour le code,
CC BY pour les données. Si dépôt Zenodo, indiquer ici le DOI une fois la release archivée.»

Pour citer ces annexes : Irandokht Dina Moinzadeh, *Canonicité et géographie littéraire :
la poésie de Los Angeles (1948-2024)*, annexes numériques, 2026, «URL du dépôt / DOI».

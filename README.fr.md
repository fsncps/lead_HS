---
language: fr
translation_of: README.md
source_updated: 2026-09-14
---

Sprachen / Languages / Langues : [EN](README.md) · [DE](README.de.md) · **FR**

# lead_HS — Le plomb dans les peintures sur le marché de l'UE (HS 3208 / 3209)

Une **étude fondée sur les documents** consacrée au **marché de l'UE**
des peintures et vernis sous les positions tarifaires **3208** (en
phase solvant) et **3209** (en phase aqueuse) : combien de produits y
sont proposés, pour combien d'entre eux une documentation détaillée —
au premier chef les **fiches de données de sécurité (FDS)** — peut
être obtenue, et ce que cette documentation révèle de la **teneur en
plomb**.

L'étude s'inscrit dans le contexte de l'**exception
Cassis-de-Dijon** suisse pour les peintures contenant du plomb et de
la législation et des processus décisionnels associés, auxquels elle
apporte des chiffres de marché documentés. Elle repose exclusivement
sur des documents accessibles au public : **pas de laboratoire, pas
d'échantillons physiques, pas de sources de données payantes.**

> **Kurzfassung / Résumé (DE/FR) :**
> [`docs/management_summary.md`](docs/management_summary.md) — synthèse
> de gestion bilingue à l'attention des décideurs.

*Les documents méthodologie et sources de données liés ci-dessous sont
rédigés en langage clair pour des lecteurs non spécialistes, chacun
avec un glossaire ; les termes spécialisés sont également expliqués à
leur première utilisation.*

## Les questions

1. **Combien** de produits de peinture le marché de l'UE compte-t-il
   sous HS 3208/3209 ? Les statistiques douanières comptent des tonnes
   et des euros, et aucun registre de produits n'existe — l'étude
   compte donc les **formulations de base** (une recette, quel que
   soit le nombre de teintes ou de contenants vendus) et reconstitue
   la taille du marché à partir de plusieurs sources officielles
   indépendantes.
2. **Pour combien de produits une documentation détaillée peut-elle
   être obtenue** — FDS et spécifications comparables — et par
   quelles sources ?
3. **Que révèle cette documentation sur le plomb** — comme pigment de
   couleur, inhibiteur de rouille ou siccatif — sur un échantillon
   significatif de produits ?

## Méthode

L'étude procède en trois temps : établir la taille du marché, obtenir
la documentation d'un échantillon significatif, analyser.

- Les documents produit sont collectés auprès de sources publiques —
  pages de fabricants et de détaillants, registres publics,
  statistiques officielles — et chaque FDS est vérifiée contre un
  dictionnaire fixe de composés du plomb.
- Les constats suspects sont recoupés avec des documents indépendants
  concernant le même produit (fiches techniques, textes d'étiquetage,
  versions antérieures de FDS). Pas de laboratoire : la documentation
  constitue la preuve.
- **Une limite est énoncée d'emblée :** les FDS ne déclarent les
  composés de plomb classifiés qu'à partir de 0,1 %, alors que
  l'interdiction suisse s'applique dès 0,01 % (100 ppm — parties par
  million) de plomb total. La méthode documentaire ne voit donc que le
  plomb *déclaré*, pas le plomb *total* ; cet angle mort accompagne
  chaque livrable.

Méthode complète, en langage clair avec glossaire :
[document méthodologie](docs/plan/3SM/10_STRATEGY/METHODOLOGY.fr.md).

## Contexte juridique

Le **principe Cassis-de-Dijon** (repris unilatéralement par la Suisse
en 2010, LOTC art. 16a) : les produits légalement vendus dans l'UE
peuvent en règle générale aussi être vendus en Suisse. Ses exceptions
sont cataloguées dans l'**OPPr** (RS 946.513.8) ; la première rubrique
concerne les **peintures contenant du plomb** et maintient la limite
suisse plus stricte pour les importations (ORRChim, annexe 2.8 :
interdiction dès 0,01 % de plomb total). Le catalogue est réexaminé
tous les cinq ans, la dernière fois en 2023, sous la conduite du SECO.

L'étude fournit dans ce contexte des chiffres de marché documentés ;
c'est une étude documentaire qui ne prend pas position sur la
réglementation elle-même. La Suisse n'intervient dans l'étude que
comme ce cadre réglementaire — le marché étudié est celui de l'UE.

## Étape actuelle : l'échantillon CSV de gestion (v0.2.4)

L'unité v0.2.4 pose la question de gestion pour chaque grand
registre : **à quoi ressemble une ligne produit** — quels champs de
données reviennent par produit, quelles colonnes d'identifiants
existent, le recoupement de produits individuels est-il possible ?
Répondu avec des lignes réellement téléchargées là où un registre en
publie (`leadhs probe download-csv-sample` ; exécution réelle du
14.09.2026, n=100 par registre, seed=42 — reproductible) et avec une
raison honnête et sourcée là où il n'en publie pas. Le manifeste ne
taire jamais un échec.

- **AS-2 — Écolabel européen (ECAT) : livré, 100 de 17 013 produits
  distincts** (17 838 lignes dans le périmètre ; en-tête d'export
  ré-épinglé exactement comme échafaudé en v0.2.3). 12 champs par
  article ; identifiants : numéro de licence (100 %), entreprise +
  TVA (86 %), EAN13/GTIN (17 % de l'échantillon). Recoupement : EAN ↔
  catalogues de distribution (le chemin d'amorçage v0.3) repose sur
  de vraies colonnes.
- **AS-3 — Cygne nordique : livré, niveau d'essai, 14 produits
  distincts.** La découverte bornée a trouvé un vrai export — l'URL
  de recherche sert un CSV via `?format=csv` (9,8 Mo). Réserves de
  qualité consignées dans le manifeste (virgules non citées entre
  guillemets, licences mixtes Écolabel européen/Cygne nordique) ; le
  pilote de recouvrement des écolabels est joignable par nom +
  titulaire de licence — l'export porte même des numéros de licence
  Écolabel européen.
- **ST-1 / ST-3 / ST-6 / ST-7 : aucune ligne produit publiée** —
  réseau nul, chaque enregistrement cite la raison structurelle (PCN
  réservé aux autorités ; SBS statistiques d'entreprises ; AT danois
  agrégats uniquement ; secret des affaires KemI au niveau produit).
  Des six grands registres, exactement deux publient des lignes
  produit ; seul ECAT possède des colonnes d'identifiants par
  article.

Chaque ligne échantillonnée porte une provenance complète (source,
clé d'exécution, date de récupération, hachage du document, seed,
index de tirage). Rapport d'unité :
[report-0.2.4.md](docs/report/report-0.2.4.md) (EN) ; le manifeste et
les échantillons sont publiés dans
[docs/report/](docs/report/csv-sample.manifest.md) (rendus de travail
par exécution dans `data/report/`).

**Addendum — sondage des sources de classe AS (2026-09-14).** Un
constat par source de classe AS, les 30 (`leadhs probe
as-source-probe`) : CSV de lignes produit là où il est obtenable, sinon
nombre d'enregistrements exact ou estimé avec provenance, sinon
pourquoi-pas + ce qui est disponible à la place. Les deux catalogues
d'écolabels réutilisent les lignes csv-sample (AS-2 : 100, AS-3 : 14) ;
Blue Angel (≈70 000) et environdec (≈2 025) n'exposent que des comptes
en texte de page ; les cinq autres registres (INIES, IBU, NF Env,
natureplus, EPD Norway) n'ont pas de surface de masse — documents
produit par produit derrière des interfaces de recherche, raison
consignée. Les 21 associations professionnelles sont des annuaires de
membres, pas des registres de produits (18 vivantes, 3 inaccessibles
au moment de la sonde). Synthèse :
[as-source-probe.summary.20260914-125322.md](docs/report/as-source-probe.summary.20260914-125322.md) (EN).

## Unités antérieures

### v0.2.3 — estimation de pool v2 : vote méta-benchmark (14.09.2026)

L'unité v0.2.3 remplace le titre à modèle unique de v0.2.2 par un
**vote méta-benchmark** : sept quantités de référence indépendantes
estiment le pool de peintures de l'UE ; chacune vote dans l'une des
cinq classes de magnitude contiguës (a 20k–50k … e >300k), et une
règle épinglée convertit le vote en un **verdict à deux niveaux** —
niveau SKU (comptage registre/produit) et niveau formulation
(collapsé ombre/conditionnement). La confiance n'est revendiquée que
lorsque ≥3 benchmarks disponibles convergent sans conflit exclusif non
adjacent ; les égalités rendent une fourchette avec les hypothèses de
basculement ; le vote reste visible dans tous les cas.

- **Niveau SKU : classe e (>300k produits)** — confiance non
  revendiquée (trois benchmarks se situent dans des classes non
  adjacentes ; consignés comme points ouverts).
- **Niveau formulation : classe c (100k–200k)** — confiance non
  revendiquée ; la conversion de niveau repose sur une fourchette
  épinglée d'effondrement d'ombres 1–10, signalée comme hypothèse (la
  déduplication mesurable des clés ECAT est faible : nom ×1,049,
  EAN ×1,266).
- De nouvelles extractions de sources primaires alimentent les
  benchmarks : déclarations des centres antipoison suédois
  peintures/vernis 71 231 (2022) ; dossiers PCN 1 444 290 (2021,
  SWD(2022) 435 annexe 16 — aucune constante de part de peinture
  n'existe) ; rapport final du JCR sur l'Écolabel européen (2026) :
  36 960 produits certifiés (03/2025) et la confirmation officielle
  qu'**aucune donnée de part de marché n'existe** ; Produktregistret
  danois ≈40 000 produits dangereux (agrégats uniquement — pas
  d'adaptateur possible) ; vérification Eurostat SBS : 3 300
  entreprises (NACE C2030, 2020).
- La section entonnoir du rapport publié porte désormais un bandeau
  de péremption ; son contenu v0.2.2 est conservé dans l'historique
  de publication.
- La passe complète de sondage du 14.09.2026 (vagues 1–3) a
  reproduit chaque chiffre clé (ECAT 17 838 rapproché exactement ;
  Comext 6 316 lignes ; ensembles bloqués/en échec identiques) —
  constats, lacunes et pistes dans le document compagnon
  [benchmarking-0.2.3.md](docs/report/benchmarking-0.2.3.md) (EN).

Détails : [report-0.2.3.md](docs/report/report-0.2.3.md) (EN) ;
tableaux lisibles par machine (vote des benchmarks, verdicts, toutes
les sections antérieures) dans le
[rapport de sondage](docs/report/probe-report.md).

### v0.2.2 — l'entonnoir à trois questions (14.09.2026)

L'unité v0.2.2 a exécuté les **passes du paysage sur le réseau réel**
(14.09.2026 ; reconnaissance uniquement — exports/APIs officiels, pas
de scraping) et a assemblé **l'entonnoir à trois questions** — chaque
chiffre est le résultat d'une requête de base de données :

- **Q1 — combien de peintures sur le marché de l'UE (estimation
  modélisée) :** le modèle `P(cn8) = M × ppp × s(cn8)` donne
  **[85 840–343 360] produits** — bornes de producteurs 800 (CEPE) à
  3 200 (Eurostat SBS NACE 20.30) × **107,3 produits par producteur**
  (ECAT : paires ÷ titulaires de licence) × parts de volume des
  importations extra-UE par code CN8. Une estimation modélisée, jamais
  un décompte. **Supplanté depuis le 14.09.2026 par le vote benchmark
  v0.2.3 (ci-dessus) ; conservé dans l'historique de publication.**
- **Q2 — pour combien de produits le triplet d'identité est
  définitivement connu (plancher) :** **17 170** paires distinctes
  (fabricant, identifiant produit) sur les registres officiels
  établis (ECAT : 17 838 entrées, 160 titulaires, 16,0 % de
  complétude d'identité).
- **Q3 — pour combien d'entre eux un document de type FDS est
  accessible (modélisé) :** **3 590** (borne supérieure ; l'hypothèse
  de taux de correspondance est en attente). Le rapport v0.5 (Q2 ÷ Q1)
  se lit **0,05–0,2**.

Le registre de sources de 101 lignes est entièrement dispositionné :
**36 comptées, 48 documentées manuellement, 4 bloquées, 13 inactives
par conception** ; l'établissement Comext couvre **les 13 codes CN8**
(6 316 lignes commerciales). Le pilote de chevauchement ECAT ∩ Cygne
Nordique reste explicitement non calculable tant qu'un second registre
n'est pas établi. Rapport d'unité :
[report-0.2.2.md](docs/report/report-0.2.2.md) ; tableaux
lisibles par machine (commerce CN8, identité, matrice de profondeur,
recensement, drapeaux de rapprochement) dans le
[rapport de sondage](docs/report/probe-report.md).

### v0.2.1 — capacité des sources sondée (14.09.2026)

Un niveau plus profond pour les **registres officiels** (Écolabel UE,
Cygne Nordique, Ange Bleu, INIES, IBU, environdec), chacun
caractérisé contre le modèle produit (CN8, fabricant, identifiant
produit) selon le volume et la profondeur. **ECAT confirmé comme
source de produits réels** (fabricant + GTIN/EAN, CN8 via catégorie,
profondeur 2, CSV téléchargeable) ; numérateur N2 préliminaire
**17 838** produits de peinture certifiés — un plancher, jamais un
total de marché. Les autres registres sont restés à ancrer /
inactifs / sans identifiant produit ; le défaut HTML-as-CSV de cette
passe a été réparé dans la v0.2.2. Détails :
[report-0.2.1.md](docs/report/report-0.2.1.md).

### v0.2.0 — carte du paysage des données (12.09.2026)

Sondage en mode reconnaissance des sources enregistrées (statistiques
officielles, une association et un registre sectoriel, et 25 sites de
peintures/revêtements/bricolage/couleurs d'artistes). Chiffres
phares : **N1** ancres de marché (2024, importations extra-UE : HS
3208 ≈2,5 Mt / ≈12,2 Mrd €, HS 3209 ≈2,1 Mt / ≈6,2 Mrd € ; CEPE ≈800
membres ; SBS NACE 20.30 = 3 200 entreprises) ; **N2 = 204 693** URL
produit visibles via sitemaps sur 23 sources comptées ; **N3 = 9**
sites avec une bibliothèque de FDS visible ; les registres nordiques
sont restés ouverts (SPIN injoignable). Détails :
[report-0.2.0.md](docs/report/report-0.2.0.md).

## Ce que les recherches antérieures montrent

| Usage du plomb | Situation documentée sur le marché de l'UE |
|---|---|
| Pigments au chromate de plomb | aucun approvisionnement légal depuis le 17 mars 2022 (dernières autorisations refusées) |
| Primaires au minium de plomb | présence documentée dans des niches (fournisseurs marins en DE ; professionnels SE uniquement) |
| Siccatifs au plomb dans les peintures alkydes | inconnu — la principale question ouverte de l'enquête |
| Couleurs à l'huile au blanc de plomb | documentées (NL, IT) — position tarifaire 3213 |

Détails et sources :
[LEAD_SDS.md](docs/plan/3SM/10_STRATEGY/LEAD_SDS.md) (EN).

## L'outil

La collecte des données et leur traçabilité reposent sur **`leadhs`**,
un petit programme en ligne de commande — pas de serveur, une machine,
une base SQLite locale. Chaque document récupéré est archivé à
l'identique, avec sa source, sa date de récupération et une empreinte
de son contenu ; chaque chiffre d'un rapport remonte à une exécution
et à un document précis. L'outil ne stocke que des données produit.

- Dans ce dépôt : `make setup` (installation, migration de la base,
  chargement du registre des sources, contrôle préalable de
  l'environnement) et `make help` (index de toutes les commandes).
- Hors du dépôt : construire le wheel (`uv build`) et l'installer avec
  un interpréteur géré (`uv tool install dist/leadhs-*.whl`), en
  travaillant toujours avec un dossier de données explicite
  (`leadhs --data-dir ~/leadhs-data …`). Cette voie est vérifiée par
  construction ; les artefacts de version publiés restent à venir. Un
  installateur pour Windows brut (sans make, sans Python
  préinstallé) est un objectif affiché pour v0.3.
- Les opérations qui touchent de vrais sites sont gardées derrière un
  `GO=1` explicite.

Détails : [architecture](docs/plan/3SM/10_STRATEGY/ARCHITECTURE.md) et
[modèle de données](docs/plan/3SM/10_STRATEGY/DATA_MODEL.md) (EN) ;
conception technique revue dans
[20_DESIGN/](docs/plan/3SM/20_DESIGN/) (EN).

## Feuille de route

| Phase | Contenu |
|---|---|
| 0 — en cours | Cartographier le paysage des données ; les trois chiffres N1/N2/N3 ; sonder la capacité des registres officiels |
| 1 | Pilote : figer le dictionnaire du plomb ; collecte et analyse des FDS sur un premier échantillon |
| 2 | Base d'échantillonnage et tirage ; collecte de documentation à pleine échelle ; annexe couleurs d'artistes (3213), selon la capacité |
| 3 | Recoupement inter-documents et assurance qualité |
| 4 | Analyse ; base de discussion ; gel de la base de données |

## Pour en savoir plus

| Document | Contenu |
|---|---|
| [`management_summary.md`](docs/management_summary.md) | synthèse bilingue (DE/FR) pour les décideurs |
| [`METHODOLOGY.fr.md`](docs/plan/3SM/10_STRATEGY/METHODOLOGY.fr.md) | comment le marché est mesuré — langage clair, glossaire inclus |
| [`DATA_SOURCE.fr.md`](docs/plan/3SM/10_STRATEGY/DATA_SOURCE.fr.md) | chaque source et les règles d'accès — langage clair, glossaire inclus |
| [`ARCHITECTURE.md`](docs/plan/3SM/10_STRATEGY/ARCHITECTURE.md) (EN) | l'outil de collecte et le concept de reporting (semi-technique) |
| [`DATA_MODEL.md`](docs/plan/3SM/10_STRATEGY/DATA_MODEL.md) (EN) | la base de preuves (technique) |
| [`LEAD_SDS.md`](docs/plan/3SM/10_STRATEGY/LEAD_SDS.md) (EN) | composés du plomb, droit UE, ce que les fiches révèlent — ou non (semi-technique) |
| [`10_STRATEGY/MASTER.md`](docs/plan/3SM/10_STRATEGY/MASTER.md) (EN) | décisions stratégiques, questions ouvertes, feuille de route |
| [`20_DESIGN/`](docs/plan/3SM/20_DESIGN/) (EN) | conception technique de l'outil + de la base |
| [`30_IMPLEMENTATION/`](docs/plan/3SM/30_IMPLEMENTATION/) (EN) | plans des phases de construction des unités (v0.1.1–v0.1.3, v0.2.0–v0.2.4 construites) — suivi des phases, critères de sortie |
| [`charts/`](docs/plan/3SM/10_STRATEGY/charts/) (EN) | les schémas, avec leurs sources (référencés depuis les documents de détail) |
| [`README 3SM`](docs/plan/3SM/README.md) (EN) | guide en langage clair de l'arbre de planification |

## Structure du dépôt

    README.md                  ce fichier (EN)
    README.de.md               version allemande
    README.fr.md               version française
    AGENTS.md                  conventions pour le travail assisté par IA (EN)
    Makefile                   point d'entrée opérateur (« make help » = index)
    pyproject.toml             empaquetage Python de l'outil leadhs
    src/leadhs/                code source de l'outil (v0.1.1 sondage, v0.1.2 couche opérateur, v0.1.3 compteurs de parcours)
    tests/                     suite de tests automatisés hors ligne
    data/                      état de travail local (gitignored) : base, stockage brut, rapports intermédiaires
    docs/report/               rapports finaux publiés (commités délibérément)
    docs/management_summary.md synthèse de gestion bilingue (DE/FR), toujours à jour
    docs/plan/3SM/             notes de planification (système à 3 étages, EN)
    ├── README.md              guide en langage clair (EN)
    ├── MASTER.md, LOG.md      tableau de bord, journal du cycle de vie (EN)
    ├── 10_STRATEGY/           constats de recherche et décisions (quoi & pourquoi)
    │   ├── METHODOLOGY.fr.md  méthodologie, français
    │   ├── DATA_SOURCE.fr.md  sources de données, français
    │   └── charts/            schémas rendus (référencés depuis les documents de détail, EN)
    ├── 20_DESIGN/             conception technique (comment exactement, EN)
    └── _archive/              matériel remplacé

## État

Les unités outil v0.1.1–v0.2.4 sont construites et testées (364 tests
automatisés hors ligne) : base de preuves, registre des sources,
reconnaissance des sources, rapports de faisabilité par source,
machinerie de comptage pour les parcours de catalogues (en attente
d'un feu vert de collecte), carte du paysage des données avec les
trois chiffres phares, sondage de capacité des registres officiels,
l'entonnoir à trois questions exécuté sur le réseau réel
(14.09.2026), et l'estimation de pool v2 — le vote méta-benchmark
avec un verdict de magnitude à deux niveaux (14.09.2026) : moteur de
benchmarks, paquet d'adaptateurs, quatre nouvelles extractions
primaires, section de rapport avec bandeau de péremption — chaque
chiffre est un résultat de requête ou une extraction datée — et
l'échantillon CSV de gestion avec la preuve par lignes produit pour
chaque registre (14.09.2026). Le rapport
est publié sous `docs/report/`. La méthodologie reste ouverte à
révision à mesure que les résultats arrivent.

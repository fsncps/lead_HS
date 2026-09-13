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

## Étape actuelle : carte du paysage des données (v0.2.0) + capacité des sources (v0.2.1)

Avant toute collecte de données produit, l'étude cartographie son
**paysage des données** : quelles sources couvrent le marché de la
peinture de l'UE, à quelle échelle, et avec quel accès à la
documentation produit. Cette carte est établie et les trois
chiffres phares sont documentés. Chaque résultat, y compris les refus
d'accès, est consigné avec sa cause, et l'audit de provenance de la
base passe.

La passe de reconnaissance du 12 septembre 2026 a couvert les sources
enregistrées (statistiques officielles, une association et un registre
sectoriel, et 25 sites de peintures/revêtements/bricolage/couleurs
d'artistes). **N1, N2 et N3** figurent dans le
[rapport de reconnaissance](docs/report/probe-report.md) et sont
résumés ci-dessous :

- **N1 — combien de peintures sur le marché de l'UE :** un ordre de
  grandeur assemblé à partir des statistiques officielles. Les ancres
  douanières 2024 (Eurostat Comext, importations UE hors UE, DS-045409)
  chiffrent **HS 3208 à ≈2,5 Mt (≈12,2 Mrd €)** et **HS 3209 à ≈2,1 Mt
  (≈6,2 Mrd €)**. Ancres côté offre : CEPE représente ≈800 entreprises
  membres ; Eurostat SBS dénombre 3.200 entreprises en NACE 20.30
  (2020, peintures + encres + mastics). La fourchette d'ordre de
  grandeur reste une **estimation** — le rapport donne les ancres et la
  méthode, jamais un chiffre unique présenté comme factuel.
- **N2 — pour combien de produits nous avons un accès aux données,
  sous une forme ou une autre :** **204.693** URL produit observées sur
  **23** sources comptées (visibles via les sitemaps ; un plancher,
  dominé par quelques grands catalogues de bricolage).
- **N3 — pour combien d'entre eux des spécifications détaillées, une
  FDS par exemple, peuvent être obtenues :** **9** sites exposent
  visiblement une bibliothèque de FDS/documents (un nombre de sites,
  pas de produits) ; aucune documentation produit n'a encore été
  collectée — cela attend le feu vert de collecte.

Méthode à ce stade : reconnaissance uniquement — conditions
d'utilisation et conditions d'accès, disponibilité d'API ou de
téléchargements, comptage des URL produit dans les sitemaps,
vérifications manuelles. Les parcours de catalogues et toute collecte
au niveau produit attendent un feu vert distinct. Les registres
nordiques restent ouverts (SPIN injoignable lors de cette passe).

### Capacité des sources sondée (v0.2.1, construite le 14.09.2026)

La carte du paysage des données (v0.2.0) a compté les sources ; v0.2.1
descend d'un niveau pour les **registres officiels** — les
enregistrements écolabel et EPD qui publient des données produit sur
les peintures — et caractérise chacun contre le modèle produit de
l'étude (code CN8, fabricant, identification produit du fabricant),
selon le volume et la profondeur. Les profils de capacité figurent
dans le [rapport de reconnaissance](docs/report/probe-report.md)
(section « Capability profile »).

- Le registre comporte désormais **7 registres officiels** (AS-1–AS-7) :
  le catalogue Écolabel UE (ECAT), Nordic Swan, Ange Bleu, INIES, IBU
  et environdec, plus AS-1. Quatre sont actifs ; Ange Bleu et INIES
  sont inactifs (export XLSX ou accès protégé).
- La page d'accueil de chaque registre actif est du HTML — les exports
  sont documentés comme **URL d'export à ancrer** lors du prochain
  passage, consignés honnêtement plutôt que lus à tort comme un export.
- **Un registre est confirmé comme source de produits réels :** le
  **catalogue Écolabel UE (ECAT)** — il expose un champ fabricant, un
  champ d'identification produit (GTIN/EAN), un mécanisme de liaison
  CN8 (catégorie) et une profondeur de données 2 ; son export CSV est
  téléchargeable.
- **Numérateur N2 préliminaire (registres officiels, plancher) : 17.838**
  peintures & vernis et revêtements de performance de l'ECAT (16.001 +
  1.817 produits selon les critères 2014 et 2025, plus 20 revêtements
  de performance). Il s'agit d'un **sous-ensemble certifié/déclaré** du
  marché — un plancher, jamais un total de marché, et les données
  produit attendent toujours le feu vert de collecte.
- Les autres registres actifs ne sont pas encore des sources de
  produits réels : environdec expose un fabricant mais pas
  d'identification produit ; Nordic Swan et IBU sont à ancrer.

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
| [`30_IMPLEMENTATION/`](docs/plan/3SM/30_IMPLEMENTATION/) (EN) | plans des phases de construction des unités (v0.1.1–v0.1.3, v0.2.0 et v0.2.1 construites) — suivi des phases, critères de sortie |
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

Les unités outil v0.1.1–v0.2.1 sont construites et testées (231 tests
automatisés hors ligne) : base de preuves, registre des sources,
reconnaissance des sources, rapports de faisabilité par source,
machinerie de comptage pour les parcours de catalogues (en attente
d'un feu vert de collecte), carte du paysage des données avec les
trois chiffres phares, et sondage de capacité des registres officiels.
La passe de reconnaissance a tourné le 12 septembre 2026 ; le rapport
est publié sous `docs/report/`. La méthodologie reste ouverte à
révision à mesure que les résultats arrivent.

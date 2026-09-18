---
language: fr
translation_of: README.md
source_updated: 2026-09-18
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

## Contexte

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

### Ce que les recherches antérieures montrent

| Usage du plomb | Situation documentée sur le marché de l'UE |
|---|---|
| Pigments au chromate de plomb | aucun approvisionnement légal depuis le 17 mars 2022 (dernières autorisations refusées) |
| Primaires au minium de plomb | présence documentée dans des niches (fournisseurs marins en DE ; professionnels SE uniquement) |
| Siccatifs au plomb dans les peintures alkydes | inconnu — la principale question ouverte de l'enquête |
| Couleurs à l'huile au blanc de plomb | documentées (NL, IT) — position tarifaire 3213 |

Détails et sources :
[LEAD_SDS.md](docs/study/LEAD_SDS.md) (EN).


## Objectifs & méthodologie
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
[document méthodologie](docs/study/METHODOLOGY.fr.md).


## Sources de données
La collecte s'appuie sur un registre de **108 sources publiques** —
statistiques et registres officiels de produits, catalogues
d'écolabels et EPD, catalogues fabricants et commerçants,
associations sectorielles — tenu dans l'outil et sondé poliment
avant toute collecte : vérifications robots/conditions, un constat
de faisabilité par source, des entrées honnêtes « aucune donnée »
avec le motif structurel au lieu d'échecs silencieux. Discipline
d'accès : documents publiquement récupérables uniquement, coût
minimal, pas de martelage de masse, crawl-delay respecté.

Le **`data_sources.csv`** curaté recense les sources à données
produit de masse confirmées (masse + tuple d'identité =
fabricant + ident produit) : aujourd'hui **AS-2 Écolabel
européen (≈17 013 peintures distinctes)** et **AS-3 Cygne
Nordique (≈2 322)** ; **AS-33 BASTA** (195 391 articles de
construction via sa propre route anonyme client web) joint la
liste dès qu'un filtre de peinture côté serveur est épinglé.
Détail : [sources de données](docs/study/DATA_SOURCE.fr.md)
(langage clair, glossaire ; document parent EN).


## État du projet : prochaines étapes (v0.3)
La prochaine phase de construction transformera les sources de masse
confirmées en une base produit consolidée, en deux couches :

**1. Téléchargement des sources de masse (couche brute).** Chaque
source de masse confirmée — Écolabel européen (≈17 013 distincts),
Cygne Nordique (≈2 322) et BASTA (195 391 articles ; via sa propre
route anonyme client web) — est copiée dans une **table brute par
source** : verbatim, sans filtrage, une ligne par enregistrement
source, avec le nom du fabricant, l'identifiant produit et le code
de groupe exactement comme écrits par la source. Les
téléchargements sont répétables (interruption, reprise),
incrémentaux (une relance ne traite que les enregistrements
nouveaux/modifiés via un journal des changements) et pilotés par
manifeste (un manifeste committé par source définit la forme de la
table avant que les données ne coulent ; les enregistrements trop
gros débordent dans le stockage brut, rien n'est perdu).
Politesse : endpoints de liste d'abord, limitation de débit et
backoff, via la CLI existante sous `GO=1`
(`leadhs raw init <source>` / `leadhs raw seed <source>`).

**2. Normalisation déterministe et fusion (couche de rapprochement).**
Pour fusionner le même produit vu dans plusieurs sources, noms et
identifiants sont normalisés de façon déterministe (pas de LLM ni
d'apprentissage — chaque lien reste explicable et reproductible) :
pliage des diacritiques Unicode, casse normalisée, suppression des
jetons de forme juridique (« Foo-Bar Ltd. » ≙ « Foo Bar Limited » →
`foo bar`), nettoyage des identifiants (majuscules, zéros, préfixes ;
« ABC-123/B » ≙ « abc00123b » → `ABC123B`). Les enregistrements
sont ensuite liés par paliers : d'abord les clés exactes
(GTIN/EAN ; identifiant normalisé au sein du même fabricant
normalisé), puis les quasi-correspondances scorées
(Jaro-Winkler, similarité token-set) — uniquement dans de petits
blocs de candidats, pour que 200 k+ lignes restent traitables.
Chaque lien porte un verdict — `auto_match` /
`review` (file humaine) / `no_match` — avec méthode et scores par
paire ; la vue produit fusionnée reste entièrement auditable, les
corrections sont append-only. Résultat : une **table fabricants et
une table produits** ramenées à l'unité formulation de l'étude,
chaque produit portant ses observations par source et le niveau de
preuve de chaque lien.

Détails : les fichiers de stratégie
[`RAW_SOURCING.md`](docs/plan/3SM/10_STRATEGY/RAW_SOURCING.md) et
[`MATCHING.md`](docs/plan/3SM/10_STRATEGY/MATCHING.md) (règles,
seuils et choix de bibliothèque y sont verrouillés comme décisions
d'adoption en attente R1–R9 et MA1–MA9).


## État du projet : unités antérieures, résultats et lacunes
L'unité v0.2.4 répond à la question de gestion par grand registre :
**comment se présente une ligne produit là-bas** — quels champs, quelles
colonnes d'identifiants, le recoupement est-il possible ? — avec des
lignes réellement téléchargées là où un registre en publie (semé,
reproductible, n=100 par registre) et un motif structurel sourcé là
où non. Sur les six grands registres, exactement deux publient des
lignes produit ; seul l'Écolabel européen ECAT possède des colonnes
d'identifiants par article
([report-0.2.4.md](docs/report/report-0.2.4.md) (EN)) :

- **AS-2 — Écolabel européen (ECAT) : 100 sur 17'013 produits
  distincts** — n° de licence 100 %, entreprise + TVA 86 %,
  EAN13/GTIN 17 % de l'échantillon ; EAN ↔ catalogues commerciaux
  (le chemin de peuplement v0.3) s'appuie sur de vraies colonnes.
- **AS-3 — Cygne Nordique : 100 sur 2'322 lignes peinture
  distinctes** — export réel sous `?format=csv` (2'424 lignes
  peinture, 53 licences), portant même des numéros de licence
  Écolabel européen.
- **ST-1/3/6/7 — aucune ligne produit publiée** (PCN réservé aux
  autorités ; SBS ; AT danois ; secret KemI) — chaque motif cité.

Le **`data_sources.csv`** curaté liste les sources à données produit
de masse confirmées + tuple d'identité : aujourd'hui exactement
AS-2 et AS-3. Le tour de sondage complet (D39, 15.09.2026) a
enregistré six candidats-consultants sans trouver de **troisième
source de masse** ; la **sonde spéciale BASTA (D40, 17.09.2026)** a
renversé cela pour AS-33 via la propre route anonyme du client web —
comptages publics exacts **195'391 articles / 1'925 entreprises** et
un échantillon semé de 100 articles (tuple d'identité 100 %, GTIN
69,8 % ; 2/100 seulement dans les groupes peinture) — mais le filtre
de peinture côté serveur reste à épingler, donc pas encore de
troisième ligne `data_sources.csv`. Détails :
[report-0.2.4.md](docs/report/report-0.2.4.md) (addenda D37–D40, EN)
et le [registre des sources](docs/study/DATA_SOURCE.md).

#### v0.2.3 — estimation de pool v2 : vote méta-benchmark (14.09.2026)

Sept quantités de référence indépendantes estiment le pool de
peintures UE ; chacune vote dans l'une des cinq classes de grandeur,
règle épinglée → verdict à deux niveaux. Résultat : **niveau SKU
classe e (>300k), niveau formulation classe c (100k–200k) —
confiance non revendiquée dans les deux cas** (conflits
non adjacents notés en points ouverts). Détails :
[report-0.2.3.md](docs/report/report-0.2.3.md) (EN),
[benchmarking-0.2.3.md](docs/report/benchmarking-0.2.3.md) (EN).

#### v0.2.2 — l'entonnoir à trois questions (14.09.2026)

Le parcours du paysage sur le réseau réel (reconnaissance seule) :
Q1 modèle de pool **[85'840–343'360]** (supplanté par le v0.2.3 ;
conservé pour l'historique de publication), Q2 plancher d'identité
**17'170** paires distinctes (fabricant, ident produit), Q3 FDS
atteignable **≈3'590** (modélisé). Chaque nombre est un résultat de
requête ; registre des sources entièrement statué. Détails :
[report-0.2.2.md](docs/report/report-0.2.2.md) (EN).

#### v0.2.1 — capacité des sources sondée (14.09.2026)

Les registres officiels caractérisés contre le modèle produit :
**ECAT confirmé source produit réelle** (fabricant + GTIN/EAN, CSV
téléchargeable), numérateur N2 préliminaire **17'838** — un plancher,
jamais un total de marché. Détails :
[report-0.2.1.md](docs/report/report-0.2.1.md) (EN).

#### v0.2.0 — carte du paysage des données (12.09.2026)

Sondage en reconnaissance seule : **N1** ancrés de marché (2024,
importations extra-UE ≈12,2 + 6,2 milliards € ; ≈3'200 entreprises),
**N2 = 204'693** URL produit visibles via sitemap, **N3 = 9** sites
avec une bibliothèque FDS visible. Détails :
[report-0.2.0.md](docs/report/report-0.2.0.md) (EN).

### Comment le travail a avancé — revue de v0.1 et v0.2

L'étude s'est construite par la base, en petites unités vérifiées —
et ce process façonne ce qu'elle peut affirmer aujourd'hui.

**v0.1 (unités v0.1.1–v0.1.3) : construire l'instrument.** L'objectif
n'était jamais d'abord les chiffres, mais un outil de collecte
fiable. v0.1.1 a livré une trousse CLI élancée (base de preuves,
registre des sources, commandes de sondage) ; v0.1.2 l'a habillée en
couche opérateur (point d'entrée make, gardes `GO=1` pour tout ce
qui touche des sites réels) et a sondé poliment toutes les sources
enregistrées — robots/conditions, un constat de faisabilité par
source ; v0.1.3 a cartographié le paysage des données et construit
la machinerie de comptage des parcours (volontairement à l'arrêt
jusqu'à un feu vert de collecte). Méthode de bout en bout :
chaque document archivé à l'identique avec hash et date de
récupération ; chaque nombre traçable vers un run ; des entrées
honnêtes « aucune donnée » au lieu d'échecs silencieux ; pas de
laboratoire, pas de sources payantes, pas de scraping au-delà d'un
go explicite. Après v0.1, l'étude savait *quelles sources existent
et ce que chacune fournit* — pas encore la taille du marché.

**v0.2 (unités v0.2.0–v0.2.4) : pointer l'instrument vers les
chiffres.** Les objectifs sont devenus chiffres d'abord : taille du
marché (N1), couverture d'accès (N2), documentation atteignable
(N3). v0.2.0 a produit la carte du paysage sur données réelles.
v0.2.1 a sondé les registres officiels et trouvé la première
source produit réelle (Écolabel européen ECAT, avec fabricant +
GTIN/EAN). v0.2.2 a exécuté l'entonnoir à trois questions — combien
de produits dans le pool (modélisé), combien d'identités produit
définivement connues (plancher compté), combien de FDS atteignables
(modélisé). v0.2.3 a remplacé l'estimation à modèle unique par un
vote méta-benchmark de quantités indépendantes donnant des verdicts
par classes de grandeur. v0.2.4 a descendu la question au niveau
ligne : à quoi ressemble réellement un enregistrement produit dans
chaque registre — et a établi que seuls les deux catalogues
d'écolabels publient des lignes produit de masse, BASTA devenant
ajoutable via sa propre interface web anonyme une fois une question
structurelle réglée.

**Ce que les revues ont constamment changé.** Le périmètre a suivi
les preuves : métriques du marché suisse abandonnées tôt (le marché
étudié est celui de l'UE ; la Suisse n'est que le cadre
réglementaire), le plan « tout parcourir » remplacé par la
discipline reconnaissance-d'abord, et le livrable aiguillé d'une
carte générale vers une réponse chiffres-d'abord pour les acteurs de
l'exception suisse sur la peinture au plomb. Constantes : la
formulation comme unité de comptage, la corroboration au lieu du
laboratoire, l'angle mort déclarée-vs-total signalé dans chaque
livrable, et la provenance de chaque nombre.


## L'outil : CLI, base de données, architecture
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

Détails : [architecture](docs/study/ARCHITECTURE.md) et
[modèle de données](docs/study/DATA_MODEL.md) (EN) ;
conception technique revue dans
[20_DESIGN/](docs/plan/3SM/20_DESIGN/) (EN).


## Documentation de détail (méthodologie, architecture, base de données)
| Document | Contenu |
|---|---|
| [`management_summary.md`](docs/management_summary.md) | synthèse bilingue (DE/FR) pour les décideurs |
| [`METHODOLOGY.fr.md`](docs/study/METHODOLOGY.fr.md) | comment le marché est mesuré — langage clair, glossaire inclus |
| [`DATA_SOURCE.fr.md`](docs/study/DATA_SOURCE.fr.md) | chaque source et les règles d'accès — langage clair, glossaire inclus |
| [`ARCHITECTURE.md`](docs/study/ARCHITECTURE.md) (EN) | l'outil de collecte et le concept de reporting (semi-technique) |
| [`DATA_MODEL.md`](docs/study/DATA_MODEL.md) (EN) | la base de preuves (technique) |
| [`LEAD_SDS.md`](docs/study/LEAD_SDS.md) (EN) | composés du plomb, droit UE, ce que les fiches révèlent — ou non (semi-technique) |
| [`10_STRATEGY/MASTER.md`](docs/plan/3SM/10_STRATEGY/MASTER.md) (EN) | décisions stratégiques, questions ouvertes, feuille de route |
| [`20_DESIGN/`](docs/plan/3SM/20_DESIGN/) (EN) | conception technique de l'outil + de la base |
| [`30_IMPLEMENTATION/`](docs/plan/3SM/30_IMPLEMENTATION/) (EN) | plans des phases de construction des unités (v0.1.1–v0.1.3, v0.2.0–v0.2.4 construites) — suivi des phases, critères de sortie |
| [`charts/`](docs/study/charts/) (EN) | les schémas, avec leurs sources (référencés depuis les documents de détail) |
| [`README 3SM`](docs/plan/3SM/README.md) (EN) | guide en langage clair de l'arbre de planification |


## Feuille de route
| Phase | Contenu |
|---|---|
| 0 — en cours | Cartographier le paysage des données ; les trois chiffres N1/N2/N3 ; sonder la capacité des registres officiels |
| 1 | Pilote : figer le dictionnaire du plomb ; collecte et analyse des FDS sur un premier échantillon |
| 2 | Base d'échantillonnage et tirage ; collecte de documentation à pleine échelle ; annexe couleurs d'artistes (3213), selon la capacité |
| 3 | Recoupement inter-documents et assurance qualité |
| 4 | Analyse ; base de discussion ; gel de la base de données |


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
    docs/study/                documentation de détail de l'étude (méthodologie, sources,
                               architecture, modèle de données, fond plomb ; traductions, charts/)
    docs/plan/3SM/             notes de planification (système à 3 étages, EN)
    ├── README.md              guide en langage clair (EN)
    ├── MASTER.md, LOG.md      tableau de bord, journal du cycle de vie (EN)
    ├── 10_STRATEGY/           constats de recherche et décisions (quoi & pourquoi) —
    │                          résumés thématiques compacts ; détails dans docs/study/
    ├── 20_DESIGN/             conception technique (comment exactement, EN)
    └── _archive/              matériel remplacé


## État
Les unités outil v0.1.1–v0.2.4 sont construites et testées (412 tests
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


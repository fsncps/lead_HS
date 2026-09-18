---
updated: 2026-09-18
language: fr
translation_of: DATA_SOURCE.md
source_updated: 2026-09-18
---

Sprachen / Langues : [EN](DATA_SOURCE.md) · [DE](DATA_SOURCE.de.md) · **FR**

# Sources de données — registre, accès, provenance

## Résumé

Ceci est le registre opérationnel de toutes les sources de données sur lesquelles s'appuie l'étude : ce que fournit chaque source, comment on y accède, à quelle granularité, selon quelles conditions et avec quel statut de vérification. METHODOLOGY.md explique pourquoi ces sources sont utilisées ; ARCHITECTURE.md (EN) couvre comment elles sont acquises et stockées. Toutes les sources sont publiquement accessibles et gratuites — une contrainte dure du projet. Chaque enregistrement tiré d'une source porte son URL source et sa date de récupération ; les documents bruts sont archivés intacts. Le registre est rédigé pour être lisible sans bagage technique — les termes sont expliqués à leur première utilisation et résumés dans le glossaire ci-dessous.

## Termes utilisés (glossaire en langage clair)

- **Provenance :** l'origine enregistrée de chaque élément de donnée — de quelle source, depuis quelle URL, récupéré à quelle date.
- **robots.txt :** un petit fichier publié par les sites web pour indiquer aux visiteurs automatisés les pages qu'ils peuvent ou non récupérer ; les outils de l'étude s'y conforment.
- **Collecte (scraping) respectueuse :** lire des pages web automatiquement — ici lentement et ouvertement (visiteur identifié, pauses entre requêtes), jamais en martelant un site en masse.
- **Limite de débit (rate limit) :** une pause auto-imposée entre requêtes — au plus une requête toutes les deux secondes par site.
- **API :** une interface de données officielle, lisible par machine, offerte par un fournisseur de statistiques — préférée à la lecture de pages web partout où elle existe.
- **Export CSV :** un fichier tableur téléchargeable (valeurs séparées par des virgules).
- **CN8 :** le code tarifaire douanier à 8 chiffres auquel les statistiques commerciales sont rapportées ; « × partenaire × année » = ventilé par pays partenaire et par année.
- **Référence commerciale (SKU) :** un article en boutique ; l'étude ramène les références aux formulations (une recette, quel que soit le nombre de teintes ou de tailles de pot).
- **Portail B2B :** une boutique en ligne business-to-business pour clients professionnels.
- **Fiche technique (TDS) :** les données de performance d'un produit (temps de séchage, rendement) — à distinguer de la fiche de données de sécurité (FDS), qui liste les ingrédients dangereux (section 3, à partir de 0,1 %).
- **Chaîne UA :** l'identification « user agent » qu'un programme envoie avec chaque requête web ; les outils de l'étude s'identifient et portent une adresse de contact.
- **sha256 (empreinte) :** une empreinte numérique du contenu d'un fichier — des fichiers identiques la partagent toujours, tout changement la modifie ; utilisée pour prouver que les documents archivés sont intacts.
- **PCN / SPIN / PRODCOM / NACE 20.30 :** registres et statistiques utilisés comme approximations de population — définis dans le glossaire de METHODOLOGY.md.
- **Base Access / mdbtools :** SPIN est livré comme fichier de base de données Microsoft Access ; mdbtools est l'utilitaire Linux capable de le lire.
- **Verrouillé par JS :** un site qui n'affiche son contenu qu'après exécution de JavaScript, si bien qu'un simple téléchargement échoue (fedlex) — nécessite un navigateur ou une copie manuelle.

## Classes de sources

Cinq classes avec des identifiants stables (le champ `source.class` de la base) :

- **CS — douane & statistiques commerciales :** EZV/swiss-impex suisse (primaire : structure le marché suisse par provenance) ; Eurostat Comext (contexte UE).
- **PE — preuves produit & FDS (web) :** sites fabricants/marques, portails B2B, catalogues de chaînes de bricolage, accastilleurs marins, boutiques d'art — la base d'échantillonnage et la base de preuves FDS. Multilingue DE/FR/IT/EN.
- **LG — textes juridiques & réglementaires :** LOTC, OPPr, ORRChim, liste négative du SECO, annexes XIV/XVII REACH, décisions JO, registres ECHA.
- **ST — statistiques structurelles & produit :** ECHA PCN, SPIN nordique, Eurostat PRODCOM/SBS — approximations de population et ancres d'échelle.
- **LI — littérature & industrie :** études à comité de lecture, IPEN, CEPE.

## PE — Taxonomie concrète des sources et sites de départ

La classe PE (preuves produit & FDS) est celle d'où provient le corpus réel de FDS/FT. Il n'existe **aucun répertoire européen gratuit unique de fiches de données de sécurité produit** — les grands agrégateurs (MSDSonline, Chemwatch, SDS Europe) sont payants et exclus par la contrainte de coût. Le corpus est donc construit à partir de sites publics de fabricants et de détaillants. Quatre niveaux :

| Niveau | Sources | Ce qu'elles donnent | Flux pertinents pour le plomb |
|---|---|---|---|
| **A — Bibliothèques FDS fabricants/marques** (primaire) | AkzoNobel (Dulux, International, Sikkens), PPG, Sherwin-Williams, Jotun, Hempel, Sika, Sto, Caparol/DAW, Alpina, Tikkurila, Teknos, Farrow & Ball | PDF FDS publics gratuits sur les pages produit / portails FDS | tous |
| **B — Fabricants de niche** (les plus pertinents pour le plomb) | Marine/anticorrosion : Epifanes, Veneziani, Boero, De IJssel, Seajet. Couleurs d'artistes : Old Holland, Zecchi, Kremer Pigmente, Michael Harding, Winsor & Newton, Sennelier, Schmincke, Talens, Maimeri, Blockx, Natural Pigments | FDS + fiches techniques pour les niches pertinentes pour le plomb | minium, couleurs d'artistes |
| **C — Portails détaillants/B2B** | Marine : SVB (svb.de), toplicht.de. Bricolage CH : Coop Bau+Hobby, Migros Do-it+Garten, Hornbach, Bauhaus, Jumbo, OBI. Bricolage UE : B&Q, Leroy Merlin, Castorama, Gamma, Praxis, Toom. Portails commerciaux B2B (DE/FR/IT) | annonces + liens FDS, spécification produit | base d'échantillonnage + FDS |
| **D — Agrégateurs FDS gratuits** | GESTIS (IFA) — au niveau substance seulement, pas de FDS produit ; quelques sites FDS gratuits | données substances, contexte | contexte |

**Remarque sur le niveau D :** GESTIS est au niveau substance (pas de FDS produit) ; la plupart des agrégateurs au niveau produit sont payants. Les niveaux A + C constituent le corpus gratuit pratique ; le niveau B couvre les niches pertinentes pour le plomb.

**Liste des sites d'amorce** (énumérée/confirmée par la sonde v0.1.1 ; le CSV du registre fait foi) :

- Marine : svb.de, toplicht.de
- Artistes : oldholland.com, zecchi.it, kremer-pigmente.com, michaelharding.co.uk, winsornewton.com, sennelier.fr, schmincke.de, talens.com, maimeri.it
- Bricolage (CH) : coop-bauundhobby.ch, migros-doitgarten.ch, hornbach.ch, bauhaus.ch, jumbo.ch, obi.ch
- Bricolage (UE) : hornbach.de, obi.de, bauhaus.de, leroymerlin.fr, castorama.fr, gamma.nl, praxis.nl, diy.com (B&Q)
- Majors : akzonobel.com, ppg.com, sherwin-williams.com, jotun.com, hempel.com, sika.com, sto.com, caparol.de, tikkurila.com, teknos.com

## Registre des sources

| ID | Classe | Source | Fournit | Accès | Granularité | Statut |
|----|-------|--------|----------|--------|-------------|--------|
| CS-1 | CS | swiss-impex.admin.ch (EZV) | importations/exportations CH, 3208/3209 (+3213) | interface web / export CSV (à confirmer) | CN8 × partenaire × année | OUVERT — accès gratuit & granularité à confirmer (phase 0, priorité élevée) |
| CS-2 | CS | Eurostat Comext DS-045409 | commerce extra-UE UE27 | API publique | CN8 × partenaire × année | vérifié (2023 extrait) |
| PE-1 | PE | sites fabricants/marques | catalogues produits, PDF FDS | collecte respectueuse | produit/formulation | OUVERT — liste d'amorce niveaux A + B ; liste de sites construite phases 1–2 |
| PE-2 | PE | chaînes de bricolage (candidates CH : Coop Bau+Hobby, Migros Do-it+Garten, Hornbach, Bauhaus, Jumbo, OBI ; équivalents UE : B&Q, Leroy Merlin, Castorama, Gamma, Praxis, Toom) | annonces de détail | collecte respectueuse | SKU → formulation | OUVERT — niveau C |
| PE-3 | PE | portails B2B / commerciaux (DE/FR/IT) | annonces professionnelles, fiches techniques | collecte respectueuse | produit | OUVERT — niveau C |
| PE-4 | PE | accastilleurs marins, boutiques d'art | flux de niche (minium, couleurs d'artistes) | collecte respectueuse | produit | partiellement vérifié (enregistrements d'amorce existants) — niveaux B/C |
| LG-1 | LG | fedlex / Lexaris | LOTC, OPPr, ORRChim consolidés | téléchargement | article | LOTC vérifiée ; consolidations actuelles ORRChim/OPPr OUVERTES (fedlex verrouillé par JS) |
| LG-2 | LG | SECO (liste négative, rapport de réexamen quinquennal, pages CdD) | catalogue des exceptions, pratique de réexamen | téléchargement | entrée | vérifié |
| LG-3 | LG | EUR-Lex / JO | REACH consolidé, décisions annexe XIV, refus 2022 | téléchargement | entrée | largement vérifié ; référence JO 2022 OUVERTE |
| LG-4 | LG | ECHA (DUR, inventaire EC) | refus d'autorisation ; vérification CAS/EC | web | entrée/substance | DUR vérifié ; contrôles d'inventaire EC en attente pour 2 CAS |
| ST-1 | ST | statistiques PCN ECHA | comptages de formulations (mélanges dangereux) | statistiques publiques | agrégé | OUVERT — localiser les agrégats au niveau formulation |
| ST-2 | ST | SPIN nordique (DK/SE/NO/FI) | comptages de préparations, incidence CAS plomb | téléchargement gratuit base Access | substance × usage × pays | disponible ; voie d'extraction OUVERTE |
| ST-3 | ST | Eurostat PRODCOM / SBS | valeurs de production, comptages de producteurs | API publique | NACE 20.30 | vérifié |
| LI-1 | LI | études / IPEN / CEPE | a priori de calibrage | DOI / web | niveau étude | vérifié |

Le registre croît pendant les phases 0–2 ; la table `source` de la base le reflète (voir DATA_MODEL.md (EN)).

## Passage de sondage (unité v0.1.1)

Avant toute collecte, chaque ligne OUVERTE du registre est sondée une fois (`leadhs probe run`, ARCHITECTURE.md (EN) M0) — une petite visite de test respectueuse qui enregistre ce que la source délivre réellement — et la colonne Statut est mise à jour à partir des résultats du sondage. Le flux par source :

![Comment chaque source est vérifiée : robots et conditions sont respectés, les requêtes sont espacées d'au moins deux secondes, les blocages et surprises sont documentés comme constats, les échantillons sont archivés intacts](charts/probe-process.png)

Par classe :

- **CS :** swiss-impex (CS-1) — confirmer l'accès gratuit, la granularité CN8 × partenaire × année, la couverture 2019–2025, le format d'export ; enregistrer comme constats de sondage. Comext (CS-2) déjà vérifié.
- **PE :** énumérer les sites candidats par flux (chaînes de bricolage, B2B, niches marine/art) ; compter les produits des catalogues (par catégorie lorsque exposée) ; enregistrer robots/conditions/limite de débit/langues et disponibilité des FDS sur un petit échantillon de pages (archivé brut) ; marquer les sites bloqués pour la règle de repli manuel (D4).
- **ST :** SPIN (ST-2) — téléchargement + vérification de la voie d'extraction (mdbtools sur Slackware) ; PCN (ST-1) — localiser les agrégats au niveau formulation (web manuel, enregistré comme tout constat de sondage).
- **LG :** non sondé — la vérification des textes juridiques reste un volet documentaire manuel (dossier juridique phase 0).

Le sondage respecte la discipline d'accès et de collecte ci-dessous — léger par conception (comptages et contraintes, pas de collecte en masse). Les sorties du sondage sont des intrants provisoires de la base d'échantillonnage (MASTER D20).

## Règles de provenance (contraignantes)

1. Chaque enregistrement collecté stocke `source_id`, `url`, `retrieved_at`.
2. Les documents bruts (HTML/PDF) sont archivés exactement comme récupérés sous `data/raw/<source-id>/<sha256>.<ext>` — le nom de fichier est une empreinte numérique (sha256) du contenu, de sorte que toute modification ultérieure est détectable ; la base de données référence cette empreinte, et le magasin brut sert de piste d'audit.
3. Les chiffres porteurs dans les rapports portent nom de source, année, URL et date de consultation (convention du projet, AGENTS.md).
4. Les textes juridiques sont cités par numéro RS/CELEX et date de consolidation (« état »), pas par URL seule.

## Discipline d'accès et de collecte (contraignante)

- Sources publiquement accessibles et gratuites uniquement — pas de bases de données payantes, pas d'études de marché commerciales (contrainte dure).
- Respecter robots.txt et les conditions des sites ; identifier le collecteur (chaîne UA avec adresse de contact) ; limite de débit (défaut ≤ 1 requête / 2 s, file d'attente par domaine) ; pas de martèlement en masse.
- Préférer les exports/API officiels au scraping HTML lorsqu'ils sont proposés (CSV swiss-impex, API Eurostat, téléchargement SPIN).
- Uniquement les FDS publiquement affichées — pas de comptes, pas de paywalls, pas de contournement des CGU (le droit UE impose la FDS gratuite sur demande, REACH art. 31(8), mais cette étude n'utilise que les fiches affichées).
- Si un site bloque la collecte : récupération manuelle du sous-ensemble nécessaire ; méthode d'accès enregistrée par enregistrement.

## DÉCISIONS

- D1 : cinq classes de sources (CS/PE/LG/ST/LI) avec identifiants stables ; la table `source` de la base reflète ce registre.
- D2 : la provenance est contraignante au niveau enregistrement (URL + date de récupération + empreinte brute), pas seulement au niveau document.
- D3 : exports/API officiels préférés au scraping HTML lorsqu'ils existent.
- D4 : pas de comptes, pas de paywalls, pas de contournement des CGU ; repli manuel en cas de blocage, enregistré par enregistrement.
- D5 : chaque ligne OUVERTE du registre est sondée une fois avant la collecte (unité v0.1.1), son statut mis à jour à partir des constats de sondage (MASTER D19).

## POINTS OUVERTS

- CS-1 swiss-impex : confirmer l'accès gratuit, la granularité CN8 × partenaire, la couverture pluriannuelle (2019–2025), le format d'export — phase 0, priorité élevée ; cible de sondage de v0.1.1.
- Liste des sites PE : sites d'amorce des niveaux A/B/C (voir « PE — Taxonomie concrète des sources et sites de départ ») à énumérer et prioriser en phases 1–2 (construction de la base) ; confirmation de la collectabilité commencée par la sonde v0.1.1.
- ST-2 base Access SPIN : voie d'extraction sur Slackware (mdbtools ?) — OUVERT ; vérifié pendant le sondage v0.1.1.
- ST-1 PCN : localiser les agrégats au niveau formulation (pratique de publication ECHA).
- LG-1 verrouillage JS de fedlex pour OPPr/ORRChim consolidées (extraction navigateur nécessaire) — repris du dossier juridique.

## RÉFÉRENCES

- URLs des sources déjà vérifiées lors de la passe de recherche 2026-08-31/09-10 : METHODOLOGY.md §RÉFÉRENCES. Ce registre ajoute les métadonnées d'accès opérationnelles au fur et à mesure de leur confirmation.

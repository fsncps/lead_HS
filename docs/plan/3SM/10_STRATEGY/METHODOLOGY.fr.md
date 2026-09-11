---
unit: v0.1.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-09-11
language: fr
translation_of: METHODOLOGY.md
source_updated: 2026-09-11
---

Sprachen / Langues : [EN](METHODOLOGY.md) · [DE](METHODOLOGY.de.md) · **FR**

# Méthodologie — population, échantillonnage, recoupement

## Résumé

Ce document explique comment l'étude mesure le marché — uniquement à partir de documents, à coût minimal, sans laboratoire. Le cadre : les peintures sous les positions tarifaires 3208 (en phase solvant) et 3209 (en phase aqueuse) sur le **marché de l'UE** (l'objet principal, avec l'attente implicite d'une absence), plus un recensement complet des couleurs à l'huile artistiques (position 3213). En termes simples : les statistiques du commerce extérieur suisse montrent ce qui est importé, d'où et en quelles quantités ; les catalogues de producteurs et de détaillants — collectés systématiquement sur leurs sites web et dédupliqués — fournissent la liste des produits sur laquelle le tirage s'effectue (la « base d'échantillonnage ») ; faute de registre officiel comptant les produits de peinture, la taille de cette liste est estimée en combinant plusieurs sources indépendantes (triangulation). Le marché est divisé en huit groupes, chacun ventilé par provenance ; quelques centaines de produits par groupe sont contrôlés via leurs fiches de données de sécurité (FDS — les fiches normalisées d'information sur les dangers qui accompagnent les produits chimiques professionnels). Un fait réglementaire clé façonne la conception : la Suisse interdit les peintures avec ≥ 0,01 % de plomb total (100 ppm — parties par million), tandis que les FDS européennes ne déclarent les composés de plomb classifiés qu'à partir de 0,1 % — la méthode présente donc un angle mort exactement à la couture réglementaire, déclaré ouvertement dans tous les résultats. Les constats suspects sont recoupés — vérifiés contre des documents indépendants sur le même produit — au lieu d'être testés en laboratoire. Les termes techniques sont expliqués à leur première utilisation et résumés dans le glossaire ci-dessous ; le tableau de correspondance avec la mise en œuvre vers la fin s'adresse au lecteur ingénieur et peut être sauté.

## DÉCISIONS (condensées ; liste faisant foi dans MASTER.md (EN))

- Unité d'analyse = formulation de base ; comptage par référence commerciale rejeté (MASTER D2).
- Échantillonnage stratifié à précision constante, ~2 000–3 000 produits, correction pour population finie lorsque les bases sont petites (MASTER D4).
- Recoupement au lieu du laboratoire — contrainte dure (MASTER D7).
- Couleurs d'artistes SH 3213 en annexe en recensement exhaustif, pas en échantillon (MASTER D13).
- Mise en œuvre : pipeline CLI `leadhs` selon ARCHITECTURE.md (EN) ; sources selon DATA_SOURCE.md ; schéma selon DATA_MODEL.md (EN).

## POINTS OUVERTS

- EZV/swiss-impex — granularité et accès gratuit (phase 0) — conditionne la pondération de la base par provenance ; cible de sondage de l'unité v0.1.1.
- Intrants de triangulation de la population à fixer (phase 0) — les comptages provisoires arrivent avec le recensement des sources v0.1.1.
- Analyse des FDS multilingues et règles de déduplication — calibrage au pilote de la phase 1.

## Termes utilisés (glossaire en langage clair)

- **FDS (fiche de données de sécurité / Sicherheitsdatenblatt / safety data sheet) :** la fiche d'information normalisée qui doit accompagner les produits chimiques professionnels dans l'UE et en Suisse ; la section 3 « Composition » liste les ingrédients dangereux classifiés à partir de 0,1 % en poids.
- **Formulation (formulation de base) :** une recette de peinture, quel que soit le nombre de teintes ou de tailles de pot vendues — l'unité de comptage de l'étude.
- **Référence commerciale (SKU) :** un article en boutique (teinte × taille de pot × marque) ; compter les références gonflerait les chiffres de 10 à 1000 fois sans ajouter d'information — rejeté.
- **CN8 / code SH :** le code tarifaire douanier à 8 chiffres sous lequel un envoi est déclaré (3208 peintures en phase solvant, 3209 aqueuses, 3213 couleurs d'artistes) ; « CN » = nomenclature combinée, la nomenclature tarifaire de l'UE.
- **ppm :** parties par million en poids (10 000 ppm = 1 %).
- **Base d'échantillonnage :** la liste des produits sur laquelle le tirage s'effectue — ici : les catalogues, dédupliqués au niveau formulation.
- **Strate / échantillonnage stratifié :** un segment de marché avec une attente de plomb similaire ; tirage séparé dans chaque segment, afin que les segments rares ne soient pas noyés.
- **Recensement exhaustif :** le décompte complet de chaque membre d'une (petite) population, par opposition à un échantillon — utilisé pour les couleurs à l'huile artistiques (3213).
- **Prévalence :** la part des produits d'un groupe contenant du plomb.
- **Marge d'erreur / intervalle de confiance de 95 % :** la proximité attendue entre une part mesurée sur un échantillon et la part réelle ; l'intervalle contient la valeur réelle dans 95 cas sur 100.
- **Correction pour population finie (FPC) :** une légère réduction de la taille d'échantillon lorsque la population elle-même est petite.
- **Triangulation :** estimer une grandeur en combinant plusieurs sources indépendantes qui en voient chacune une partie.
- **Recoupement :** vérifier un constat suspect contre des documents indépendants concernant le même produit.
- **PCN (notification aux centres antipoison) :** le registre européen des mélanges dangereux notifiés aux centres antipoison — au niveau formulation, mais limité aux mélanges dangereux et non publié ouvertement.
- **SPIN :** la base des registres nordiques de produits (DK/SE/NO/FI) ; rapporte les comptages de préparations contenant une substance donnée.
- **UFI :** un code à 16 caractères sur une FDS européenne qui identifie la formulation précise auprès des centres antipoison.
- **NACE 20.30 :** le code de classification statistique de la « fabrication de peintures, vernis et revêtements similaires ».

## Cadre réglementaire et catégorisation juridique

- **Cassis de Dijon (CH — autonome, non bilatéral) :** les produits légalement commercialisés dans l'UE/l'EEE peuvent être mis sur le marché suisse sans nouvelle approbation suisse (LOTC art. 16a, adopté unilatéralement le 1er juillet 2010 ; l'un des trois instruments LOTC — les AMN selon l'art. 14 LOTC sont distincts et hors champ). Les exceptions (Conseil fédéral ; art. 16a al. 2 let. e en corrélation avec l'art. 4 al. 3–4 : intérêts publics prépondérants, p. ex. la protection de la santé), définies à la naissance du principe, sont cataloguées dans l'OPPr (RS 946.513.8) art. 2 ; **let. a ch. 1 = peintures et vernis contenant du plomb et articles traités (renvoi à l'annexe 2.8 ORRChim)** — en vigueur depuis 2010, toujours listé dans la liste négative du SECO du 1er janvier 2026. Chaîne institutionnelle : demandeur/responsable = BBL (contexte de mandatement 2026-09-10 ; à vérifier avant toute mention dans les livrables), chargé de la mise en œuvre, du suivi, de la révision ; autorité d'exécution OFEV ; **le SECO réexamine l'ensemble du catalogue des exceptions tous les cinq ans** (OPPr art. 3 ; 2023 : maintien ; prochain ~2028) ; base légale de la tenue de la liste : art. 31 al. 2 LOTC (vérifié, Lexaris RS 946.51). L'étude fournit la base de décision dans ce cycle, sans préjuger du résultat.
- **Interdiction suisse de substances :** l'annexe 2.8 ORRChim (rédaction 2005 ; texte actuel OUVERT) définit les peintures au plomb comme celles avec plomb total ≥ 0,01 % (100 ppm) et interdit leur mise sur le marché (ainsi que les articles traités) — plus strict que l'UE, qui n'interdit que les carbonates/sulfates de plomb *dans les peintures* (annexe XVII 16/17) et a mis fin à l'approvisionnement légal en chromate de plomb via le refus d'autorisation (17 mars 2022).
- **Frontière produits chimiques/CdD (Portail d'annonce des produits chimiques) :** un produit entre sur le marché soit sous le droit suisse des produits chimiques, soit sous le régime CdD — pas de mélange ; les obligations de suivi (registre des produits, FDS) survivent au CdD.
- **Conséquence de conception — champ « catégorie juridique » :** chaque enregistrement de la base porte : code SH/CN (inféré), catégorie juridique (peinture / couleur d'artiste / pigment / article traité), provenance (CH/UE/pays tiers) et si l'interdiction suisse des 100 ppm de plomb total est vraisemblablement touchée (composés déclarés et fourchettes) — la méthode FDS ne peut pas mesurer le plomb total.
- **Avertissement majeur :** seuil d'interdiction suisse 100 ppm plomb total < seuil de déclaration FDS UE 0,1 % (1000 ppm, composés classifiés). Des produits conformes au droit de l'UE et entièrement documentés peuvent tout de même dépasser invisiblement l'interdiction suisse pour cette étude. Énoncé dans chaque livrable ; non délimitable expérimentalement (pas de laboratoire).

## Population et définition

- Population cible : formulations distinctes de peintures/vernis (SH 3208/3209) disponibles sur le **marché de l'UE** — l'objet principal — avec le **marché suisse comme métrique additionnelle** (production nationale + importations ; la règle suisse des 100 ppm se superpose à la présence conforme au droit de l'UE). Les estimations de population UE/EEE servent aussi d'ancres d'échelle.
- **Aucun registre ne les compte** — la taille de la population doit être triangulée.
- Unité = formulation de base : les teintes co-notifiées comme une seule (pratique KemI) ; les variantes de teintage au point de vente ne constituent pas des entrées PCN distinctes (règl. (UE) 2020/1676). Le comptage au niveau référence est explicitement rejeté (gonfle N de 1 à 3 ordres de grandeur sans ajouter d'information).
- Hypothèse de travail : **10⁴–10⁵ formulations dans l'EEE** ; base suisse vraisemblablement d'un ordre de grandeur inférieure (à fixer en phase 0). Ancres UE : ~3 200 producteurs UE27 (NACE 20.30, Eurostat SBS 2019–20) ; CEPE ~800 membres ≈ 85 % de 17 Md€ ; commerce extra-UE UE27 : 1,1 Md€ à l'entrée / 4,3 Md€ à la sortie, ~860 kt (2023, Comext DS-045409, sommes CN8 calculées).
- **Annexe recensement — SH 3213 couleurs à l'huile artistiques :** les couleurs d'artistes aux pigments de plomb (blanc de Cremnitz PW1, jaune de Naples PY41, jaune de plomb-étain, minium) sont hors 3208/3209 (CN 2026 : 3213 10 00 / 3213 90 00) et invisibles dans les bases issues des statistiques commerciales, pourtant le cas documenté le plus clair de couleurs au plomb légalement sur le marché de l'UE (Old Holland NL ; Zecchi IT ; Michael Harding UK→UE non vérifié). Population petite (des dizaines de marques) → **recensement exhaustif, pas un échantillon** : énumérer les marques, contrôler catalogues/FDS par pays, enregistrer les pigments de plomb et les restrictions nationales éventuelles (régimes SE réservés aux professionnels, etc.).

## Construction de la base d'échantillonnage

1. **Statistiques du commerce extérieur suisse (EZV/swiss-impex) :** importations/exportations au niveau CN8 par pays partenaire, pluriannuelles — structure le marché par provenance et pondère la dimension provenance de chaque strate. Disponibilité/granularité à confirmer en phase 0 (OUVERT). Inclure 3213 pour l'annexe recensement.
2. **Catalogues producteurs/détaillants suisses et UE** (portails B2B, chaînes de bricolage, sites de marques ; DE/FR/IT), lus et dédupliqués au niveau formulation — la véritable base d'échantillonnage et l'épine dorsale de la base de données. Le volet UE applique la même méthode aux catalogues côté UE ; produits d'amorce en dossier : Epifanes WERDOL Bleimennige (accastillage DE, FDS 2021), BRAVA blymönja (SE, professionnels uniquement, autorisation), Old Holland Cremnitz White No. 3 (PW1), Zecchi (biacca, giallorino, minio, peinture à l'huile PY41).
3. **Proximations côté UE (contexte/échelle) :** statistiques PCN de l'ECHA (niveau formulation, EEE entier, mélanges dangereux uniquement ; ~19 % de non-notification selon le pilote du Forum ECHA S1-2025 → facteur de sous-comptage) ; SPIN nordique (registres DK/SE/NO/FI ; base Access ~1 Go ; comptages par catégorie d'usage ; requêtes par CAS du plomb possibles ; noms de produits confidentiels) ; Eurostat PRODCOM.
4. **Statistiques structurelles suisses** (OFS/SBS) : comptages de producteurs nationaux et valeurs de production.

## Stratification (projet : 8 strates de segments × provenance)

| # | Strate | A priori CN | A priori plomb |
|---|---|---|---|
| S1 | Décoratif aqueux | 3209 | ~0 |
| S2 | Décoratif solvant/glycéro | 3208 | très faible (siccatifs possibles — flux ouvert clé) |
| S3 | Primaires anticorrosion/protection de l'acier | 3208 | **élevé (minium ; niche UE documentée)** |
| S4 | Revêtements marine & conteneurs | 3208 | élevé (documenté : WERDOL) |
| S5 | Peintures de marquage routier | 3208 | modéré (héritage PbCrO₄ ; Turner & Filella 2022 : 63 % des échantillons >10 mg/kg) |
| S6 | OEM industriel (coil, réparation, machinerie) | 3208 | modéré (chromates terminés 2022) |
| S7 | Marques importées de pays tiers | les deux | **élevé** (prévalence des marchés d'origine) |
| S8 | Résiduel (bois, sols, spécialités) | les deux | faible |

Plus l'**annexe recensement 3213** (couleurs d'artistes, pas d'échantillonnage). Chaque strate est ventilée par provenance — production CH / importation UE / importation pays tiers — avec des tirages pondérés par les parts d'importation EZV (phase 0).

## Taille de l'échantillon (à précision constante)

- La formule standard (n = z²·p(1−p)/e² — en mots : le nombre à contrôler dépend de la marge d'erreur visée et de la part attendue, **pas** de la taille du marché) donne : **385** produits par groupe pour ±5 % ; **≈ 811** pour ±1,5 % sur des occurrences plus rares (confiance 95 %).
- Correction pour population finie (une réduction lorsque le groupe lui-même est petit) : n/(1+n/N).
- Conception complète ≈ 2 000–3 000 produits ; pilote ≈ 300–800.
- Remarque : ce qui compte, c'est combien de produits sont contrôlés, pas la fraction du marché que cela représente ; si la population totale N ≈ 30–50k, la conception retombe incidemment à 5–10 %.

## Détermination du plomb (documents uniquement)

- Primaire : analyse de la section 3 des FDS contre le dictionnaire du plomb (voir `LEAD_SDS.md` (EN)) ; enregistrer fourchettes de concentration, classification, obsolescence (format antérieur à 2021/878 = signal rouge), UFI, déclarations de la section 15. FDS des marchés CH/UE typiquement en DE/FR/IT/EN — gestion des langues requise dans le pipeline.
- Secondaire/comptages : comptages de préparations par CAS du plomb SPIN (estimation de contexte nordique pour le monde des registres UE).
- **Recoupement au lieu du laboratoire (pas de laboratoire, contrainte dure) :**
  - chaque suspect positif recoupé, dans la mesure du disponible, avec des documents indépendants sur le même produit : fiches techniques, texte d'étiquette, annonces de détaillants, déclarations de producteurs, versions antérieures de FDS, variantes de marque inter-marchés ;
  - score de cohérence ; les contradictions entre documents sont elles-mêmes des constats rapportables ;
  - un silence cohérent sur plusieurs documents indépendants = preuve faible d'absence, rapportée comme telle.
- **Limites énoncées (quantifiées par hypothèse, pas par mesure) :** plomb déclaré uniquement (≥0,1 % composés classifiés) ; la bande 100–1000 ppm (interdiction suisse sous le seuil de déclaration UE), le plomb d'impureté et les fiches sous-déclarantes ou périmées sont invisibles. La base de discussion finale porte une section explicite de limites.

## Volet commerce extérieur & juridique suisse (phase 0, documents uniquement)

- Extraction EZV/swiss-impex : CN8 × partenaire, 2019–2025, 3208+3209 (+3213).
- Vérifier les textes consolidés actuels : annexe 2.8 ORRChim (RS 814.81) — seuil, articles traités, exceptions ; OPPr (RS 946.513.8) — catalogue art. 2 et corps de l'art. 16 ; libellé FR.
- Documenter la chaîne de gouvernance CdD de l'exception plomb à partir de sources publiques : bureau demandeur/responsable, procédure de réexamen (OPPr art. 3), acte de naissance 2010 (message/explicatif) — rôle du BBL actuellement seulement selon le contexte de mandatement.
- Volet UE : référence JO du refus d'autorisation des chromates de plomb du 17 mars 2022 ; guidage ECHA (le cas échéant) annexe XVII 16/17 vs couleurs d'artistes ; balayage du commerce de détail des primaires au minium en FR/IT.

## Correspondance avec la mise en œuvre

| Étape de méthode (ce document) | Étage du pipeline | CLI | Entités de données |
|---|---|---|---|
| Recensement des sources & sondage | probe | `probe run`, `probe report` | probe_run, probe_finding → population_anchor |
| Construction de la base (catalogues) | acquire, ingest | `acquire run`, `ingest sightings` | product, sighting |
| Statistiques commerciales | acquire, ingest | `acquire run` (CS-1/CS-2) | trade_stat |
| Stratification & populations | frame | `frame set` | frame_stratum, population_anchor |
| Taille de l'échantillon & tirage | sample | `sample plan`, `sample draw` | sampling_run, sample_selection |
| Détermination du plomb | parse | `parse sds`, `review` | sds_finding, lead_compound |
| Recoupement | corroborate | `review`, `corroborate` | corroboration |
| Annexe recensement (3213) | ingest, parse | produits marqués census | product |
| Analyse & rapport | analyze, report | `analyze prevalence`, `report build` | dérivé + tout |

## Diagrammes

`charts/lead-decision-tree` rend sous forme d'arbre de décision la logique de détermination du plomb et d'angle mort de ce document :

![Comment un produit est jugé : sa fiche de données de sécurité liste-t-elle un composé de plomb, est-il déclaré à partir de 0,1 %, l'interdiction suisse des 100 ppm s'applique-t-elle vraisemblablement, et les documents indépendants sont-ils d'accord ?](charts/lead-decision-tree.png)

Les schémas de stratégie sont des propositions — les documents écrits l'emportent. Index : `charts/README.md` (EN).

## RÉFÉRENCES (consultées le 31 août 2026 ; ajouts LOTC/CdD 10 septembre 2026)

- Liste négative CdD du SECO, 1er janvier 2026 : seco.admin.ch/dam/de/sd-web/8jJ6a7UYFYzf/Negativliste-SECO-Januar-2026-DE.pdf
- Rapport de réexamen quinquennal SECO/WBF, 29 mars 2023 : seco.admin.ch/dam/de/sd-web/jUlHD7NFv0hM/BERICHT_Fünfjährige Überprüfung der CdD-Ausnahmen gemäss Art. 3 VIPaV, 2023.pdf
- Page Cassis-de-Dijon du SECO : seco.admin.ch/de/cassis-de-dijon-prinzip
- Page LOTC du SECO (trois instruments) : seco.admin.ch/de/bundesgesetz-technische-handelshemmnisse
- Texte intégral LOTC RS 946.51, état au 1er mai 2017 (Lexaris ; art. 4, 16a, 31 al. 2) : lexaris.de/book/version/documentflat/head/222871
- Page AMN du SECO (délimitation du champ seulement) : seco.admin.ch/de/allgemeine-informationen-mra
- Portail d'annonce des produits chimiques, guide CdD : anmeldestelle.admin.ch/de/cassis-de-dijon
- Art. 16a LOTC (état 2010, archivé) : web.archive.org/web/20101011224435/http://www.admin.ch/ch/d/sr/946_51/a16a.html
- OPPr RS 946.513.8, art. 1–2 (état 2010, archivé) : web.archive.org/web/20101011224439/http://www.admin.ch/ch/d/sr/946_513_8/a2a.html
- Annexe 2.8 ORRChim (état 2005, archivé) : web.archive.org/web/20060210084345/http://www.admin.ch/ch/d/sr/814_81/app23.html
- CJUE 120/78 Rewe/Cassis de Dijon : eur-lex.europa.eu/legal-content/DE/TXT/HTML/?uri=CELEX:61978CJ0120
- CJUE C-389/19 P (25 février 2021, effets maintenus) : iclr.co.uk/document/2021000886/casec38919p/html ; Tribunal T-837/16 (7 mars 2019) : eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:62016TJ0837
- Registre des utilisations en aval de l'ECHA (toutes les autorisations de chromate de plomb refusées) : echa.europa.eu/du-66-notifications
- Turner & Filella 2022, peintures routières, 11 pays : DOI 10.1016/j.envpol.2022.120492
- Epifanes WERDOL Bleimennige (FDS 2021 + annonces) : toplicht.de/de/farben-bootsbau/farben-konservierung/grundierungen/ueber-wasser/5911/epifanes-werdol-blei-mennige
- BRAVA blymönja (SE, professionnels uniquement) : raseglarhuset.com/frg-fernissa/blymja
- Old Holland Cremnitz White No. 3 (PW1) : oldholland.com/classic_oil_colours/d3-cremnitz-white/
- Zecchi (biacca, giallorino, minio, PY41) : zecchi.it/products.php?category=29 ; category=36
- CN 2026 position 3213 : zolltarifnummern.de/2026/3213
- Plateforme suisse du commerce extérieur (source phase 0 prévue) : swiss-impex.admin.ch
- API Eurostat Comext DS-045409 : ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409
- Eurostat SBS sbs_na_ind_r2 (NACE C2030) : ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_na_ind_r2
- CEPE : cepe.org/about-the-industry/
- Pilote PCN du Forum ECHA (février 2026, via source secondaire) : cirs-group.com/en/chemicals/echa-releases-pilot-project-report-on-pcn-enforcement-nearly-20-of-companies-failed-to-meet-compliance-obligations
- SPIN : web.archive.org/web/20250116153625/http://spin2000.net/ ; téléchargement de la base : web.archive.org/web/20240615081956/http://spin2000.net/?page_id=54
- FAQ KemI (co-notification des teintes) : web.archive.org/web/20210227095243/https://www.kemi.se/fragor-och-svar/fragor-och-svar-om-produktregistret
- Codes CN 2025 : zolltarifnummern.de/2025/3208, /3209 (validés contre la liste de codes Comext)

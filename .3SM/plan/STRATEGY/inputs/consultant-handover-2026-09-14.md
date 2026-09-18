# Handover: EU Paint Product Registries and Market-Size Estimation

**Project:** `lead_HS`  
**Scope:** EU-market paints and varnishes under HS/CN families **3208** and **3209**  
**Purpose:** Identify large public product-level data sources and improve the methodology for estimating the total number of distinct paint formulations/products on the EU market.  
**Project repository:** https://github.com/fsncps/lead_HS  
**Status:** Research handover / source-expansion proposal  
**Date:** 2026-09-14

---

## 1. Executive conclusion

The project already has a strong starting source in the **EU Ecolabel Catalogue (ECAT)** and a second sustainability-oriented source in **Nordic Swan**. Their weakness is selection bias: environmentally labelled paints are particularly unlikely to contain lead and are not representative of the full coatings market.

The next source-expansion step should therefore prioritize databases selected by **chemical hazard, occupational use, construction-market presence, SDS availability, or regulatory authorization**, rather than additional ecolabel catalogues.

The most promising newly identified sources are:

1. **KemiDigi / Finnish Chemical Products Register** — public individual records for dangerous chemical products placed on the Finnish market; highly complementary to ECAT.
2. **BG BAU WINGIS / GefKomm-Bau** — German construction-chemical/SDS ecosystem searchable by manufacturer, trade name, article number and article description.
3. **BASTA** — very large Swedish/Nordic construction-product database with company, product and article-number identity.
4. **INIES** — French construction environmental-declaration database; important because one declaration may cover many explicitly listed **commercial references**, so the true product-level yield may be much larger than the FDES count suggests.
5. **eBVD** — structured Swedish building-product declarations and API integration, useful for product identity and cross-linkage.
6. **Quick-FDS** — large supplier-mediated SDS discovery source, particularly useful for identifying exact product/SDS pairs.
7. **ECHA Biocidal Products, PT21 antifouling products** — regulator-maintained niche list of marine coatings with strong identifiers and bulk-export capability.

The main methodological recommendation is to stop treating the EU product-total problem primarily as a collection of independent magnitude guesses. Instead:

- build several **overlapping identifiable product lists** with different selection mechanisms;
- link the same products/formulations across lists;
- estimate the unseen population using **multiple-list capture-recapture / multiple-systems estimation (MSE)**;
- independently construct a **manufacturer census × measured assortment distribution** estimator as a validation route.

The project should continue to preserve both:
- the **native product/SKU/article level**, and
- a derived **base-formulation level**.

Do not collapse variants during ingestion. Collapse after record linkage.

---

# 2. Target unit and terminology

The study's primary scientific unit should remain:

> **Base formulation:** one paint/coating recipe, regardless of how many shades, pack sizes, EANs/GTINs or retail SKUs are sold from it.

However, source systems rarely expose that unit directly. They may count:

- catalogue entries,
- article numbers,
- GTIN/EAN SKUs,
- trade names,
- product families,
- SDS documents,
- hazardous-mixture notifications,
- UFI-bearing mixtures,
- ecolabel licences,
- regulatory authorisations,
- environmental declarations.

Therefore the database should store the source-native identity first and derive formulation entities later.

A useful hierarchy is:

```text
manufacturer / legal entity
    ↓
brand
    ↓
commercial product / trade name
    ↓
article / SKU / GTIN / EAN / package / shade
    ↓
SDS / UFI / formulation evidence
    ↓
derived base formulation
```

One source row must never be assumed to equal one formulation without evidence.

---

# 3. Source-selection principle

The purpose of adding sources is not simply to increase `N`.

The project needs **different ascertainment mechanisms**.

A useful conceptual set is:

| Ascertainment mechanism | Example sources | Expected bias |
|---|---|---|
| Environmental certification | ECAT, Nordic Swan, M1 | lower-hazard / greener products |
| Hazard notification | KemiDigi, national chemical registers | hazardous products |
| Occupational chemical use | WINGIS / GefKomm-Bau | professional/construction chemicals |
| Construction-product declaration | BASTA, INIES, eBVD | construction coatings |
| Manufacturer / SDS publication | Quick-FDS, manufacturer portals | documented commercial products |
| Regulatory authorization | ECHA PT21 | regulated niche products |
| General retail | DIY chains, B2B retailers | consumer / shelf-available products |
| Industry association | CEPE, national associations | manufacturer census, not product census |

Different biases are desirable because the **overlap pattern** between differently selected lists is what can eventually estimate unseen products.

---

# 4. High-priority product-level sources

## 4.1 KemiDigi — Finnish Chemical Products Register

**Priority:** A+  
**Primary role:** hazardous-product registry; counterweight to ECAT  
**Country:** Finland  
**Operator:** Finnish Safety and Chemicals Agency (Tukes)

### URLs

- KemiDigi:  
  https://www.kemidigi.fi/
- Tukes chemical information / notification pages:  
  https://tukes.fi/en/chemicals
- Finnish public-service description of Chemical Products Register:  
  https://www.suomi.fi/services/webpage/the-chemical-products-register-finnish-safety-and-chemicals-agency-tukes/e65f9c7e-87b4-4b1f-8f5b-8711eb3792cb

### Why this source matters

KemiDigi contains information submitted for **dangerous chemical products placed on the Finnish market**.

This makes its selection mechanism almost the opposite of ECAT:

```text
ECAT       → environmentally certified / preferentially low-hazard
KemiDigi   → dangerous chemical products requiring notification
```

For the lead study this is exceptionally valuable.

### Useful record fields observed / expected

Individual public records can expose:

- trade name;
- responsible company / manufacturer / importer / operator;
- intended use / use codes;
- physical state;
- CLP classification;
- product-level KemiDigi record identifiers;
- sometimes SDS attachments;
- other regulatory chemical information.

### Research tasks

1. Determine whether public records can be enumerated exhaustively.
2. Identify query/filter fields corresponding to paints, varnishes and coatings.
3. Determine whether any product/use taxonomy maps cleanly onto 3208/3209.
4. Establish public-record count for relevant paint/coating categories.
5. Draw a reproducible random sample of e.g. 100 records.
6. Measure:
   - manufacturer completeness;
   - product/trade-name completeness;
   - product-record ID completeness;
   - article/GTIN/UFI/SDS availability;
   - SDS publication rate.
7. Test linkage against ECAT, BASTA, WINGIS and manufacturer catalogues.

### Main limitation

KemiDigi represents:

- Finland, not the whole EU;
- dangerous chemicals, not all paints.

It is therefore not a standalone denominator.

It is potentially excellent for:
- hazard-tail coverage;
- overlap modelling;
- lead-relevant sampling;
- national scaling benchmarks.

---

## 4.2 BG BAU WINGIS / GefKomm-Bau

**Priority:** A+  
**Primary role:** occupational/construction chemical product + SDS identity  
**Country:** Germany  
**Operator:** BG BAU / GISBAU

### URLs

- WINGIS Online:  
  https://www.wingisonline.de/
- BG BAU GISBAU / GefKomm-Bau information:  
  https://www.bgbau.de/themen/sicherheit-und-gesundheit/gefahrstoffe/gisbau/gefkomm-bau
- BG BAU GISBAU:  
  https://www.bgbau.de/themen/sicherheit-und-gesundheit/gefahrstoffe/gisbau

### Why this source matters

WINGIS is unusually close to the project's preferred identity structure.

Search and indexing are built around fields such as:

- manufacturer;
- trade/product name;
- article number;
- article description;
- GISCODE / product-group information;
- SDS-derived information.

This is much more useful than a generic product catalogue.

### Potential identity tuple

```text
manufacturer
+ trade name
+ article number
+ SDS identity/version
+ GISCODE/product group
```

### Research tasks

1. Determine whether the catalogue can be enumerated rather than merely searched.
2. Find any index, sitemap, export, endpoint or documented interface.
3. Determine paint/coating categories:
   - dispersion paints;
   - varnishes;
   - alkyd paints;
   - primers;
   - anticorrosive coatings;
   - floor coatings;
   - industrial coating systems.
4. Count relevant product records.
5. Test article-number uniqueness.
6. Test whether SDS links are current and directly retrievable.
7. Establish manufacturer and formulation overlap with KemiDigi / BASTA / ECAT.

### Main limitation

Public search is confirmed; public **bulk enumerability** remains to be demonstrated.

This should be treated as a dedicated technical probe.

---

## 4.3 BASTA

**Priority:** A+  
**Primary role:** very large article-level construction-product catalogue  
**Country:** Sweden / Nordic market orientation

### URLs

- BASTA home/database:  
  https://www.bastaonline.se/
- English site:  
  https://www.bastaonline.se/en

### Scale

BASTA publicly describes a database containing **more than 200,000 construction and civil-engineering products/articles**.

Not all are paints.

The important question is the size of the paint/coating subset.

### Useful identity fields

Observed product pages expose combinations of:

- company;
- product/trade name;
- article number;
- unique product/article page;
- classification/category;
- assessment/declaration information;
- linked documentation.

### Why this source matters

Compared with ECAT, BASTA is not simply a list of ecolabel awards. Its article-level construction-product database is much broader.

It could supply:

- thousands of identifiable coating products;
- cross-links to eBVD;
- manufacturer/article identifiers;
- useful chemical / sustainability metadata.

### Research tasks

1. Find category/taxonomy codes corresponding to paint/coatings.
2. Test obvious Swedish building-product codes such as relevant BSAB groups.
3. Derive:
   - total BASTA article count;
   - paint/coating article count;
   - distinct manufacturer count;
   - distinct `(manufacturer, article number)` count;
   - distinct `(manufacturer, product name)` count.
4. Probe API availability and access conditions.
5. Sample 100 paint records with full fields.
6. Measure article-number / GTIN / document completeness.
7. Test overlap with eBVD, ECAT, KemiDigi and manufacturer sites.

### Main limitation

BASTA has its own sustainability/assessment selection.

It must not be treated as an unbiased representation of the entire coatings market.

Also:

> BASTA and eBVD must not automatically be treated as independent lists in capture-recapture models because they exchange data.

---

## 4.4 INIES

**Priority:** A  
**Primary role:** France; construction products; potentially large commercial-reference expansion

### URLs

- INIES:  
  https://www.inies.fr/
- Public INIES database:  
  https://base-inies.fr/
- INIES webservice information:  
  https://www.inies.fr/le-webservice/

### Critical methodological point

Do not measure INIES only as:

```text
number of FDES declarations
```

An FDES can cover many explicitly named:

> **références commerciales couvertes**

Therefore the relevant extraction should be:

```text
FDES
    ↓
declarant/manufacturer
    ↓
commercial references covered
    ↓
individual commercial product identities
```

This may multiply the usable product-level yield substantially.

### Relevant category

A category exists for approximately:

```text
floor/wall coverings / paints / decorative products
```

The FDES count is only the top-level document count.

The project needs the **commercial-reference count**.

### Research tasks

1. Enumerate paint/decor FDES entries.
2. Parse `Références commerciales couvertes`.
3. Store:
   - FDES ID;
   - manufacturer/declarant;
   - brand;
   - each commercial reference;
   - relevant product category;
   - declaration validity dates.
4. Estimate:
   - references per FDES;
   - distinct commercial references;
   - distinct manufacturers.
5. Determine whether the public UI permits reproducible bulk extraction.
6. Keep paid/licensed webservice access outside scope unless the project constraint changes.

### Main limitation

Public consultation is free, but convenient bulk/webservice access may be licensed.

The no-paid-data constraint therefore requires careful access review.

---

## 4.5 eBVD

**Priority:** A−  
**Primary role:** structured Nordic building-product declarations and linkage  
**Country:** Sweden / Nordic

### URLs

- eBVD:  
  https://www.ebvd.org/
- API information:  
  https://www.ebvd.org/en/about-ebvd/api/

### Useful characteristics

eBVD publishes structured environmental building-product declarations.

Potential fields include:

- company;
- product;
- product category;
- construction-use information;
- material/chemical information;
- declaration identifiers;
- related product documentation.

The service also connects to other Swedish construction-product databases.

### API

The API is publicly described as available free of charge after agreement/account setup.

This should be investigated because it may provide a clean structured extraction route.

### Main limitation

eBVD and BASTA are linked systems.

For population-estimation purposes they should initially be modelled as part of the same source family or with an explicit dependency term.

---

## 4.6 Quick-FDS

**Priority:** A− / B+  
**Primary role:** large SDS discovery catalogue  
**Geography:** France / European suppliers

### URL

- Quick-FDS:  
  https://www.quickfds.com/

### Why it matters

Quick-FDS distributes supplier-provided safety data sheets and covers a large number of supplier companies.

This may be especially useful for:

- exact commercial product names;
- manufacturer/supplier identification;
- SDS retrieval;
- language/version information;
- historic/current SDS matching.

Paint products from major European brands are represented.

### Research tasks

1. Determine whether supplier and product lists are enumerable.
2. Estimate paint/coating product count.
3. Identify stable product IDs or document IDs.
4. Test direct SDS retrieval.
5. Determine whether crawl/export terms permit research-scale acquisition.
6. Measure overlap against manufacturer SDS portals.

### Limitation

Quick-FDS may be more useful as an **SDS corpus/discovery source** than as a clean exhaustive population frame.

Do not assume it is complete for all products of participating manufacturers.

---

## 4.7 ECHA Biocidal Products — PT21 antifouling products

**Priority:** B+  
**Primary role:** clean regulator-maintained marine-coatings stratum  
**Geography:** EU / EEA

### URLs

- ECHA biocidal products:  
  https://echa.europa.eu/information-on-chemicals/biocidal-products
- ECHA main site:  
  https://echa.europa.eu/

### Relevant product type

**PT21 — Antifouling products**

These are coatings used to control fouling organisms on:

- vessels;
- aquaculture equipment;
- other submerged structures.

### Useful fields

Records can include:

- trade name;
- authorisation number;
- authorisation holder;
- authorised market/country;
- active substances;
- authorisation dates;
- SPC / regulatory documents.

ECHA exposes bulk-download/export mechanisms for its biocidal product data, including structured formats.

### Why it matters

This is not a general-market denominator.

It is valuable because it offers:

- a well-defined regulatory niche;
- strong product identity;
- professional/marine coatings;
- a chemically interesting segment that ecolabel databases underrepresent.

### Research tasks

1. Export all PT21 records.
2. Deduplicate:
   - same product authorised in multiple Member States;
   - same formulation under multiple trade names where evidence permits.
3. Link manufacturer/authorisation holder to marine supplier catalogues.
4. Determine which products fall under 3208/3209 versus other tariff treatment.

---

# 5. Secondary / supplementary sources

## 5.1 ECAT — EU Ecolabel Catalogue

**Role:** existing high-quality identifiable source  
**Bias:** environmentally certified products

### URLs

- EU Ecolabel:  
  https://environment.ec.europa.eu/topics/circular-economy/eu-ecolabel-home_en
- EU Ecolabel catalogue entry point:  
  https://environment.ec.europa.eu/topics/circular-economy/eu-ecolabel-home/consumer/products-covered-eu-ecolabel_en

The project already has ECAT extraction working and has demonstrated:

- large paint-product counts;
- licence identifiers;
- company information;
- some GTIN/EAN coverage;
- reproducible exports.

Retain as a core list, but do not use it as a representative lead-prevalence sample.

---

## 5.2 Nordic Swan

**Role:** second ecolabel / Scandinavian overlap list  
**Bias:** environmentally certified products

### URLs

- Nordic Swan Ecolabel:  
  https://www.nordic-swan-ecolabel.org/
- Product search:  
  https://www.nordic-swan-ecolabel.org/product-search/

The project has already found a CSV-like export route.

Continue the ECAT × Nordic Swan overlap exercise, but treat them as relatively similar ascertainment mechanisms.

---

## 5.3 M1 Emission Classification

**Role:** Finnish low-emission construction products  
**Bias:** low-emission / construction-oriented products

### URL

https://ymparisto.rakennustieto.fi/en/m1-emission-classification-of-building-materials

Potentially useful as:
- another Finnish product list;
- source of manufacturer/product identity;
- overlap with KemiDigi.

Not a priority denominator.

---

## 5.4 EPD / construction-product systems

Potential secondary sources include:

- IBU: https://ibu-epd.com/
- Environdec / International EPD System: https://www.environdec.com/
- ECO Platform: https://www.eco-platform.org/
- baubook: https://www.baubook.info/
- DGNB Navigator: https://navigator.dgnb.de/

These are useful for:

- product identity;
- manufacturer names;
- category classification;
- product-family documentation;
- cross-linkage.

They are generally weaker as unbiased population frames.

---

## 5.5 Safety Gate

**Role:** unsafe/non-compliant product discovery  
**Bias:** enforcement / hazard incidents

### URL

https://ec.europa.eu/safety-gate-alerts/screen/webReport

Do not use as a denominator.

Potentially valuable for:
- lead-containing product case discovery;
- model/article/barcode identifiers;
- country and brand information;
- enforcement context.

---

## 5.6 EU BTI / EBTI tariff-classification records

**Role:** HS/CN classification validation  
**Bias:** products for which binding tariff decisions were requested

### URL

https://ec.europa.eu/taxation_customs/dds2/ebti/ebti_home.jsp

Useful for answering:

> Does this type of named coating actually classify under CN 3208/3209?

Not useful as a market-product census.

---

# 6. Critical issue: HS 3208 / 3209 are rarely product-database fields

Most product databases do **not** contain HS/CN codes.

Therefore the project should distinguish:

```text
product discovery
```

from:

```text
tariff classification
```

A product may first be discovered from KemiDigi, WINGIS, BASTA, etc. and only later assigned to 3208/3209 based on:

- product type;
- solvent/water medium;
- chemistry;
- SDS/TDS;
- product description;
- known CN classification;
- BTI examples;
- explicit manufacturer customs information.

A source should not be rejected merely because it lacks HS codes.

Instead store:

```text
hs_scope_status =
    confirmed_3208
    confirmed_3209
    probable_3208
    probable_3209
    ambiguous
    out_of_scope
```

plus the evidence used.

---

# 7. Revised market-size methodology

## 7.1 Problem

There is no known public EU master register of every paint product.

Current magnitude benchmarks mix different units:

- SKU;
- trade name;
- notification;
- dossier;
- formulation;
- ecolabel product;
- manufacturer assortment.

Scaling these directly produces wide and assumption-heavy ranges.

The next methodology should exploit **overlap between actual product lists**.

---

# 8. Multiple-list capture–recapture / multiple-systems estimation

## 8.1 Core idea

Suppose several incomplete lists cover the same population.

For every linked formulation, record whether it appears in each list.

Example:

```text
formulation_id | ECAT | KemiDigi | BASTA | WINGIS | INIES
---------------|------|----------|-------|--------|------
F0001          | 1    | 0        | 1     | 0      | 1
F0002          | 0    | 1        | 0     | 1      | 0
F0003          | 1    | 1        | 1     | 1      | 0
...
```

Products absent from every list are invisible.

The distribution of observed capture patterns contains information about how many invisible records are likely to exist.

This is the same general family as capture-recapture estimation, extended to several administrative lists.

---

## 8.2 Why simple two-list estimation is insufficient

A naive two-list estimator assumes, approximately:

- homogeneous capture probability;
- independence between lists.

Neither assumption holds here.

Examples:

- large multinational brands are much more likely to occur in every source;
- BASTA and eBVD exchange data;
- ECAT and Nordic Swan select similar environmental products;
- WINGIS and manufacturer SDS libraries may share source documents;
- KemiDigi captures hazardous products preferentially.

Therefore use:

- log-linear multiple-systems estimation;
- Bayesian MSE;
- explicit list-interaction terms;
- stratification.

Do not use a simple Lincoln–Petersen estimator as the final method.

---

# 9. Stratification

Capture probability will differ enormously between market segments.

At minimum consider stratifying by:

### Product chemistry / customs family

```text
3208 — non-aqueous / solvent-borne
3209 — aqueous / water-borne
```

### Market segment

```text
decorative
industrial
protective / anticorrosive
marine
floor coatings
wood coatings
specialty
```

### Channel

```text
consumer / retail
professional construction
industrial B2B
marine
```

### Manufacturer scale

```text
large multinational
medium regional
small/local
```

### Geography

Possible broad blocks:

```text
Nordic
DACH
France/Benelux
Southern EU
Central/Eastern EU
```

The exact final stratification should be driven by data volume and model identifiability.

---

# 10. Record linkage before population estimation

Population estimation is only as good as entity resolution.

The database should retain all original identifiers.

Useful linkage fields:

- legal manufacturer;
- brand;
- exact trade name;
- normalized trade name;
- article number;
- manufacturer product number;
- GTIN/EAN;
- SDS filename;
- SDS revision date;
- SDS product identifier;
- UFI;
- licence number;
- authorization number;
- FDES/commercial reference;
- source-native record ID.

A probabilistic / evidence-based linkage system is preferable to one aggressive deduplication rule.

Store:

```text
link_type
link_confidence
link_evidence
```

Examples:

```text
same_gtin                  very high
same_manufacturer_article  very high
same_ufi                   very high evidence of composition identity
same_sds_document          high
same_manufacturer_name     medium/high
fuzzy_name_only            low
```

---

# 11. UFI: use carefully

The **Unique Formula Identifier (UFI)** is particularly valuable for hazardous mixtures.

Where present:

```text
same UFI
```

is strong evidence that two commercial records refer to the same mixture/formulation composition.

However:

```text
different UFI
```

must not automatically imply a different formulation.

Commercial/regulatory structures can generate multiple UFIs for products that are chemically equivalent or near-equivalent.

Likewise:

- many non-hazardous paints will not have a UFI;
- historic products may predate UFI implementation;
- products may be marketed differently across countries.

Therefore use UFI as a **strong positive linkage feature**, not a universal primary key.

---

# 12. Independent estimator: manufacturer census × observed assortment

Capture-recapture should not be the only estimator.

The project should build a second route.

## Step 1 — manufacturer census

Construct the best possible census from:

- CEPE;
- national paint/coatings associations;
- KemiDigi companies;
- BASTA companies;
- WINGIS manufacturers;
- INIES declarants;
- retailer brand/manufacturer lists;
- ECAT licence holders;
- Nordic Swan licence holders.

Link legal entities and brands.

Then estimate unseen manufacturers, if necessary, using overlap between independent manufacturer lists.

Manufacturer-level linkage is much easier than product-level linkage.

---

## Step 2 — stratified manufacturer sample

Instead of assuming:

```text
25–150 products/manufacturer
```

measure it.

Sample manufacturers by strata such as:

```text
large / medium / small
×
decorative / industrial / marine / mixed
×
region
```

For each sampled manufacturer:

1. enumerate its current EU catalogue;
2. retain article/SKU records;
3. collect SDS/TDS where possible;
4. collapse to base formulations using explicit evidence;
5. count:
   - native products/SKUs;
   - product families;
   - distinct SDS identities;
   - inferred formulations.

This produces an empirical distribution of formulations/manufacturer.

---

## Step 3 — weighted estimator

Use:

```text
estimated manufacturers in stratum
×
observed mean/median formulation count in stratum
```

with uncertainty from both components.

This becomes an independent validation of the MSE estimate.

Agreement between the two methods would be much more persuasive than agreement among several assumption-driven magnitude benchmarks.

---

# 13. Do not use market-volume data as the main product-count estimator

Eurostat / Comext / PRODCOM volume and value statistics are valuable for:

- economic context;
- relative importance of subcategories;
- stratification weights;
- reasonableness checks.

They are poor direct estimators of product count because:

```text
tonnes per formulation
```

varies enormously between:

- mass-market wall paint;
- industrial coatings;
- specialist marine products;
- niche protective coatings.

Therefore:

```text
market tonnes ÷ assumed tonnes/product
```

should remain only a sensitivity benchmark.

---

# 14. Separate two estimands

The project should distinguish clearly between:

## A. Market size

```text
N = number of distinct base formulations under 3208/3209
```

and:

## B. Lead prevalence

```text
p = proportion of those formulations containing relevant lead
```

These require different sampling logic.

---

# 15. Lead-prevalence sampling

Do not sample only from a single pooled registry.

Construct deliberately different source strata.

### Lower-hazard / environmentally selected

- ECAT
- Nordic Swan
- M1

### Broad construction/commercial middle

- BASTA
- INIES
- eBVD
- ordinary retailers
- manufacturer catalogues

### Hazard/professional tail

- KemiDigi
- WINGIS / GefKomm-Bau
- Quick-FDS
- manufacturer SDS libraries

### High-interest niche

- ECHA PT21
- marine chandlers
- anticorrosive coatings
- specialist primers

Oversampling the hazard/professional tail is desirable for **finding lead-containing products**.

But prevalence estimates must be reweighted back to estimated market-stratum sizes.

---

# 16. Formulation collapse must be empirical

The current broad shade/pack compression assumption should eventually be replaced by measurements.

Useful empirical questions:

1. How many GTIN/EAN SKUs map to one SDS?
2. How many article numbers map to one SDS?
3. How many colour variants share one SDS?
4. How many pack sizes share one article family?
5. How many commercial references in INIES map to one declaration/formulation?
6. How often does one UFI occur under multiple trade names?
7. How often does one trade name have multiple distinct UFIs/SDS formulations?

For each source where both SKU and formulation-like identifiers exist, compute actual compression distributions.

Then estimate:

```text
SKU → commercial product → base formulation
```

from data instead of assuming a fixed 1–10 factor.

---

# 17. Suggested source-dependency groups

For capture-recapture modelling, do not automatically count every database as an independent list.

Potential dependency groups:

### Environmental-certification family

```text
ECAT
Nordic Swan
M1
```

### Swedish construction-data family

```text
BASTA
eBVD
possibly related Swedish building databases
```

### SDS ecosystem

```text
WINGIS / GefKomm-Bau
Quick-FDS
manufacturer SDS portals
```

### Chemical-notification family

```text
KemiDigi
other national chemical product registers
PCN-related systems
```

Model dependencies explicitly or choose one representative list from tightly coupled systems.

---

# 18. Recommended immediate implementation/probe order

## Phase 1 — high-value reconnaissance

### 1. KemiDigi

Deliver:

```text
enumeration mechanism
paint/coating filters
in-scope record count
100-row sample
identifier completeness
SDS completeness
```

### 2. BASTA

Deliver:

```text
paint/coating taxonomy
paint article count
manufacturer count
100-row sample
article-number completeness
API/export feasibility
```

### 3. WINGIS / GefKomm-Bau

Deliver:

```text
enumerability assessment
product-count estimate
manufacturer list
article-number fields
SDS retrieval path
```

### 4. INIES

Deliver:

```text
paint/decor FDES count
commercial references per FDES
total commercial-reference count
manufacturer/reference sample
```

### 5. eBVD

Deliver:

```text
API access result
relevant category count
100-row sample
dependency mapping to BASTA
```

### 6. Quick-FDS

Deliver:

```text
supplier enumeration
paint-product enumeration feasibility
stable identifiers
SDS accessibility
```

### 7. ECHA PT21

Deliver:

```text
complete structured export
distinct trade-name count
authorisation-holder count
cross-country dedup analysis
```

---

# 19. Standard probe output per source

Every registry probe should produce the same machine-readable summary.

Suggested fields:

```text
source_id
source_name
source_url
country_scope
market_scope
selection_mechanism
access_method
public_access
bulk_export
api
enumerable
terms_status
robots_status
record_count_total
record_count_in_scope
category_filter
manufacturer_field
brand_field
trade_name_field
article_number_field
gtin_field
ufi_field
sds_field
tds_field
source_record_id_field
licence_or_authorisation_field
hs_code_field
sample_size
identity_completeness
sds_completeness
retrieval_date
notes
```

Also record source dependency:

```text
independence_group
known_data_exchange_with
```

This is important for later MSE modelling.

---

# 20. Recommended identity completeness metric

For every source calculate at least:

```text
manufacturer present %
trade name present %
native source ID present %
article/product number present %
GTIN/EAN present %
UFI present %
SDS reachable %
TDS reachable %
```

And two operational measures:

### Product-level identifiable

```text
manufacturer
+
(trade name OR article number OR GTIN)
```

### Strong cross-source identifiable

At least one of:

```text
GTIN/EAN
manufacturer article number
UFI
SDS identity
regulatory authorization/licence number
```

---

# 21. Proposed first overlap matrix

Once KemiDigi, BASTA and WINGIS are staged, construct:

```text
ECAT
Nordic Swan
KemiDigi
BASTA
WINGIS
INIES commercial references
```

Do not initially include every available list.

A six-list model is already complex.

Produce:

1. raw record counts;
2. exact-identifier overlaps;
3. high-confidence fuzzy-link overlaps;
4. manufacturer-level overlaps;
5. formulation-level overlaps;
6. source dependency diagnostics;
7. capture-pattern table.

Example:

```text
capture_pattern   count
100000            ...
010000            ...
001000            ...
110000            ...
101000            ...
111000            ...
...
```

This becomes the input to MSE.

---

# 22. Geographic issue

A Finnish or Swedish national database cannot simply be multiplied by:

```text
EU population / national population
```

without strong assumptions.

National markets differ in:

- domestic manufacturers;
- climate;
- building systems;
- language/branding;
- retailer structure;
- industrial mix;
- environmental regulation;
- market concentration.

Use national registers principally for:

- product discovery;
- list-overlap estimation;
- manufacturer coverage;
- assortment distribution;
- stratum calibration.

If national scaling is used, model it as a sensitivity analysis, not the primary estimator.

---

# 23. Product availability and "on the EU market"

Define the temporal population explicitly.

Recommended definition:

> A product/formulation is considered on the EU market if there is evidence that it was commercially offered, notified, authorised, registered, certified or documented for sale/use in at least one EU Member State during the study reference period.

Record:

```text
first_seen
last_seen
source_valid_from
source_valid_to
sds_revision_date
declaration_valid_to
authorisation_status
```

Avoid mixing long-discontinued products with current-market products.

---

# 24. Suggested reference period

Choose one explicit study window, e.g.:

```text
2024–2026 current-market evidence
```

Then classify records:

```text
current
recent/historic
unknown
```

Do not silently mix historical SDS archives with present-market products.

---

# 25. Source table for project integration

| ID proposal | Source | Main selection mechanism | Product-level? | Strong identifier potential | SDS potential | Priority |
|---|---|---|---:|---:|---:|---:|
| AS-KD | KemiDigi | hazardous chemical notification | yes | high | medium/high | A+ |
| PE-WG | WINGIS/GefKomm | occupational/SDS construction chemistry | yes | high | very high | A+ |
| AS-BA | BASTA | construction-product declaration | yes | high | medium | A+ |
| AS-IN | INIES commercial references | construction EPD/FDES | yes after expansion | medium/high | low/medium | A |
| AS-EB | eBVD | building-product declaration | yes | medium/high | medium | A− |
| PE-QF | Quick-FDS | supplier SDS distribution | yes | medium | very high | A− |
| LG/BP-21 | ECHA PT21 | regulatory authorisation | yes | very high | regulatory docs | B+ |
| AS-EC | ECAT | ecolabel | yes | high | low/medium | existing |
| AS-NS | Nordic Swan | ecolabel | yes | medium/high | low/medium | existing |
| AS-M1 | M1 | low-emission certification | yes | medium | low/medium | B |
| AS-EPD | IBU/Environdec/etc. | environmental declaration | family/product | medium | low | B/C |
| LG-SG | Safety Gate | enforcement | yes | medium/high | low | auxiliary |
| CS-BTI | EBTI/BTI | customs classification | yes/case | high | none | auxiliary |

---

# 26. Decision points for the next project unit

The next unit should answer:

### Source feasibility

- Can KemiDigi be exhaustively enumerated?
- How many BASTA articles are actually paint/coating products?
- Can WINGIS be enumerated beyond interactive search?
- How many INIES commercial references sit behind the paint/decor FDES category?
- Does eBVD offer practical API access under the project's free/public constraint?
- Is Quick-FDS suitable for systematic enumeration or only SDS discovery?

### Identity

- Which sources expose:
  - article number?
  - GTIN?
  - UFI?
  - native product ID?
  - SDS?

### Population methodology

- Are at least three large lists sufficiently different and sufficiently linkable to support a first MSE experiment?
- Can manufacturer-list overlap estimate the number of unseen manufacturers?
- Can observed manufacturer assortments replace the present assumed products/manufacturer range?
- Can actual SKU→formulation compression be measured?

---

# 27. Recommended change in project emphasis

The project currently has enough evidence to say that the EU paint-product universe is large and cannot be enumerated from one official source.

The most valuable next step is **not another broad magnitude benchmark**.

It is to obtain:

```text
large product list A
large product list B
large product list C
+
cross-source identity
+
overlap counts
```

The project then moves from:

> several independent guesses about the denominator

to:

> a statistical estimate derived from observed product populations and their overlap.

That is a major methodological improvement.

---

# 28. Immediate practical recommendation

Create a new source-expansion unit focused on:

```text
KemiDigi
BASTA
WINGIS
INIES commercial references
```

with the exit criterion:

> At least three new sources have either a complete in-scope export or a reproducible enumerated sample/count, and at least two permit high-confidence product matching against another source.

Then execute the first overlap study.

After that, decide whether full MSE is identifiable or whether the manufacturer-census estimator should remain the principal denominator method.

---

# 29. URLs collected in one place

## Project

- https://github.com/fsncps/lead_HS

## Existing core sources

- EU Ecolabel:  
  https://environment.ec.europa.eu/topics/circular-economy/eu-ecolabel-home_en
- Nordic Swan:  
  https://www.nordic-swan-ecolabel.org/
- Nordic Swan product search:  
  https://www.nordic-swan-ecolabel.org/product-search/

## New high-priority sources

- KemiDigi:  
  https://www.kemidigi.fi/
- Tukes chemicals:  
  https://tukes.fi/en/chemicals
- Finnish Chemical Products Register description:  
  https://www.suomi.fi/services/webpage/the-chemical-products-register-finnish-safety-and-chemicals-agency-tukes/e65f9c7e-87b4-4b1f-8f5b-8711eb3792cb
- WINGIS:  
  https://www.wingisonline.de/
- BG BAU GefKomm-Bau:  
  https://www.bgbau.de/themen/sicherheit-und-gesundheit/gefahrstoffe/gisbau/gefkomm-bau
- BASTA:  
  https://www.bastaonline.se/
- BASTA English:  
  https://www.bastaonline.se/en
- INIES:  
  https://www.inies.fr/
- INIES public database:  
  https://base-inies.fr/
- INIES webservice:  
  https://www.inies.fr/le-webservice/
- eBVD:  
  https://www.ebvd.org/
- eBVD API:  
  https://www.ebvd.org/en/about-ebvd/api/
- Quick-FDS:  
  https://www.quickfds.com/
- ECHA Biocidal Products:  
  https://echa.europa.eu/information-on-chemicals/biocidal-products

## Supplementary sources

- M1 emission classification:  
  https://ymparisto.rakennustieto.fi/en/m1-emission-classification-of-building-materials
- IBU:  
  https://ibu-epd.com/
- International EPD System:  
  https://www.environdec.com/
- ECO Platform:  
  https://www.eco-platform.org/
- baubook:  
  https://www.baubook.info/
- DGNB Navigator:  
  https://navigator.dgnb.de/
- EU Safety Gate:  
  https://ec.europa.eu/safety-gate-alerts/screen/webReport
- EU Binding Tariff Information / EBTI:  
  https://ec.europa.eu/taxation_customs/dds2/ebti/ebti_home.jsp

---

# 30. Bottom line

The most promising route is now:

```text
ECAT
    +
KemiDigi
    +
WINGIS
    +
BASTA
    +
INIES commercial references
    +
selected regulatory / SDS sources
```

These lists represent materially different parts of the paint market.

Use them first to create a linked product/formulation universe.

Then estimate the missing part using:

```text
multiple-list capture-recapture / MSE
```

and independently validate it using:

```text
manufacturer census
×
measured formulations per manufacturer
```

This approach should provide a substantially more defensible answer to:

> **How many distinct paint formulations under HS 3208/3209 are actually on the EU market?**

than further multiplication of national register counts or assumed products-per-producer constants.

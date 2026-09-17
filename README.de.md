---
language: de
translation_of: README.md
source_updated: 2026-09-17
---

Sprachen / Languages / Langues: [EN](README.md) · **DE** · [FR](README.fr.md)

# lead_HS — Blei in Farben auf dem EU-Markt (HS 3208 / 3209)

Eine **dokumentengestützte Studie** zum **EU-Markt** für Farben und
Lacke unter den Zollpositionen **3208** (lösemittelhaltig) und **3209**
(wässrig): wie viele Produkte dort im Verkehr sind, für wie viele
davon sich detaillierte Dokumentation — vor allem
**Sicherheitsdatenblätter (SDB)** — beschaffen lässt, und was diese
Dokumentation über den **Bleigehalt** aussagt.

Die Studie ist im Kontext der schweizerischen
**Cassis-de-Dijon-Ausnahme** für bleihaltige Farben und der zugehörigen
Gesetzgebung und Entscheidungsfindung angesiedelt, denen sie belegte
Marktzahlen beiträgt. Sie arbeitet ausschliesslich mit öffentlich
abrufbaren Dokumenten: **kein Labor, keine physischen Muster, keine
bezahlten Datenquellen.**

> **Kurzfassung / Résumé (DE/FR):**
> [`docs/management_summary.md`](docs/management_summary.md) —
> zweisprachige Management-Zusammenfassung für Entscheidungsträger.

*Die unten verlinkten Methodik- und Quellendokumente sind in einfacher
Sprache für nicht-fachliche Leserschaft geschrieben, jeweils mit
Glossar; Fachbegriffe werden auch bei der ersten Verwendung erklärt.*

## Die Fragen

1. **Wie viele** Farbprodukte gibt es auf dem EU-Markt unter HS
   3208/3209? Zollstatistiken zählen Tonnen und Euro, ein
   Produktregister existiert nicht — die Studie zählt daher
   **Basisrezepturen** (eine Rezeptur, egal wie viele Farbtöne oder
   Gebindegrössen daraus verkauft werden) und bestimmt die Marktgrösse
   aus mehreren unabhängigen amtlichen Quellen.
2. **Für wie viele Produkte lässt sich detaillierte Dokumentation
   beschaffen** — SDB und vergleichbare Spezifikationen — und über
   welche Quellen?
3. **Was zeigt diese Dokumentation über Blei** — als Farbpigment,
   Rostschutz oder Trockenstoff — an einer bedeutenden Stichprobe von
   Produkten?

## Methode

Die Studie geht in drei Schritten vor: Marktgrösse bestimmen,
Dokumentation für eine bedeutende Stichprobe beschaffen, auswerten.

- Produktdokumente werden aus öffentlichen Quellen gesammelt —
  Hersteller- und Händlerseiten, öffentliche Register, amtliche
  Statistiken —; jedes SDB wird gegen ein festes Verzeichnis von
  Bleiverbindungen geprüft.
- Auffällige Befunde werden gegen unabhängige Dokumente zum selben
  Produkt abgeglichen (technische Datenblätter, Etikettentexte,
  ältere SDB-Fassungen). Es gibt kein Labor; die Dokumentation ist die
  Evidenz.
- **Eine Einschränkung steht von Beginn an:** SDB deklarieren
  klassifizierte Bleiverbindungen erst ab 0,1 %, während das
  Schweizer Verbot ab 0,01 % (100 ppm — Teile pro Million)
  Gesamtblei greift. Die Dokumentmethode sieht daher nur *deklariertes*
  Blei, nicht *Gesamtblei*; dieser blinde Fleck wird in jedem
  Ergebniswerk ausgewiesen.

Volle Methodik, in einfacher Sprache mit Glossar:
[Methodik-Dokument](docs/plan/3SM/10_STRATEGY/METHODOLOGY.de.md).

## Regulatorischer Kontext

Das **Cassis-de-Dijon-Prinzip** (2010 unilateral von der Schweiz
übernommen, THG Art. 16a): Produkte, die rechtmässig in der EU im
Verkehr sind, dürfen grundsätzlich auch in der Schweiz verkauft
werden. Seine Ausnahmen sind im **VIPaV** (SR 946.513.8) katalogisiert;
der erste Eintrag betrifft **bleihaltige Farben** und hält die
strengere Schweizer Grenze für Importe aufrecht (ChemRRV Anhang 2.8:
verboten ab 0,01 % Gesamtblei). Der Katalog wird alle fünf Jahre
überprüft, zuletzt 2023, unter Führung des SECO.

Die Studie liefert in diesem Kontext belegte Marktzahlen; sie ist eine
Dokumentstudie und bezieht keine Position zur Regelung selbst. Die
Schweiz kommt in der Studie nur als dieser regulatorische Rahmen vor —
untersuchter Markt ist der EU-Markt.

## Aktueller Stand: die Verwaltungs-CSV-Stichprobe (v0.2.4)

Die Einheit v0.2.4 stellt pro grosser Registerdatenbank die
Verwaltungsfrage: **wie sieht eine Produktzeile dort aus** — welche
Datenfelder kommen pro Produkt zurück, welche Identifikator-Spalten
existieren, ist die Kreuzidentifikation einzelner Produkte möglich?
Beantwortet mit echt geladenen Zeilen, wo ein Register welche
publiziert (`leadhs probe download-csv-sample`; echter Lauf
14.09.2026, n=100 pro Register, seed=42 — reproduzierbar) und mit
einer ehrlichen, belegten Begründung, wo nicht. Das Manifest
verschweigt einen Fehlschlag nie.

- **AS-2 — EU Ecolabel (ECAT): geliefert, 100 von 17'013
  unterscheidbaren Produkten** (17'838 In-Scope-Zeilen;
  Export-Header exakt wie in v0.2.3 gestuft re-gepinnt). 12 Felder je
  Artikel; Identifikatoren: Lizenznummer (100%), Unternehmen + USt
  (86%), EAN13/GTIN (17% der Stichprobe). Kreuz-ID: EAN ↔
  Handelskataloge (der v0.3-Aufbaupfad) steht auf echten Spalten.
- **AS-3 — Nordischer Schwan: geliefert, 100 von 2'322
  unterscheidbaren Farbpositionen.** Die begrenzte Suche fand einen
  echten Export — die Such-URL liefert ein Semikolon-CSV unter
  `?format=csv` (9,8 MB; Farbpool 2'424 Zeilen, 53 Lizenzen, 20
  Lizenznehmer). (Der erste Lauf mit «Versuchsstufe, 14
  unterscheidbare» war ein Werkzeugdefekt — ein laxer Scope-Filter
  und ein ECAT-förmiger Dedupe-Schlüssel — korrigiert und aus dem
  archivierten Export neu gerendert, D38.) Der
  Ecolabel-Überlappungs-Pilot ist über Name + Lizenzhalter
  verknüpfbar — der Export trägt sogar EU-Ecolabel-Lizenznummern.
- **ST-1 / ST-3 / ST-6 / ST-7: keine Produktzeilen publiziert** —
  null Netz, jeder Datensatz belegt den strukturellen Grund (PCN nur
  für Behörden; SBS Unternehmensstatistik; dänisches AT nur Aggregate;
  KemI Produktgeheimhaltung). Von den sechs grossen Registern
  publizieren genau zwei überhaupt Produktzeilen; nur ECAT hat
  Identifikator-Spalten je Artikel.

Jede Stichprobenzeile trägt volle Provenienz (Quelle, Lauf-Schlüssel,
Abrufdatum, Dokument-Hash, seed, Zieindex). Einheitsbericht:
[report-0.2.4.md](docs/report/report-0.2.4.md) (EN); Manifest und
Stichproben sind veröffentlicht unter
[docs/report/](docs/report/csv-sample.manifest.md) (Arbeitsrenderungen
je Lauf in `data/report/`).

**Addendum — AS-Klassen-Quellenprobe (2026-09-14).** Ein Befund je
AS-Klassen-Quelle, alle 30 (`leadhs probe as-source-probe`):
Produktzeilen-CSV wo erhältlich, sonst exakte oder geschätzte
Datensatzzahl mit Provenienz, sonst Warumnicht + was stattdessen
verfügbar ist. Die beiden Ökolabel-Kataloge wiederverwenden die
csv-sample-Zeilen (AS-2: 100 von 17'013 distinct; AS-3: 100 von
2'322 distinct); Blue Angel (≈70'000, registerseits behauptet, alle
Kategorien) und environdec (≈2'025) bieten nur Seitenzählungen —
seit D38 mit archivierter Landingpage als Beleg; die übrigen fünf
Register (INIES, IBU, NF Env, natureplus, EPD Norway) haben keine
Bulk-Oberfläche — Einzeldokumente hinter Such-UIs, Grund vermerkt.
Die 21 Branchenverbände sind Mitgliederverzeichnisse, keine
Produktregister (18 live, 3 zur Probezeit nicht erreichbar).
Zusammenfassung (D38-korrigierter Re-Publish):
[as-source-probe.summary.20260914-165555.md](docs/report/as-source-probe.summary.20260914-165555.md) (EN).

**Addendum — data_sources.csv (2026-09-14, D38).** Eine kuratierte
Liste der Quellen mit **bestätigten Bulk-Produktdaten** samt
Identitäts-Tupel (Hersteller + Produkt-Identifikator) — zunächst
genau AS-2 und AS-3, die einzigen Quellen, die die Schwelle derzeit
erfüllen. Sie wächst nur, wenn künftige Sondierungen die Schwelle
bestätigen; gesperrte nationale Register und unsondierte Kandidaten
bleiben in
[docs/plan/3SM/10_STRATEGY/DATA_SOURCE.md](docs/plan/3SM/10_STRATEGY/DATA_SOURCE.md)
dokumentiert.

**Addendum — Komplette Sondierungsrunde + Quellen-Erweiterungsfühler
(2026-09-15, D39).** Die ganze Sondierungssuite lief erneut in einem
Durchgang — Zensus (108 Quellen), frische CSV-Stichprobe, AS-Quellen-
probe — **mit sechs neuen Kandidatenquellen** aus einer Beratungs-
übergabe (Quellen aus AS-Klasse jetzt 36 Zeilen) im Register:
**AS-31 KemiDigi** (finnisches Chemiproduktregister,
Gefahren-Stratum), **AS-32 WINGIS/GefKomm-Bau** (deutsches
Bau-SDS-Ökosystem), **AS-33 BASTA** (schwedischer
Bauartenkatalog, >200'000 Artikel behauptet), **AS-34 eBVD**
(nordische Deklarationen), **AS-35 Quick-FDS** (SDS-Discovery),
**AS-36 ECHA PT21 Antifouling (Marine-Beschichtungen)**. Befunde:
Die beiden Ökolabel-Stichprobenpools reproduzieren sich
deterministisch beim frischen Download (17'013 / 2'322 distinct);
die Zensus-Kennzahl bleibt N2 = 331'644 / Flurboden 17'838; und die
neue Datenpool-Antwort: **keine dritte Bulk-Quelle** — keine der
sechs bietet eine Exportoberfläche (je ≤5 freundliche GETs:
Soft-Landing-HTML / 404er, Zählung nicht sichtbar; ECHA
robots-blockiert, die gehärtete-Host-Klasse). Eine der Quellen zu
bestätigen erfordert ein per-Quelle-Abstecken (Kategorie-Erkundungen,
API-Bedingungen, Vereinbarungen) — Arbeit der nächsten Einheit gemäss
[INPUT-source-expansion-MSE.md](docs/plan/3SM/10_STRATEGY/INPUT-source-expansion-MSE.md)
(EN). Vollabdeckungs-Report-Snapshot:
[probe-report.20260915-000619.3a5fc07d.md](docs/report/probe-report.20260915-000619.3a5fc07d.md)
(EN).

**Addendum — BASTA-Sonderprobe (2026-09-17, D40).** AS-33 bekam eine
nutzerbeauftragte Vertiefung (ein Kategorie-Proxy genügt statt
HS-Codes). Die Kernaussage dreht die D39-Antwort um: **die
«auth-gated API» ist von eigener Web-Client-Seite überbrückt** — der
Client ruft einen gleichursprünglichen anonymen Proxy auf,
`/apiproxy/v3/search/articles` (wörtlich aus dem generierten
OpenAPI-Client des Webangebots abgesteckt). Exakte öffentliche
Zählungen: **195'391 Artikel / 1'925 Unternehmen** (Keyfigures; die
ungefilterte Suche meldet 200'769 — 5'378 mehr als die Keyfigure,
nicht dekomponiert). Eine gesäte 100-Artikel-Stichprobe
([CSV](data/report/basta-probe.20260917-183244.AS-33.csv), Seed 42)
wurde über einen Zufalls-Seiten-Satz von 20'000 Zeilen gezogen: 41
Hersteller, 45 BK04-Baugruppen, Identitätstupel
(Hersteller + Artikelnummer + interne ID) 100 % vollständig, GTIN
69,8 %. Strukturbefund: die suche paginiert herstellerzeitgeklustert
(eine Seite ≈ ein Unternehmen) — Einzel-Seiten-Stichproben sind
nicht repräsentativ; der Lauf poolt ehrlich über zufällige
Positionen. Der Farbananteil von BASTA ist klein: die
Farb-BK04-Gruppen (03402 Fasadfärg utomhus / 03404 Vägg- och
takfärg inomhus) tragen 2 von 100 gestichprobeten Artikeln. Das
`data_sources.csv`-Gate (bestätigt Bulk + Identität +
In-Scope-Filter) ist **nicht** erfüllt — bis ein serverseitiger
Farbfilter abgesteckt ist, keine dritte Zeile; Details im
[report-0.2.4.md](docs/report/report-0.2.4.md) (D40-Addendum, EN).

## Frühere Einheiten

### v0.2.3 — Pool-Schätzung v2: Meta-Benchmark-Abstimmung (14.09.2026)

Die Einheit v0.2.3 ersetzt die Ein-Modell-Überschrift von v0.2.2 durch
eine **Meta-Benchmark-Abstimmung**: sieben unabhängige Benchmark-Grössen
schätzen den EU-Farben-Pool; jede stimmt in eine von fünf aneinander-
anschliessenden Grössenklassen (a 20k–50k … e >300k), und eine fest
gepinnte Regel wandelt die Abstimmung in ein **doppelstufiges Urteil**
um — SKU-Stufe (Register-/Produktzählung) und Formulierungs-Stufe
(schatten-/gebindekollabiert). Vertrauen wird nur erklärt, wenn ≥3
verfügbare Benchmarks ohne ausschliesslich nicht-angrenzenden Konflikt
konvergieren; Gleichstände liefern eine Spanne samt Kipp-Annahmen; die
Abstimmung ist in jedem Fall vollständig sichtbar.

- **SKU-Stufe: Klasse e (>300k Produkte)** — Vertrauen nicht erklärt
  (drei Benchmarks liegen in nicht-angrenzenden Klassen; als offene
  Punkte vermerkt).
- **Formulierungs-Stufe: Klasse c (100k–200k)** — Vertrauen nicht
  erklärt; die Stufen-Umsetzung reitet auf einer gepinnten 1–10
  Schattenkollaps-Spanne, als Annahme gekennzeichnet (die messbare
  ECAT-Schlüssel-Deduplizierung ist klein: Name ×1,049, EAN ×1,266).
- Neue Primärquellen-Extraktionen füttern die Benchmarks:
  schwedische Giftzentren-Meldungen Farben/Lacke 71'231 (2022);
  PCN-Dossiers 1'444'290 (2021, SWD(2022) 435 Anhang 16 — keine
  Farbanteil-Konstante existiert); JRC-Abschlussbericht Ecolabel
  (2026): 36'960 zertifizierte Produkte (03/2025) und die amtliche
  Bestätigung, dass **keine Marktanteil-Daten existieren**; dänisches
  Produktregistret ≈40'000 gefährliche Produkte (nur Aggregate —
  kein Adapter möglich); Eurostat-SBS-Verifikation: 3'300
  Unternehmen (NACE C2030, 2020).
- Der Trichter-Abschnitt des publizierten Berichts trägt jetzt ein
  Überholt-Banner; sein v0.2.2-Inhalt bleibt in der
  Veröffentlichungshistorie erhalten.
- Der volle Sondierungslauf vom 14.09.2026 (Wellen 1–3) reproduzierte
  jede Kernzahl (ECAT 17'838 exakt abgeglichen; Comext 6'316 Zeilen;
  identische blockiert/fehlerhaft-Sets) — Befunde, Lücken und Wege im
  Begleitdokument
  [benchmarking-0.2.3.md](docs/report/benchmarking-0.2.3.md) (EN).

Details: [report-0.2.3.md](docs/report/report-0.2.3.md) (EN);
maschinenlesbare Tabellen (Benchmark-Abstimmung, Urteile, alle
bisherigen Abschnitte) im
[Sondierungsbericht](docs/report/probe-report.md).

### v0.2.2 — der Drei-Fragen-Trichter (14.09.2026)

Die Einheit v0.2.2 hat die **Landschaftsläufe im echten Netz**
ausgeführt (14.09.2026; nur Erkundung — amtliche Exporte/APIs, kein
Scraping) und den **Drei-Fragen-Trichter** zusammengestellt — jede
Zahl ein Datenbank-Abfrageergebnis:

- **F1 — wie viele Farben auf dem EU-Markt (modellierte Schätzung):**
  das Poolmodell `P(cn8) = M × ppp × s(cn8)` liefert **[85'840–343'360]
  Produkte** — Hersteller-Grenzen 800 (CEPE) bis 3'200 (Eurostat SBS
  NACE 20.30) × **107,3 Produkte je Hersteller** (ECAT: Paare ÷
  Lizenznehmer) × mengengewichte der gestützten Ausseneinfuhr je
  CN8-Code. Eine modellierte Schätzung, nie eine Zählung.
  **Überholt seit 14.09.2026 durch die v0.2.3-Benchmark-Abstimmung
  (oben); bleibt in der Veröffentlichungshistorie erhalten.**
- **F2 — für wie viele Produkte das Identitäts-Tripel definitiv
  bekannt ist (Untergrenze):** **17'170** unterscheidbare
  (Hersteller, Produkt-Ident)-Paare über die gestützten amtlichen
  Register (ECAT: 17'838 Einträge, 160 Lizenznehmer, 16,0 %
  Identitätsvollständigkeit).
- **F3 — für wie viele davon ein SDB-artiges Dokument erreichbar ist
  (modelliert):** **3'590** (Obergrenze; die Trefferquoten-Annahme
  steht noch aus). Das v0.5-Verhältnis (F2 ÷ F1) liegt bei
  **0,05–0,2**.

Das 101 Zeilen umfassende Quellenregister ist vollständig
dispositioniert: **36 gezählt, 48 manuell dokumentiert, 4 blockiert,
13 inaktiv per Design**; die Comext-Unterlage deckt **alle 13
CN8-Codes** ab (6'316 Handelszeilen). Der ECAT ∩ Nordic-Swan-
Überlappungspilot bleibt ausdrücklich unbestimmbar, bis ein zweites
Register gestützt ist. Einheitsbericht:
[report-0.2.2.md](docs/report/report-0.2.2.md); maschinenlesbare
Tabellen (CN8-Handel, Identität, Tiefenmatrix, Kapitel,
Abstimmungskennzeichen) im
[Sondierungsbericht](docs/report/probe-report.md).

### v0.2.1 — Quellenfähigkeit sondiert (14.09.2026)

Eine Ebene tiefer bei den **amtlichen Registern** (EU Ecolabel, Nordic
Swan, Blauer Engel, INIES, IBU, environdec), jede charakterisiert
gegen das Produktmodell (CN8, Hersteller, Produkt-Ident) nach Umfang
und Tiefe. **ECAT als real-Produktquelle bestätigt** (Hersteller +
GTIN/EAN, CN8 über Kategorie, Tiefe 2, herunterladbares CSV);
vorläufiger N2-Zähler **17.838** zertifizierte Farbprodukte — eine
Untergrenze, nie eine Marktzahl. Die übrigen Register blieben
Export-zu-verankern / inaktiv / ohne Produkt-Ident; der
HTML-als-CSV-Defekt dieser Runde wurde in v0.2.2 behoben. Details:
[report-0.2.1.md](docs/report/report-0.2.1.md).

### v0.2.0 — Datenlandschaft-Karte (12.09.2026)

Nur-Erkundung-Sondierung der registrierten Quellen (amtliche
Statistiken, ein Branchen- und Industrieverband sowie 25
Farben-/Beschichtungs-/Heimwerker-/Künstlerfarben-Seiten). Leitgrössen:
**N1** Markt-Anker (2024, EU-Ausseneinfuhren: HS 3208 ≈2,5 Mio. t /
≈12,2 Mrd. €, HS 3209 ≈2,1 Mio. t / ≈6,2 Mrd. €; CEPE ≈800 Mitglieder;
SBS NACE 20.30 = 3.200 Unternehmen); **N2 = 204.693** per Sitemap
sichtbare Produkt-URLs über 23 gezählte Quellen; **N3 = 9** Webseiten
mit sichtbarer SDB-Bibliothek; die nordischen Register blieben offen
(SPIN nicht erreichbar). Details:
[report-0.2.0.md](docs/report/report-0.2.0.md).

## Was frühere Recherchen zeigen

| Bleiverwendung | Dokumentierter Status auf dem EU-Markt |
|---|---|
| Bleichromat-Pigmente | keine rechtmässige Versorgung seit 17. März 2022 (letzte Zulassungen verweigert) |
| Bleimennige-Grundierungen | dokumentierte Nischenpräsenz (Schifffahrtsanbieter in DE; SE nur für Fachbetriebe) |
| Blei-Trockenstoffe in Alkydfarben | unbekannt — die zentrale offene Frage der Erhebung |
| Künstlerölfarben mit Bleiweiss | dokumentiert (NL, IT) — Zollposition 3213 |

Details und Quellen:
[LEAD_SDS.md](docs/plan/3SM/10_STRATEGY/LEAD_SDS.md) (EN).

## Das Werkzeug

Datensammlung und Nachvollziehbarkeit laufen über **`leadhs`**, ein
kleines Kommandozeilenprogramm — kein Server, eine Maschine, eine
lokale SQLite-Datenbank. Jedes abgerufene Dokument wird unverändert
archiviert, mit Quelle, Abrufdatum und Inhalts-Hash; jede Zahl in
einem Bericht ist auf einen konkreten Lauf und ein konkretes Dokument
zurückführbar. Das Werkzeug erfasst ausschliesslich Produktdaten.

- In diesem Repository: `make setup` (Installation, Datenbank-
  Migration, Quellenregister laden, Umgebungs-Vorprüfung) und
  `make help` (Verzeichnis aller Befehle).
- Ausserhalb des Repositories: Wheel bauen (`uv build`) und mit einem
  verwalteten Interpreter installieren
  (`uv tool install dist/leadhs-*.whl`), stets mit explizitem
  Datenverzeichnis (`leadhs --data-dir ~/leadhs-data …`). Dieser Weg
  ist build-verifiziert; veröffentlichte Release-Artefakte stehen
  noch aus. Ein Installer für nacktes Windows (ohne make, ohne
  vorinstalliertes Python) ist ein erklärtes Ziel für v0.3.
- Vorgänge, die echte Sites berühren, sind hinter einem expliziten
  `GO=1` abgesichert.

Details: [Architektur](docs/plan/3SM/10_STRATEGY/ARCHITECTURE.md) und
[Datenmodell](docs/plan/3SM/10_STRATEGY/DATA_MODEL.md) (je EN); das
begutachtete technische Design in
[20_DESIGN/](docs/plan/3SM/20_DESIGN/) (EN).

## Fahrplan

| Phase | Inhalt |
|---|---|
| 0 — aktuell | Datenlandschaft kartieren; die drei Leitgrössen N1/N2/N3; Fähigkeit der amtlichen Register sondieren |
| 1 | Pilot: Blei-Verzeichnis einfrieren; SDB-Sammlung und -Auswertung an einer ersten Stichprobe |
| 2 | Auswahlrahmen und Stichprobe; Dokumentensammlung im vollen Umfang; Künstlerfarben-Anhang (3213), nach verfügbarer Kapazität |
| 3 | Dokumentenübergreifender Abgleich und Qualitätssicherung |
| 4 | Auswertung; Diskussionsgrundlage; Einfrieren der Datenbank |

## Wo Sie mehr lesen

| Dokument | Inhalt |
|---|---|
| [`management_summary.md`](docs/management_summary.md) | zweisprachige (DE/FR) Zusammenfassung für Entscheidungsträger |
| [`METHODOLOGY.de.md`](docs/plan/3SM/10_STRATEGY/METHODOLOGY.de.md) | wie der Markt gemessen wird — einfache Sprache, mit Glossar |
| [`DATA_SOURCE.de.md`](docs/plan/3SM/10_STRATEGY/DATA_SOURCE.de.md) | jede Quelle und die Zugriffsregeln — einfache Sprache, mit Glossar |
| [`ARCHITECTURE.md`](docs/plan/3SM/10_STRATEGY/ARCHITECTURE.md) (EN) | das Sammelwerkzeug und das Reporting-Konzept (halbtechnisch) |
| [`DATA_MODEL.md`](docs/plan/3SM/10_STRATEGY/DATA_MODEL.md) (EN) | die Evidenzdatenbank (technisch) |
| [`LEAD_SDS.md`](docs/plan/3SM/10_STRATEGY/LEAD_SDS.md) (EN) | Bleiverbindungen, EU-Recht, was Datenblätter verraten — und was nicht (halbtechnisch) |
| [`10_STRATEGY/MASTER.md`](docs/plan/3SM/10_STRATEGY/MASTER.md) (EN) | Strategieentscheide, offene Fragen, Fahrplan |
| [`20_DESIGN/`](docs/plan/3SM/20_DESIGN/) (EN) | technisches Design von Werkzeug + Datenbank |
| [`30_IMPLEMENTATION/`](docs/plan/3SM/30_IMPLEMENTATION/) (EN) | Bauphasen-Pläne der Baueinheiten (v0.1.1–v0.1.3, v0.2.0–v0.2.4 gebaut) — Phasenverfolgung, Abnahme-Gates |
| [`charts/`](docs/plan/3SM/10_STRATEGY/charts/) (EN) | die Diagramme mit ihren Quellen (referenziert aus den Detaildokumenten) |
| [`3SM-README`](docs/plan/3SM/README.md) (EN) | einfachsprachige Anleitung zum Planungsbaum |

## Repository-Struktur

    README.md                  diese Datei (EN)
    README.de.md               deutsche Fassung
    README.fr.md               französische Fassung
    AGENTS.md                  Konventionen für KI-gestützte Arbeit an diesem Repo (EN)
    Makefile                   Operator-Einstiegspunkt («make help» = Verzeichnis)
    pyproject.toml             Python-Paketierung des leadhs-Werkzeugs
    src/leadhs/                Quellcode des Werkzeugs (v0.1.1 Sondierung, v0.1.2 Operator-Schicht, v0.1.3 Lauf-Zähler)
    tests/                     automatisierte Offline-Testsuite
    data/                      lokaler Arbeitszustand (gitignored): Datenbank, Raw-Speicher, Berichts-Zwischenstände
    docs/report/               publizierte Berichts-Finalfassungen (bewusst committet)
    docs/management_summary.md zweisprachige Management-Zusammenfassung (DE/FR), stets aktuell
    docs/plan/3SM/             Planungsnotizen (3-Stufen-System, EN)
    ├── README.md              einfachsprachige Anleitung zum Planungsbaum (EN)
    ├── MASTER.md, LOG.md      Projekt-Dashboard, Lifecycle-Log (EN)
    ├── 10_STRATEGY/           Recherchebefunde und Entscheide (was & warum)
    │   ├── METHODOLOGY.de.md  Methodik, deutsch
    │   ├── DATA_SOURCE.de.md  Datenquellen, deutsch
    │   └── charts/            gerenderte Diagramme (referenziert aus den Detaildokumenten, EN)
    ├── 20_DESIGN/             technisches Design (wie genau, EN)
    └── _archive/              überholtes Material

## Status

Die Werkzeug-Einheiten v0.1.1–v0.2.4 sind gebaut und getestet (364
automatisierte Offline-Tests): Evidenzdatenbank, Quellenregister,
Quellensondierung, Feasibility-Berichte je Quelle, Zähl-Maschinerie für
Katalogdurchläufe (wartet auf eine Sammel-Freigabe), die
Datenlandschaft-Karte mit den drei Leitgrössen, die
Quellenfähigkeits-Sondierung der amtlichen Register, der
Drei-Fragen-Trichter im echten Netz (14.09.2026) sowie die
Pool-Schätzung v2 — die Meta-Benchmark-Abstimmung mit doppelstufigem
Grössenklassen-Urteil (14.09.2026): Benchmark-Maschine,
Adapter-Paket, vier neue Primärextraktionen, Berichtsabschnitt mit
Überholt-Banner — jede Zahl ein Abfrageergebnis oder eine datierte
Extraktion — und die Verwaltungs-CSV-Stichprobe mit Produktzeilen-
Evidenz je Register (14.09.2026). Der Bericht ist unter `docs/report/`
veröffentlicht. Die
Methodik bleibt offen für Revision, während Ergebnisse eintreffen.

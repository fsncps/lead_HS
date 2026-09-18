---
language: de
translation_of: README.md
source_updated: 2026-09-18
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
[Methodik-Dokument](docs/study/METHODOLOGY.de.md).

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

## Aktueller Stand (Einheit v0.2.4)

Die Einheit v0.2.4 beantwortet die Verwaltungsfrage pro grossem
Register: **wie sieht eine Produktzeile dort aus** — welche Felder,
welche Identifikator-Spalten, ist Kreuzidentifikation möglich? — mit
echten geladenen Zeilen, wo ein Register welche publiziert (gesät,
reproduzierbar, n=100 je Register), und mit belegtem strukturellem
Grund, wo nicht. Von den sechs grossen Registern publizieren genau
zwei Produktzeilen überhaupt; nur EU-Ecolabel ECAT hat
Identifikator-Spalten je Artikel
([report-0.2.4.md](docs/report/report-0.2.4.md) (EN)):

- **AS-2 — EU Ecolabel (ECAT): 100 von 17'013 unterscheidbaren
  Produkten** — Lizenznummer 100 %, Unternehmen + USt 86 %,
  EAN13/GTIN 17 % der Stichprobe; EAN ↔ Handelskataloge (der
  v0.3-Aufbaupfad) steht auf echten Spalten.
- **AS-3 — Nordischer Schwan: 100 von 2'322 unterscheidbaren
  Farbpositionen** — echter Export unter `?format=csv` (2'424
  Farbzeilen, 53 Lizenzen), mit EU-Ecolabel-Lizenznummern.
- **ST-1/3/6/7 — keine Produktzeilen publiziert** (PCN nur für
  Behörden; SBS; dänisches AT; KemI-Geheimhaltung) — jeder Grund
  belegt.

Die kuratierte **`data_sources.csv`** listet die Quellen mit
bestätigten Bulk-Produktdaten samt Identitäts-Tupel: heute genau
AS-2 und AS-3. Die komplette Sondierungsrunde (D39, 15.09.2026)
registrierte sechs Berater-Kandidaten und fand **keine dritte
Bulk-Quelle**; die **BASTA-Sonderprobe (D40, 17.09.2026)** drehte das
für AS-33 über die eigene anonyme Web-Client-Route um — exakte
öffentliche Zählungen **195'391 Artikel / 1'925 Unternehmen** und
eine gesäte 100-Artikel-Stichprobe (Identitätstupel 100 %, GTIN
69,8 %; nur 2/100 in den Farbgruppen) — aber der serverseitige
Farbfilter bleibt ungesteckt, also noch keine dritte `data_sources
.csv`-Zeile. Details: [report-0.2.4.md](docs/report/report-0.2.4.md)
(D37–D40-Addenda, EN) und
[Datenquellenregister](docs/study/DATA_SOURCE.md).

## Frühere Einheiten

### v0.2.3 — Pool-Schätzung v2: Meta-Benchmark-Abstimmung (14.09.2026)

Sieben unabhängige Benchmark-Grössen schätzen den EU-Farben-Pool; je
eine von fünf Grössenklassen, gepinnte Regel → doppelstufiges
Urteil. Ergebnis: **SKU-Stufe Klasse e (>300k), Formulierungs-Stufe
Klasse c (100k–200k) — Vertrauen in beiden nicht erklärt** (nicht
angrenzende Konflikte als offene Punkte vermerkt). Details:
[report-0.2.3.md](docs/report/report-0.2.3.md) (EN),
[benchmarking-0.2.3.md](docs/report/benchmarking-0.2.3.md) (EN).

### v0.2.2 — der Drei-Fragen-Trichter (14.09.2026)

Der Landschaftslauf im echten Netz (nur Erkundung): F1 Poolmodell
**[85'840–343'360]** (überholt durch die v0.2.3-Abstimmung; bleibt
in der Veröffentlichungshistorie), F2 Identitätsuntergrenze
**17'170** distinct (Hersteller, Produkt-Ident)-Paare, F3
SDB-erreichbar **≈3'590** (modelliert). Jede Zahl ein
Datenbank-Abfrageergebnis; Register vollständig dispositioniert.
Details: [report-0.2.2.md](docs/report/report-0.2.2.md) (EN).

### v0.2.1 — Quellenfähigkeit sondiert (14.09.2026)

Die amtlichen Register gegen das Produktmodell charakterisiert:
**ECAT als real-Produktquelle bestätigt** (Hersteller + GTIN/EAN,
CSV-Export), vorläufiger N2-Zähler **17'838** — eine Untergrenze,
nie eine Marktzahl. Details:
[report-0.2.1.md](docs/report/report-0.2.1.md) (EN).

### v0.2.0 — Datenlandschaft-Karte (12.09.2026)

Nur-Erkundung-Sondierung: **N1** Markt-Anker (2024,
EU-Ausseneinfuhren ≈12,2 + 6,2 Mrd. €; ≈3'200 Unternehmen),
**N2 = 204'693** sitemap-sichtbare Produkt-URLs, **N3 = 9** Webseiten
mit sichtbarer SDB-Bibliothek. Details:
[report-0.2.0.md](docs/report/report-0.2.0.md) (EN).

## Was frühere Recherchen zeigen

| Bleiverwendung | Dokumentierter Status auf dem EU-Markt |
|---|---|
| Bleichromat-Pigmente | keine rechtmässige Versorgung seit 17. März 2022 (letzte Zulassungen verweigert) |
| Bleimennige-Grundierungen | dokumentierte Nischenpräsenz (Schifffahrtsanbieter in DE; SE nur für Fachbetriebe) |
| Blei-Trockenstoffe in Alkydfarben | unbekannt — die zentrale offene Frage der Erhebung |
| Künstlerölfarben mit Bleiweiss | dokumentiert (NL, IT) — Zollposition 3213 |

Details und Quellen:
[LEAD_SDS.md](docs/study/LEAD_SDS.md) (EN).

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

Details: [Architektur](docs/study/ARCHITECTURE.md) und
[Datenmodell](docs/study/DATA_MODEL.md) (je EN); das
begutachtete technische Design in
[20_DESIGN/](docs/plan/3SM/20_DESIGN/) (EN).

## Wie die Arbeit vorankam — Rückblick auf v0.1 und v0.2

Die Studie wurde von unten aufgebaut, in kleinen verifizierten
Einheiten — und dieser Prozess formt, was sie heute sagen kann.

**v0.1 (Einheiten v0.1.1–v0.1.3): das Instrument bauen.** Ziel war
nie zuerst Zahlen — sondern ein verlässliches Sammelwerkzeug.
v0.1.1 lieferte ein schlankes Kommandozeilen-Set (Evidenzdatenbank,
Quellenregister, Sondierbefehle); v0.1.2 ummantelte es zur
Operatorschicht (make-Einsprung, `GO=1`-Gates für alles, was echte
Sites berührt) und sondierte alle registrierten Quellen höflich —
Robots/Bedingungen, je Quelle ein Feasibility-Befund; v0.1.3 kartierte
die Datenlandschaft und baute die Zähl-Maschinerie für
Katalogdurchläufe (bewusst stillgelegt bis zur Sammel-Freigabe).
Methode durchgängig: jedes Dokument unverändert archiviert mit Hash
und Abrufdatum; jede Zahl auf einen Lauf zurückführbar; ehrliche
«keine Daten»-Einträge statt stiller Fehlschläge; kein Labor, keine
Bezugsquellen, kein Scraping über ein explizites Go hinaus. Nach v0.1
wusste die Studie, *welche Quellen es gibt und was jede hergibt* —
noch nicht, wie gross der Markt ist.

**v0.2 (Einheiten v0.2.0–v0.2.4): das Instrument auf die Zahlen
richten.** Die Ziele wurden zahlen-zentriert: Marktgrösse (N1),
Zugriffsdeckung (N2), erreichbare Dokumentation (N3). v0.2.0
lieferte die Landschaftskarte auf echten Daten. v0.2.1 sondierte die
amtlichen Register und fand die erste echte Produktquelle (EU
Ecolabel ECAT, mit Hersteller + GTIN/EAN). v0.2.2 führte den
Drei-Fragen-Trichter aus — wie gross der Pool (modelliert), wie
viele Produktidentitäten definitiv bekannt (gezählter Flurboden),
wie viele SDB erreichbar (modelliert). v0.2.3 ersetzte die
Ein-Modell-Schätzung durch eine Meta-Benchmark-Abstimmung unabhängiger
Grössen mit Grössenklassen-Urteilen. v0.2.4 senkte die Frage auf die
Zeilenebene: wie sieht ein Produkt-Datensatz in jedem Register
wirklich aus — und stellte fest, dass nur die beiden Ökolabel-Kataloge
überhaupt Bulk-Produktzeilen publizieren, wobei BASTA über das eigene
anonyme Web-Interface ergänzbar wird, sobald eine strukturelle Frage
geklärt ist.

**Was die Revisionsrunden stetig änderten.** Der Umfang wanderte mit dem
Befund: Schweizer Marktkennzahlen früh gestrichen (untersuchter Markt
ist die EU; die Schweiz ist nur regulatorischer Rahmen), der
«Alles-Durchlaufen»-Plan durch Erst-Erkundungs-Disziplin ersetzt, und
die Lieferung geschärft von einer allgemeinen Datenkarte zu einer
zahlen-zentrierten Antwort für die Akteure um die
Blei-Farb-Ausnahme. Konstant blieben: die Formulierung als Zähleinheit,
Abgleich statt Labor, die erklärte-vs-gesamt-Lücke als Restriktion in
jeder Lieferung, und Provenienz für jede Zahl.

## Geplant: vom Bulk-Download zur einen Produkttabelle (v0.3)

Die nächste Bauphase verwandelt die bestätigten Bulk-Quellen in eine
konsolidierte Produktdatenbank, in zwei Schichten:

**1. Bulk-Download der Quellen (Raw-Schicht).** Jede bestätigte
Bulk-Quelle — EU Ecolabel (≈17'013 distinct), Nordischer Schwan
(≈2'322) und BASTA (195'391 Artikel; über die eigene anonyme
Web-Client-Route angezapft) — wird in eine **Raw-Tabelle je Quelle**
übernommen: wortgetreu, ungefiltert, eine Zeile je
Quellendatensatz, mit Herstellername, Produktkennung und
Gruppencode genau wie von der Quelle geschrieben. Die Downloads
sind wiederholbar (Unterbrechung, Fortsetzen), inkrementell
(Wiederholung prüft nur neue/veränderte Datensätze anhand eines
Change-Journals) und manifest-getrieben (ein kommittiertes
Manifest je Quelle definiert die Tabellenform, bevor Daten
fliessen; übergrosse Datensätze werden in den Raw-Speicher
ausgelagert, nichts geht verloren). Höflichkeit: List-Endpoint
zuerst, Ratenbegrenzung und Backoff, über die bestehende
`GO=1`-gesteuerte CLI (`leadhs raw init <source>` /
`leadhs raw seed <source>`).

**2. Deterministische Normalisierung und Verschmelzung
(Matching-Schicht).** Um dasselbe Produkt aus mehreren Quellen
zusammenzuführen, werden Namen und Identifikatoren deterministisch
normalisiert (keine LLM/Maschine-Lern-Zuordnung — jede Verknüpfung
bleibt erklärbar und reproduzierbar): Unicode-Diaekritik-Faltung,
Case-Folding, Streichen von Rechtsform-Token («Foo-Bar Ltd.» ≙
«Foo Bar Limited» → `foo bar`), Identifier-Aufräumen (Gross-/Nullen,
Präfixe; «ABC-123/B» ≙ «abc00123b» → `ABC123B`). Die Datensätze
werden dann in Stufen verknüpft: zuerst exakte Schlüssel
(GTIN/EAN; normalisierter Identifikator innerhalb desselben
normalisierten Herstellers), dann bewertete Nahvergleiche
(Jaro-Winkler, Token-Set-Ähnlichkeit) — nur innerhalb kleiner
Kandidatenblöcke, damit 200k+ Zeilen handhabbar bleiben. Jede
Kandidatenverknüpfung trägt ein Urteil — `auto_match` / `review`
(humane Warteschlange) / `no_match` — mit Methode und Punktzahl je
Paar; die zusammengeführte Produkt-Sicht bleibt völlig auditerbar,
Korrekturen sind nur anhängend (append-only). Ergebnis: eine
**Hersteller- und eine Produkttabelle** auf der Formulierungseinheit
der Studie, je Produkt mit allen Quellenbeobachtungen und der
Belegstufe je Verknüpfung.

Details: die Strategieakten
[`RAW_SOURCING.md`](docs/plan/3SM/10_STRATEGY/RAW_SOURCING.md) und
[`MATCHING.md`](docs/plan/3SM/10_STRATEGY/MATCHING.md) (die Regeln,
Schwellen und Bibliothekswahl werden dort als Anhänge-Entscheide
R1–R9 und MA1–MA9 verankert).

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
| [`METHODOLOGY.de.md`](docs/study/METHODOLOGY.de.md) | wie der Markt gemessen wird — einfache Sprache, mit Glossar |
| [`DATA_SOURCE.de.md`](docs/study/DATA_SOURCE.de.md) | jede Quelle und die Zugriffsregeln — einfache Sprache, mit Glossar |
| [`ARCHITECTURE.md`](docs/study/ARCHITECTURE.md) (EN) | das Sammelwerkzeug und das Reporting-Konzept (halbtechnisch) |
| [`DATA_MODEL.md`](docs/study/DATA_MODEL.md) (EN) | die Evidenzdatenbank (technisch) |
| [`LEAD_SDS.md`](docs/study/LEAD_SDS.md) (EN) | Bleiverbindungen, EU-Recht, was Datenblätter verraten — und was nicht (halbtechnisch) |
| [`10_STRATEGY/MASTER.md`](docs/plan/3SM/10_STRATEGY/MASTER.md) (EN) | Strategieentscheide, offene Fragen, Fahrplan |
| [`20_DESIGN/`](docs/plan/3SM/20_DESIGN/) (EN) | technisches Design von Werkzeug + Datenbank |
| [`30_IMPLEMENTATION/`](docs/plan/3SM/30_IMPLEMENTATION/) (EN) | Bauphasen-Pläne der Baueinheiten (v0.1.1–v0.1.3, v0.2.0–v0.2.4 gebaut) — Phasenverfolgung, Abnahme-Gates |
| [`charts/`](docs/study/charts/) (EN) | die Diagramme mit ihren Quellen (referenziert aus den Detaildokumenten) |
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
    docs/study/                Detaildokumentation der Studie (Methodik, Quellen, Architektur,
                               Datenmodell, Blei-Hintergrund; Übersetzungen, charts/)
    docs/plan/3SM/             Planungsnotizen (3-Stufen-System, EN)
    ├── README.md              einfachsprachige Anleitung zum Planungsbaum (EN)
    ├── MASTER.md, LOG.md      Projekt-Dashboard, Lifecycle-Log (EN)
    ├── 10_STRATEGY/           Recherchebefunde und Entscheide (was & warum) —
    │                          schlanke Themen-Zusammenfassungen; Details in docs/study/
    ├── 20_DESIGN/             technisches Design (wie genau, EN)
    └── _archive/              überholtes Material

## Status

Die Werkzeug-Einheiten v0.1.1–v0.2.4 sind gebaut und getestet (412
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

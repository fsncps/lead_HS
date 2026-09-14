---
language: de
translation_of: README.md
source_updated: 2026-09-14
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

## Aktueller Stand: der Drei-Fragen-Trichter (v0.2.2)

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

## Frühere Einheiten

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
| [`30_IMPLEMENTATION/`](docs/plan/3SM/30_IMPLEMENTATION/) (EN) | Bauphasen-Pläne der Baueinheiten (v0.1.1–v0.1.3, v0.2.0–v0.2.2 gebaut) — Phasenverfolgung, Abnahme-Gates |
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

Die Werkzeug-Einheiten v0.1.1–v0.2.2 sind gebaut und getestet (299
automatisierte Offline-Tests): Evidenzdatenbank, Quellenregister,
Quellensondierung, Feasibility-Berichte je Quelle, Zähl-Maschinerie für
Katalogdurchläufe (wartet auf eine Sammel-Freigabe), die
Datenlandschaft-Karte mit den drei Leitgrössen, die
Quellenfähigkeits-Sondierung der amtlichen Register sowie der
Drei-Fragen-Trichter im echten Netz (14.09.2026): Staging-Datenbank,
Wellen-Ausführung, vollständige Disposition des 101-Zeilen-Registers
und der Bericht mit Trichter-, CN8-Handels-, Identitäts-, Tiefen- und
Kapitel-Abschnitten — jede Zahl ein Abfrageergebnis. Der Bericht ist
unter `docs/report/` veröffentlicht. Die Methodik bleibt offen für
Revision, während Ergebnisse eintreffen.

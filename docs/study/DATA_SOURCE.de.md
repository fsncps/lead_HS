---
updated: 2026-09-18
language: de
translation_of: DATA_SOURCE.md
source_updated: 2026-09-18
---

Sprachen: [EN](DATA_SOURCE.md) · **DE** · [FR](DATA_SOURCE.fr.md)

# Datenquellen — Register, Zugang, Provenienz

## Zusammenfassung

Dies ist das operationale Register aller Datenquellen, auf die die Studie zurückgreift: was jede Quelle liefert, wie auf sie zugegriffen wird, mit welcher Granularität, unter welchen Bedingungen und mit welchem Verifikationsstatus. METHODOLOGY.md erklärt, warum diese Quellen verwendet werden; ARCHITECTURE.md (EN) behandelt, wie sie beschafft und gespeichert werden. Alle Quellen sind öffentlich abrufbar und kostenlos — eine harte Projektrandbedingung. Jeder aus einer Quelle übernommene Datensatz trägt seine Quell-URL und das Abrufdatum; Rohdokumente werden unverändert archiviert. Das Register ist so geschrieben, dass es ohne technischen Hintergrund lesbar ist — Begriffe werden bei der ersten Verwendung erläutert und im Glossar unten zusammengefasst.

## Verwendete Begriffe (Glossar in einfacher Sprache)

- **Provenienz:** die protokollierte Herkunft jedes Datenelements — aus welcher Quelle, von welcher URL, an welchem Datum abgerufen.
- **robots.txt:** eine kleine Datei, die Websites veröffentlichen, um automatischen Besuchern mitzuteilen, welche Seiten sie abrufen dürfen und welche nicht; die Werkzeuge der Studie halten sich daran.
- **(Höfliches) Scraping:** Webseiten automatisiert lesen — hier langsam und offen (identifizierter Besucher, Pausen zwischen Anfragen), niemals eine Site im Massenbetrieb abfragen.
- **Rate-Limit:** eine selbst auferlegte Pause zwischen Anfragen — höchstens eine Anfrage alle zwei Sekunden pro Site.
- **API:** eine offizielle, maschinenlesbare Datenschnittstelle eines Statistikanbieters — überall, wo vorhanden, dem Lesen von Webseiten vorgezogen.
- **CSV-Export:** eine herunterladbare Tabellendatei (kommagetrennte Werte).
- **CN8:** der 8-stellige Zolltarifcode, auf dessen Ebene Handelsstatistiken berichtet werden; «× Partner × Jahr» = aufgeschlüsselt nach Partnerland und Jahr.
- **SKU (Artikeleinheit):** ein Shop-Artikel; die Studie fasst SKUs zu Rezepturen zusammen (eine Rezeptur, egal wie viele Töne oder Gebindegrössen).
- **B2B-Portal:** ein Business-to-Business-Webshop für professionelle Kunden.
- **TDS (technisches Datenblatt):** die Leistungsdaten eines Produkts (Trocknungszeit, Ergiebigkeit) — zu unterscheiden vom Sicherheitsdatenblatt (SDB), das gefährliche Inhaltsstoffe listet (Abschnitt 3, ab 0,1 %).
- **UA-String:** die «User-Agent»-Kennung, die ein Programm mit jeder Webanfrage sendet; die Werkzeuge der Studie identifizieren sich und tragen eine Kontaktadresse.
- **sha256 (Hash):** ein digitaler Fingerabdruck des Inhalts einer Datei — identische Dateien haben ihn stets gemeinsam, jede Änderung verändert ihn; dient dem Nachweis, dass archivierte Dokumente unverändert sind.
- **PCN / SPIN / PRODCOM / NACE 20.30:** Register und Statistiken als Grundgesamtheits-Näherungen — definiert im Glossar von METHODOLOGY.md.
- **Access-DB / mdbtools:** SPIN wird als Microsoft-Access-Datenbankdatei ausgeliefert; mdbtools ist das Linux-Dienstprogramm, das sie lesen kann.
- **JS-gesperrt (JS-gated):** eine Site, die ihren Inhalt erst nach Ausführung von JavaScript zeigt, sodass ein einfacher Download fehlschlägt (fedlex) — braucht einen Browser oder manuelles Kopieren.

## Quellenklassen

Fünf Klassen mit stabilen IDs (das Datenbankfeld `source.class`):

- **CS — Zoll- & Handelsstatistik:** Schweizer EZV/swiss-impex (primär: strukturiert den Schweizer Markt nach Herkunft); Eurostat Comext (EU-Kontext).
- **PE — Produkt- & SDB-Evidenz (Web):** Hersteller-/Markenseiten, B2B-Portale, DIY-Kettenkataloge, Marinehändler, Kunstbedarfsläden — der Auswahlrahmen und die SDB-Evidenzbasis. Mehrsprachig DE/FR/IT/EN.
- **LG — Rechts- & Regulierungstexte:** THG, VIPaV, ChemRRV, SECO-Negativliste, REACH-Anhänge XIV/XVII, OJ-Entscheide, ECHA-Register.
- **ST — Struktur- & Produktstatistiken:** ECHA PCN, Nordischer SPIN, Eurostat PRODCOM/SBS — Grundgesamtheits-Näherungen und Skalierungsanker.
- **LI — Literatur & Industrie:** peer-reviewte Studien, IPEN, CEPE.

## PE — Konkrete Quellentaxonomie und Ausgangsquellen (Seed-Sites)

Die PE-Klasse (Produkt- & SDB-Evidenz) ist, woher das eigentliche MSDS/TDS-Korpus kommt. Es gibt **kein einzelnes, kostenloses EU-Verzeichnis von Produktsicherheitsdatenblättern** — die grossen Aggregatoren (MSDSonline, Chemwatch, SDS Europe) sind kostenpflichtig und durch die Kostenbeschränkung ausgeschlossen. Das Korpus wird daher aus öffentlichen Hersteller- und Händlersites aufgebaut. Vier Stufen:

| Stufe | Quellen | Was sie liefert | Bleirelevante Ströme |
|---|---|---|---|
| **A — SDB-Bibliotheken der Hersteller/Marken** (primär) | AkzoNobel (Dulux, International, Sikkens), PPG, Sherwin-Williams, Jotun, Hempel, Sika, Sto, Caparol/DAW, Alpina, Tikkurila, Teknos, Farrow & Ball | kostenlose öffentliche SDB-PDFs auf Produktseiten / SDB-Portalen | alle |
| **B — Nischenhersteller** (die bleirelevanten) | Marine/Korrosionsschutz: Epifanes, Veneziani, Boero, De IJssel, Seajet. Künstlerfarben: Old Holland, Zecchi, Kremer Pigmente, Michael Harding, Winsor & Newton, Sennelier, Schmincke, Talens, Maimeri, Blockx, Natural Pigments | SDB + TDS für die bleirelevanten Nischen | Bleimennige, Künstlerfarben |
| **C — Handels-/B2B-Portale** | Marine: SVB (svb.de), toplicht.de. CH-DIY: Coop Bau+Hobby, Migros Do-it+Garten, Hornbach, Bauhaus, Jumbo, OBI. EU-DIY: B&Q, Leroy Merlin, Castorama, Gamma, Praxis, Toom. B2B-Handelsportale (DE/FR/IT) | Listings + SDB-Links, Produktspezifikation | Auswahlrahmen + SDB |
| **D — Kostenlose SDB-Aggregatoren** | GESTIS (IFA) — nur auf Stoffebene, keine Produkt-SDB; einige kostenlose SDB-Seiten | Stoffdaten, Kontext | Kontext |

**Hinweis zu Stufe D:** GESTIS ist auf Stoffebene (keine Produkt-SDB); die meisten produktbezogenen Aggregatoren sind kostenpflichtig. Die Stufen A + C sind das praktische kostenlose Korpus; Stufe B deckt die bleirelevanten Nischen ab.

**Seed-Site-Liste** (durch die v0.1.1-Sondierung aufgezählt/bestätigt; das Register-CSV ist das massgebliche Register):

- Marine: svb.de, toplicht.de
- Künstler: oldholland.com, zecchi.it, kremer-pigmente.com, michaelharding.co.uk, winsornewton.com, sennelier.fr, schmincke.de, talens.com, maimeri.it
- DIY (CH): coop-bauundhobby.ch, migros-doitgarten.ch, hornbach.ch, bauhaus.ch, jumbo.ch, obi.ch
- DIY (EU): hornbach.de, obi.de, bauhaus.de, leroymerlin.fr, castorama.fr, gamma.nl, praxis.nl, diy.com (B&Q)
- Majors: akzonobel.com, ppg.com, sherwin-williams.com, jotun.com, hempel.com, sika.com, sto.com, caparol.de, tikkurila.com, teknos.com

## Quellenregister

| ID | Klasse | Quelle | Liefert | Zugang | Granularität | Status |
|----|-------|--------|----------|--------|-------------|--------|
| CS-1 | CS | swiss-impex.admin.ch (EZV) | CH-Importe/-Exporte, 3208/3209 (+3213) | Web-UI / CSV-Export (zu bestätigen) | CN8 × Partner × Jahr | OFFEN — freier Zugang & Granularität zu bestätigen (Phase 0, hohe Priorität) |
| CS-2 | CS | Eurostat Comext DS-045409 | EU27-Aussenhandel | öffentliche API | CN8 × Partner × Jahr | verifiziert (2023 extrahiert) |
| PE-1 | PE | Hersteller-/Markenseiten | Produktkataloge, SDB-PDFs | höfliches Scraping | Produkt/Rezeptur | OFFEN — Seed-Liste Stufe A + B; Site-Liste aufgebaut Phase 1–2 |
| PE-2 | PE | DIY-Ketten (CH-Kandidaten: Coop Bau+Hobby, Migros Do-it+Garten, Hornbach, Bauhaus, Jumbo, OBI; EU-Äquivalente: B&Q, Leroy Merlin, Castorama, Gamma, Praxis, Toom) | Handels-Listings | höfliches Scraping | SKU → Rezeptur | OFFEN — Stufe C |
| PE-3 | PE | B2B-/Handelsportale (DE/FR/IT) | professionelle Listings, TDS | höfliches Scraping | Produkt | OFFEN — Stufe C |
| PE-4 | PE | Marinehändler, Kunstbedarfsläden | Nischenströme (Bleimennige, Künstlerfarben) | höfliches Scraping | Produkt | teilweise verifiziert (Seed-Einträge vorhanden) — Stufe B/C |
| LG-1 | LG | fedlex / Lexaris | konsolidierte THG, VIPaV, ChemRRV | Download | Artikel | THG verifiziert; aktuelle ChemRRV/VIPaV-Konsolidierung OFFEN (fedlex JS-gesperrt) |
| LG-2 | LG | SECO (Negativliste, Fünfjahresbericht, CdD-Seiten) | Ausnahmenkatalog, Überprüfungspraxis | Download | Eintrag | verifiziert |
| LG-3 | LG | EUR-Lex / OJ | REACH konsolidiert, Annex-XIV-Entscheide, Verweigerung 2022 | Download | Eintrag | weitgehend verifiziert; OJ-Referenz 2022 OFFEN |
| LG-4 | LG | ECHA (DUR, EC-Inventar) | Zulassungsverweigerungen; CAS/EC-Verifikation | Web | Eintrag/Stoff | DUR verifiziert; EC-Inventar-Prüfungen für 2 CAS ausstehend |
| ST-1 | ST | ECHA-PCN-Statistiken | Rezepturzählungen (gefährliche Gemische) | öffentliche Statistiken | aggregiert | OFFEN — Rezepturebenen-Agregate lokalisieren |
| ST-2 | ST | Nordischer SPIN (DK/SE/NO/FI) | Zubereitungszählungen, Blei-CAS-Inzidenz | kostenloser Access-DB-Download | Stoff × Verwendung × Land | verfügbar; Extraktionsweg OFFEN |
| ST-3 | ST | Eurostat PRODCOM / SBS | Produktionswerte, Herstellerzählungen | öffentliche API | NACE 20.30 | verifiziert |
| LI-1 | LI | Studien / IPEN / CEPE | Kalibrierungs-Priors | DOI / Web | Studienebene | verifiziert |

Das Register wächst während Phase 0–2; die Datenbanktabelle `source` spiegelt es (siehe DATA_MODEL.md (EN)).

## Sondierungsdurchlauf (Einheit v0.1.1)

Vor jeder Sammlung wird jede OFFENE Registerzeile einmal sondiert (`leadhs probe run`, ARCHITECTURE.md (EN) M0) — ein kleiner, höflicher Testbesuch, der protokolliert, was die Quelle tatsächlich liefert — und die Statusspalte wird aus den Sondierungsergebnissen aktualisiert. Der Ablauf pro Quelle:

![Wie jede Quelle geprüft wird: robots und Bedingungen werden respektiert, Anfragen im Mindestabstand von zwei Sekunden gesendet, Sperren und Überraschungen als Befunde dokumentiert, Muster unverändert archiviert](charts/probe-process.png)

Pro Klasse:

- **CS:** swiss-impex (CS-1) — freien Zugang, Granularität CN8 × Partner × Jahr, Abdeckung 2019–2025, Exportformat bestätigen; als Sondierungsbefunde protokollieren. Comext (CS-2) bereits verifiziert.
- **PE:** Kandidatensites pro Strom aufzählen (DIY-Ketten, B2B, Marine-/Kunst-Nischen); Katalogprodukte zählen (pro Kategorie, wo exponiert); robots/Bedingungen/Rate-Limit/Sprachen und SDB-Verfügbarkeit an einer kleinen Seitenstichprobe protokollieren (roh archiviert); gesperrte Sites für die manuelle Fallback-Regel (D4) markieren.
- **ST:** SPIN (ST-2) — Download + Prüfung des Extraktionswegs (mdbtools auf Slackware); PCN (ST-1) — Rezepturebenen-Agregate lokalisieren (manuelles Web, protokolliert wie jeder Sondierungsbefund).
- **LG:** nicht sondiert — Rechtstext-Verifikation bleibt manueller Dokumenten-Workstream (Phase-0-Rechtsdossier).

Die Sondierung hält die untenstehende Zugriffs- und Scraping-Disziplin ein — leichtgewichtig by design (Zählungen und Randbedingungen, keine Massensammlung). Sondierungsergebnisse sind vorläufige Rahmen-Inputs (MASTER D20).

## Provenienzregeln (bindend)

1. Jeder gelesene Datensatz speichert `source_id`, `url`, `retrieved_at`.
2. Rohdokumente (HTML/PDF) werden exakt wie abgerufen unter `data/raw/<source-id>/<sha256>.<ext>` archiviert — der Dateiname ist ein digitaler Fingerabdruck (sha256) des Dateiinhalts, sodass jede spätere Änderung erkennbar ist; die Datenbank referenziert diesen Fingerabdruck, der Rohspeicher dient als Audit-Trail.
3. Tragende Zahlen in Berichten tragen Quellenname, Jahr, URL und Abrufdatum (Projektkonvention, AGENTS.md).
4. Rechtstexte werden mit SR/CELEX-Nummer und Konsolidierungsdatum («Stand») zitiert, nicht allein mit URL.

## Zugriffs- & Scraping-Disziplin (bindend)

- Nur öffentlich abrufbare, kostenlose Quellen — keine kostenpflichtigen Datenbanken, keine kommerziellen Marktberichte (harte Randbedingung).
- robots.txt und Seitenbedingungen respektieren; den Scraper identifizieren (UA-String mit Kontaktadresse); Rate-Limit (Standard ≤ 1 Anfrage / 2 s, domänenweise Warteschlange); kein Massenabfragen.
- Offizielle Exporte/APIs dem HTML-Scraping vorziehen, wo angeboten (swiss-impex CSV, Eurostat API, SPIN-Download).
- Nur öffentlich publizierte SDB — keine Konten, keine Paywalls, keine ToS-Umgehungen (EU-Recht verpflichtet zur kostenlosen SDB auf Anfrage, REACH Art. 31(8), aber diese Studie nutzt nur publizierte Blätter).
- Wenn eine Site Scraping blockiert: manuelle Beschaffung des benötigten Teils; Zugriffsart pro Datensatz protokollieren.

## ENTSCHEIDE

- D1: fünf Quellenklassen (CS/PE/LG/ST/LI) mit stabilen IDs; die DB-Tabelle `source` spiegelt dieses Register.
- D2: Provenienz ist auf Datensatzebene bindend (URL + Abrufdatum + Roh-Hash), nicht nur auf Dokumentebene.
- D3: offizielle Exporte/APIs dem HTML-Scraping vorgezogen, wo vorhanden.
- D4: keine Konten, keine Paywalls, keine ToS-Umgehungen; manueller Fallback bei Blockade, pro Datensatz protokolliert.
- D5: jede OFFENE Registerzeile wird vor der Sammlung einmal sondiert (Einheit v0.1.1), ihr Status aus den Sondierungsbefunden aktualisiert (MASTER D19).

## OFFENE PUNKTE

- CS-1 swiss-impex: freien Zugang, CN8 × Partner-Granularität, mehrjährige Abdeckung (2019–2025), Exportformat bestätigen — Phase 0, hohe Priorität; Sondierungsziel von v0.1.1.
- PE-Site-Liste: Seed-Sites der Stufen A/B/C (siehe «PE — Konkrete Quellentaxonomie und Ausgangsquellen») in Phase 1–2 aufzählen und priorisieren (Rahmenaufbau); Bestätigung der Lesbarkeit durch die v0.1.1-Sondierung begonnen.
- ST-2 SPIN Access-DB: Extraktionsweg auf Slackware (mdbtools?) — OFFEN; während der v0.1.1-Sondierung geprüft.
- ST-1 PCN: Rezepturebenen-Agregate lokalisieren (ECHA-Veröffentlichungspraxis).
- LG-1 fedlex-JS-Sperre für konsolidierte VIPaV/ChemRRV (Browser-Extraktion nötig) — übernommen aus dem Rechtsdossier.

## REFERENZEN

- URLs der in der Recherche 2026-08-31/09-10 bereits verifizierten Quellen: METHODOLOGY.md §REFERENZEN. Dieses Register ergänzt operationale Zugangsmetadaten, sobald sie bestätigt sind.

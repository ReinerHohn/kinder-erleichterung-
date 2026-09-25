# Kinder-Erleichterung

Ein durchsuchbarer, **evidenzbasierter Katalog** rund um die Frage: *Was macht Kinder-Haben stressig, warum wollen viele weniger Kinder — und was hilft wirklich dagegen?* Mit ehrlichem Blick darauf, wo **KI, Robotik und clevere Produkte** real entlasten und wo es Hype ist.

Gebaut im selben Baumuster wie die Schwester-Projekte (`leistungsfaehigkeit`, `flirt`, `finanz-wissen`): `hebel/*.json` → `build.py` → self-contained `dashboard.html`. Nur Python-Standardbibliothek, keine Abhängigkeiten, läuft offline.

## Was drin ist

101 Karten (Wirkung 1–5 · Aufwand 1–5 · Evidenz A/B/C · Quellen) in 9 Kategorien:

| Kategorie | Worum es geht |
|---|---|
| 🧭 **Strategie & Synthese** | Der rote Faden: Hebel-Ranking „Wie macht man Kinder wieder attraktiv?" (Hürden abbauen statt Wunsch erzeugen) |
| 🍼 **Stressoren im Alltag** | Schlafmangel, Mental Load, Betreuungslücke, Babysitter-Suche, Freiheitsverlust, Kosten, Teilzeitfalle, Terminchaos, Paarkonflikt, Burnout, Hebammenmangel/Geburtstrauma, Wochenbettdepression |
| 📉 **Ursachen: weniger Kinderwunsch** | Opportunitätskosten/Child Penalty, Gender-Care-Gap, Unsicherheit, Wohnkosten, Aufschub, Partnerlosigkeit, Werte, Klima (überschätzt), **Fertility Gap**, Südkorea-Extremfall, Migration |
| 🛠️ **Lösungen & Politik** | Kita-Ausbau, Vätermonate, Elterngeld, Ganztag, Wohnraum, Steuer/Splitting, Alleinerziehende, Länder­vergleich FR/SE, „was NICHT wirkt" (Ungarn), 4-Tage-Woche, IVF/Social Freezing, „Es braucht ein Dorf" |
| 🤖 **KI & Robotik** | Saug-/Wisch-/Mähroboter, Admin-KI, Lern-KI, smarte Babyphones, soziale Roboter, Sprachassistenten, Telemedizin/Symptomchecker, Exoskelette, Telepräsenz, Ungleichheit |
| 🚀 **Frontier & Zukunftstechnik** | Humanoide Roboter (Fahrplan 2026–2035), künstliche Gebärmutter/Ectogenesis, In-vitro-Gametogenese, PGT-P, Ovar-Verjüngung, Gebärmuttertransplantation |
| 💡 **Sweet Spots (Produkte & Gadgets)** | SNOO & günstige Wiegen, weißes Rauschen, Pucken, Tragetuch, Babyphone, Nasensauger, Thermometer, Windel-Abo, Familienkalender — inkl. „lohnt NICHT" |
| 💼 **Service- & Geschäftsideen** | Kindergeburtstag-Service, Geschenke-Concierge, geprüfte Babysitter-Vermittlung, Meal-Abo, Bürokratie-Concierge, Ferienbetreuung, Leih-Oma u.a. — mit ehrlicher Tragfähigkeits-Bewertung |
| 📋 **Was auf mich zukommt (Rechte & Fahrplan)** | Kind krank (§45 SGB V, §616 BGB), Mutterschutz, Elternzeit, Elterngeld, Kündigungsschutz, Brückenteilzeit, Betriebskita, Tagespflege/Au-pair, Fahrplan, U-Untersuchungen |

Dazu ein **U-Untersuchungs-Terminrechner** (U1–U9, J1) direkt im Dashboard: Geburtsdatum eingeben → alle Fälligkeiten mit „jetzt fällig"-Markierung. Es gibt dafür keine offizielle API — die Zeitfenster (G-BA/BZgA) sind fest hinterlegt und laufen offline im Browser.

## Nutzung

```sh
python3 build.py     # baut dashboard.html + KATALOG.md
python3 test.py      # Struktur-/Logik-Tests
./run.sh             # bauen, testen, Dashboard öffnen
```

Sortierung standardmäßig nach **Sweet Spots zuerst** (Wirkung ÷ Aufwand) — die Low-Hanging-Fruits oben. Umschaltbar auf Wirkung, geringster Aufwand, beste Evidenz, Name.

## Prinzipien

- **Anti-Hype:** ehrliche Grenzen, verbreitete Irrtümer mit echten Zahlen, „lohnt-NICHT"-Karten. Kinderbetreuung wird nicht an Technik delegiert (Bindung/Aufsicht/Sicherheit zuerst).
- **Belegt:** jede Karte mit Quellen (OECD, DIW, ifo, BiB, Destatis, Stiftung Warentest, AAP, FDA, Gesetze). Evidenzgrad transparent.
- **Kein Rat-Ersatz:** Wissenswerkzeug, kein medizinischer/rechtlicher/steuerlicher Rat.

## Neue Karte hinzufügen

Eine Datei `hebel/<id>.json` nach `schema.json` anlegen (`id` = Dateiname, kebab-case), dann `python3 build.py`. `test.py` prüft Pflichtfelder, Wertebereiche, Quellen-URLs und Synergie-Links.

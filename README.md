# Doppel-K.-o.-System: eine zweite Chance

Siebtes und letztes Stück der **Turnierplanung**-Linie der "Konzepte"-Reihe von [sebastianhanisch.net](https://sebastianhanisch.net).
Interaktive Demo: `streamlit run app.py`.

**[→ Demo live ausprobieren](#) (Deploy offen)**

## Ergebnis in Kürze

Echte strukturelle Variante von Stück 2 (K.-o.-System mit Setzliste): ein **Verlierer-Baum** gibt jedem
Team eine zweite Chance, wie in den meisten E-Sport-Turnieren üblich - erst zwei Niederlagen werfen raus.
Gemessen (3.000 Wiederholungen je Teilnehmerzahl, Rating-Vorsprung 500 für Setzplatz 1):

| Teams | P(Favorit gewinnt) Einzel | P(Favorit gewinnt) Doppel | Ø Spiele Einzel | Ø Spiele Doppel |
|---|---|---|---|---|
| 8  | 85,5 % | 96,5 % | 7,0  | 14,2 |
| 16 | 80,5 % | 94,8 % | 15,0 | 30,2 |
| 32 | 75,8 % | 93,2 % | 31,0 | 62,2 |

Der Verlierer-Baum schützt den wirklich stärksten Teilnehmer spürbar besser vor einem einzelnen
schlechten Tag - **aber zu einem echten Preis**: doppelt so viele Spiele. Der Effekt braucht zudem
einen echten Stärkeunterschied (Preset "Ausgeglichenes Feld": bei Rating-Vorsprung 0 schrumpft die
Differenz zwischen beiden Formaten fast auf null).

## Was die Demo zeigt

1. **Ein Team auf seinem Weg**: die Route eines gewählten Teams durch Gewinner- und Verlierer-Baum,
   Spiel für Spiel - Kernerzählung eines Doppel-K.-o.-Systems ("verloren, zurückgekämpft, ...").
2. **Gewinner-Baum + Verlierer-Baum**: beide als echter Turnierbaum, im selben visuellen Stil wie
   Stück 2 - der Verlierer-Baum zeigt zusätzlich farblich, welche Teams frisch aus dem Gewinner-Baum
   durchgefallen sind.
3. **📐 Schützt der Verlierer-Baum den wirklich stärksten Teilnehmer?**: Sieg-Wahrscheinlichkeit im
   Vergleich zu Stück 2s Einzel-K.-o.
4. **🔬 Experiment**: der Spielanzahl-Preis der zweiten Chance.
5. **🚧 Wo die Annahmen enden**: nur Zweierpotenzen, vereinfachte Verlierer-Baum-Paarung, kein Remis.

## Modell und Verfahren

- **Gewinner-Baum**: identische Setzlisten-Rekursion wie Stück 2 (`standard_seed_order`).
- **Verlierer-Baum** (`de2_bracket.py`, per WebSearch verifizierte Standardkonstruktion): jede
  Gewinner-Baum-Runde liefert frische Verlierer. Ab der zweiten Etappe hat der Verlierer-Baum eine
  **Minor-Phase** (bisherige Teilnehmer spielen gegeneinander) und eine **Major-Phase** (Minor-Sieger
  gegen die frischen Gewinner-Baum-Verlierer derselben Ebene) - verhindert sofortige
  Wiederholungsspiele. Für $n=2^k$ Teams: $k-1$ solcher Doppel-Etappen, $2(k-1)$ Verlierer-Baum-Runden
  insgesamt.
- **Bracket-Reset**: Finale zwischen Gewinner-Baum-Champion (0 Niederlagen) und Verlierer-Baum-Champion
  (1 Niederlage) - gewinnt Letzterer, folgt ein entscheidendes zweites Spiel (beide stünden bei 1
  Niederlage). Gesamtspielzahl: $2n-2$ ohne Reset, $2n-1$ mit Reset (jedes ausscheidende Team verliert
  exakt zweimal, der Champion höchstens einmal).
- **Quellen**: [Wikipedia, "Double-elimination tournament"](https://en.wikipedia.org/wiki/Double-elimination_tournament)
  (Minor-/Major-Rundenstruktur, Bracket-Reset/"if game"); [Toornament Knowledge Base, "Introducing the
  Loser Bracket"](https://help.toornament.com/structures/introducing-the-loser-bracket) (Bestätigung:
  die genaue Paarung innerhalb einer Minor-Runde ist zwischen Plattformen nicht einheitlich, siehe "Wo
  die Annahmen enden").

## Was diese Demo nicht kann

Nur Zweierpotenzen als Teilnehmerzahl (kein Freilos-Mechanismus). Die Verlierer-Baum-Paarung innerhalb
einer Minor-Runde ist eine wohldefinierte, aber nicht die einzig "offizielle" Regel - reale Plattformen
variieren hier. Kein Remis, reiner Elo-Münzwurf wie in Stück 2.

## Verifikation

- **Strukturell** (`tests/test_bracket.py`): Setzliste reproduziert die bekannte 16er-Tafel, jedes
  ausscheidende Team hat exakt 2 Niederlagen, Gesamtspielzahl folgt der $2n{-}2$/$2n{-}1$-Formel,
  Bracket-Reset erzeugt genau 2 Finalspiele.
- **Politik-Vergleich** (`tests/test_evaluation.py`): Doppel-K.-o. schützt den Favoriten immer besser
  als Einzel-K.-o., braucht doppelt so viele Spiele, der Vorteil schrumpft ohne Rating-Vorsprung.
- **Regressionstests** (`tests/test_claims.py`): konkrete Zahlen aus der Tabelle oben fixiert.

## Dateistruktur

```
app.py                 Streamlit-Oberfläche
de2_constants.py        Regler-Grenzen, Presets
de2_elo.py               Elo-Erwartungswert
de2_bracket.py            Einzel- und Doppel-K.-o.-Simulation
de2_evaluation.py         Vergleich, Sweeps
de2_presets.py            Permalink-Muster
de2_visualization.py      Plotly-Grafiken
tests/                    pytest-Suite
```

## Lokal starten

```bash
python -m venv venv
venv\Scripts\activate  # Windows; unter Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Turnierplanung: 7 Wege zum Turnierplan](https://sebastianhanisch.net/konzepte-turnierplanung.html).

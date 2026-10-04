"""Doppel-K.-o.-System - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Siebtes und letztes Stück der "Turnierplanung"-Linie der "Konzepte"-Reihe: eine echte strukturelle
Variante von Stück 2 (K.-o.-System mit Setzliste) - ein Verlierer-Baum gibt jedem Team eine zweite
Chance, wie in den meisten E-Sport-Turnieren üblich. Zwei Niederlagen werfen raus statt einer.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import de2_constants as C
from de2_bracket import simulate_double_elimination, simulate_single_elimination
from de2_evaluation import ratings_with_favorite, sweep_comparison
from de2_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from de2_visualization import (
    build_losers_bracket_tree,
    build_match_count_chart,
    build_win_probability_chart,
    build_winners_bracket_tree,
)

st.set_page_config(page_title="Doppel-K.-o.-System – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _tournaments(n_seeds, seed, favorite_edge):
    ratings = ratings_with_favorite(n_seeds, favorite_edge)
    import random

    single = simulate_single_elimination(n_seeds, ratings, random.Random(seed))
    double = simulate_double_elimination(n_seeds, ratings, random.Random(seed))
    return single, double


@st.cache_data(show_spinner=False)
def _sweep():
    return sweep_comparison(C.SWEEP_N_SEEDS_VALUES, C.SWEEP_REPS)


def _team_route(double_result, team):
    lines = []
    for m in double_result.matches:
        if team not in (m.seed_a, m.seed_b):
            continue
        opp = m.seed_b if m.seed_a == team else m.seed_a
        result = "gewinnt" if m.winner == team else "verliert"
        bracket_label = {"WB": "Gewinner-Baum", "LB": "Verlierer-Baum", "GF": "Finale"}[m.bracket]
        lines.append(f"**{bracket_label} ({m.label})**: gegen Setzplatz {opp} - {result}")
    return lines


st.title("🥈 Doppel-K.-o.-System: eine zweite Chance")
st.markdown(
    """
Beim K.-o.-System aus Stück 2 wirft eine einzige Niederlage sofort raus - ein einziger schlechter Tag
kann den eigentlich stärksten Teilnehmer eliminieren. Das **Doppel-K.-o.-System** (Standard bei den
meisten E-Sport-Turnieren) gibt jedem eine zweite Chance: wer im **Gewinner-Baum** verliert, fällt in
den **Verlierer-Baum** und kämpft sich zurück. Erst zwei Niederlagen werfen wirklich raus. Das Finale
zwischen beiden Bäumen kann sogar zweimal gespielt werden (**Bracket-Reset**), wenn der Verlierer-Baum-
Finalist das erste Finale gewinnt - beide stünden dann bei einer Niederlage.
"""
)
st.caption(
    "Baut auf Stück 2 (bracket-seeding-demo) auf: identische Setzliste für den Gewinner-Baum. Neu ist "
    "der Verlierer-Baum (Minor-/Major-Rundenstruktur, siehe README) und die Frage: hilft die zweite "
    "Chance dem wirklich stärksten Team - und was kostet das an zusätzlichen Spielen?"
)

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_seeds = st.select_slider("Teilnehmerzahl", options=C.N_SEEDS_OPTIONS, key="n_seeds_select")
    seed = st.slider("Saatwert", *bounds("seed_slider"), key="seed_slider",
                      help="Bestimmt alle simulierten Spielergebnisse.")
    favorite_edge = st.slider(
        "Rating-Vorsprung Setzplatz 1", *bounds("favorite_edge_slider"), step=C.FAVORITE_EDGE_STEP,
        key="favorite_edge_slider", format="%d", help="0 = alle Teams gleich stark.",
    )

sync_query_params(n_seeds, seed, favorite_edge)

n_seeds = int(n_seeds)
seed = int(seed)
favorite_edge = int(favorite_edge)
single_result, double_result = _tournaments(n_seeds, seed, favorite_edge)

st.markdown("---")
st.markdown("## 🎯 Ein Team auf seinem Weg durch beide Bäume")
focus_team = st.selectbox("Team im Fokus", list(range(1, n_seeds + 1)), key="focus_team_select")
route = _team_route(double_result, focus_team)
if focus_team == double_result.champion:
    st.success(f"🏆 Setzplatz {focus_team} gewinnt das Turnier!")
elif double_result.losses[focus_team] == 1:
    st.info(f"Setzplatz {focus_team} steht noch im Turnier (1 Niederlage).")
else:
    st.warning(f"Setzplatz {focus_team} scheidet mit 2 Niederlagen aus.")
for line in route:
    st.markdown("- " + line)

st.markdown("---")
col_wb, col_lb = st.columns(2)
with col_wb:
    st.markdown("### Gewinner-Baum")
    st.plotly_chart(build_winners_bracket_tree(double_result.wb_rounds, double_result.champion),
                     width="stretch", key=f"wb_{n_seeds}_{seed}_{favorite_edge}")
with col_lb:
    st.markdown("### Verlierer-Baum")
    st.plotly_chart(build_losers_bracket_tree(double_result.matches, double_result.champion),
                     width="stretch", key=f"lb_{n_seeds}_{seed}_{favorite_edge}")
    st.caption("Orange = frisch aus dem Gewinner-Baum durchgefallen oder Verlierer-Baum-Sieger, Gold = Turniersieger.")

st.caption(
    f"Turnier-Sieger: Setzplatz {double_result.champion} - {double_result.n_matches} Spiele insgesamt"
    + (", inklusive Bracket-Reset" if double_result.reset_happened else " (kein Bracket-Reset nötig)")
    + ". Zum Vergleich: Einzel-K.-o. mit denselben Ratings/Setzliste (anderer Zufallslauf) hätte "
    f"Setzplatz {single_result.champion} gewinnen lassen, in {len(single_result.matches)} Spielen."
)

st.markdown("---")
st.subheader("📐 Schützt der Verlierer-Baum den wirklich stärksten Teilnehmer?")
sweep = _sweep()
st.plotly_chart(build_win_probability_chart(sweep), width="stretch", key="win_prob_chart")
current = next((s for s in sweep if s.n_seeds == n_seeds), None)
if current is not None:
    st.caption(
        f"Bei {n_seeds} Teams (Rating-Vorsprung {C.DEFAULT_FAVORITE_EDGE}, {current.n_reps:,} Wiederholungen): "
        f"Einzel-K.-o. lässt den Favoriten in {current.p_favorite_wins_single:.1%} der Fälle gewinnen, "
        f"Doppel-K.-o. in {current.p_favorite_wins_double:.1%} - die zweite Chance schützt echt vor "
        "einem einzelnen schlechten Tag."
    )

st.markdown("---")
st.subheader("🔬 Experiment: was kostet die zweite Chance an Spielen?")
st.plotly_chart(build_match_count_chart(sweep), width="stretch", key="match_count_chart")
if current is not None:
    st.caption(
        f"Bei {n_seeds} Teams: Einzel-K.-o. braucht im Mittel {current.mean_matches_single:.1f} Spiele, "
        f"Doppel-K.-o. {current.mean_matches_double:.1f} - doppelt so viele (plus vereinzelt ein "
        f"Bracket-Reset-Spiel, hier in {current.reset_rate:.1%} der Läufe). Der Fairness-Gewinn hat "
        "einen echten, messbaren Preis: doppelt so viele Spiele und damit Spielzeit."
    )

st.markdown("---")

with st.expander("🚧 Wo die Annahmen enden"):
    st.markdown(
        """
- **Nur Zweierpotenzen als Teilnehmerzahl.** Kein Freilos-Mechanismus wie in Stück 2 - hier bewusst
  ausgeklammert, um die Verlierer-Baum-Konstruktion nicht zusätzlich zu verkomplizieren.
- **Verlierer-Baum-Paarung ist eine wohldefinierte, aber nicht die einzig "offizielle" Regel.** Reale
  Turnierplattformen (Toornament, Challonge, ...) variieren in der genauen Paarung innerhalb einer
  Minor-Runde - die Minor-/Major-Grundstruktur (verhindert sofortige Wiederholungsspiele) ist
  Standard, die Reihenfolge innerhalb einer Runde nicht.
- **Kein Remis, keine echten Ergebnisse** - reiner Elo-Münzwurf wie in Stück 2.
- **Der gemessene Fairness-Gewinn braucht einen echten Stärkeunterschied.** Bei Rating-Vorsprung 0
  (Preset "Ausgeglichenes Feld") verschwindet der Effekt fast vollständig - der Verlierer-Baum schützt
  vor Pech, nicht vor Gleichstand.
        """
    )

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gewinner-Baum**: identische Setzlisten-Rekursion wie Stück 2 (`standard_seed_order`). **Verlierer-
Baum**: WB-Runde $r$ liefert $n/2^r$ frische Verlierer. Jede LB-Etappe ab der zweiten hat eine
Minor-Phase (bisherige LB-Teilnehmer spielen gegeneinander) und eine Major-Phase (Minor-Sieger gegen
die frischen WB-Verlierer derselben Ebene) - $k{-}1$ solcher Doppel-Etappen für $n=2^k$ Teams, macht
insgesamt $2(k{-}1)$ LB-Runden. Gesamtspielzahl ohne Bracket-Reset: $2n-2$ (jedes ausscheidende Team
verliert genau zweimal, der Champion höchstens einmal); mit Reset: $2n-1$.

**Bracket-Reset**: das Finale zwischen Gewinner-Baum-Champion (0 Niederlagen) und Verlierer-Baum-
Champion (1 Niederlage) - gewinnt Letzterer, stehen beide bei 1 Niederlage, ein entscheidendes zweites
Spiel folgt.

Implementiert in `de2_bracket.py` (beide Turnierformen) und `de2_evaluation.py` (Vergleich, Sweeps).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Turnierplanung: 7 Wege zum Turnierplan](https://sebastianhanisch.net/konzepte-turnierplanung.html)."
)

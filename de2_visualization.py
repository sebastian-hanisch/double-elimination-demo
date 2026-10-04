"""Plotly-Visualisierungen: Gewinner-Baum (identische Konstruktion wie bracket-seeding-demo),
Verlierer-Baum als Etappen-Tabelle, Vergleichsdiagramme. Alle Figuren per lock_axes gesperrt
(Touch-Scrolling-Konvention des Portfolios)."""

from __future__ import annotations

import plotly.graph_objects as go

from de2_bracket import DoubleEliminationResult
from de2_evaluation import ComparisonStats

BLUE = "#1f77b4"
ORANGE = "#d68a2e"
GOLD = "#e8b923"
GRAY = "#8a8f98"
GREEN = "#2ca02c"
RED = "#c0392b"


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def build_winners_bracket_tree(rounds: tuple, champion: int) -> go.Figure:
    positions = [list(range(len(rounds[0])))]
    for r in range(1, len(rounds)):
        prev = positions[r - 1]
        positions.append([(prev[2 * i] + prev[2 * i + 1]) / 2 for i in range(len(rounds[r]))])

    fig = go.Figure()
    for r in range(len(rounds) - 1):
        for i in range(len(rounds[r])):
            y_next = positions[r + 1][i // 2]
            fig.add_trace(go.Scatter(
                x=[r, r + 1], y=[positions[r][i], y_next], mode="lines",
                line=dict(color=GRAY, width=2), hoverinfo="skip", showlegend=False,
            ))
    for r in range(len(rounds)):
        for i, s in enumerate(rounds[r]):
            is_champion = r == len(rounds) - 1
            color = GOLD if is_champion else BLUE
            fig.add_trace(go.Scatter(
                x=[r], y=[positions[r][i]], mode="markers+text", text=[str(s)],
                textposition="middle center", textfont=dict(color="white", size=11),
                marker=dict(size=26, color=color, line=dict(width=2, color="white")),
                hovertext=f"Setzplatz {s}" + (" - WB-Champion" if is_champion else ""),
                hoverinfo="text", showlegend=False,
            ))
    n_rounds = len(rounds) - 1
    labels = [f"WB R{r+1}" for r in range(n_rounds)] + ["WB-Champion"]
    fig.update_xaxes(tickmode="array", tickvals=list(range(len(rounds))), ticktext=labels)
    fig.update_yaxes(visible=False, autorange="reversed")
    fig.update_layout(template="plotly_white", height=max(300, 22 * len(rounds[0])),
                       margin=dict(l=10, r=10, t=10, b=30))
    return lock_axes(fig)


def build_losers_bracket_tree(matches: tuple, champion: int) -> go.Figure:
    """Echter Baum wie build_winners_bracket_tree, nicht nur eine Etappen-Tabelle - Minor-Runden
    verbinden zwei Knoten derselben Spalte wie im Gewinner-Baum, Major-Runden zeigen zusaetzlich den
    frisch aus dem Gewinner-Baum durchgefallenen Gegner als eigenen Knoten DERSELBEN Spalte (leicht
    versetzt), bevor beide in der naechsten Spalte zum Sieger verschmelzen."""
    lb_matches = [m for m in matches if m.bracket == "LB"]
    groups: list[tuple[str, list]] = []
    for m in lb_matches:
        if groups and groups[-1][0] == m.label:
            groups[-1][1].append(m)
        else:
            groups.append((m.label, [m]))

    first_label, first_matches = groups[0]
    entry_teams = sorted({s for m in first_matches for s in (m.seed_a, m.seed_b)})

    node_x: dict[int, list[float]] = {}
    node_y: dict[int, list[float]] = {}
    node_text: dict[int, list[str]] = {}
    edges: list[tuple[float, float, float, float]] = []

    def add_node(seed, x, y, text):
        node_x.setdefault(seed, []).append(x)
        node_y.setdefault(seed, []).append(y)
        node_text.setdefault(seed, []).append(text)

    col = 0
    y_pos = {s: i * 2 for i, s in enumerate(entry_teams)}
    for s in entry_teams:
        add_node(s, col, y_pos[s], f"Setzplatz {s} - fällt aus dem Gewinner-Baum durch")
    col_labels = {0: "Eintritt"}

    for label, ms in groups:
        is_minor = "minor" in label
        if is_minor:
            col += 1
            winners_y = {}
            for m in ms:
                y = (y_pos[m.seed_a] + y_pos[m.seed_b]) / 2
                edges.append((col - 1, y_pos[m.seed_a], col, y))
                edges.append((col - 1, y_pos[m.seed_b], col, y))
                winners_y[m.winner] = y
                add_node(m.winner, col, y, f"Setzplatz {m.winner} gewinnt {label}")
            y_pos = winners_y
            col_labels[col] = "Minor"
        else:
            for m in ms:
                fresh = m.seed_a if m.seed_a not in y_pos else m.seed_b
                carried = m.seed_b if fresh == m.seed_a else m.seed_a
                y_pos[fresh] = y_pos[carried] + 0.7
                add_node(fresh, col, y_pos[fresh], f"Setzplatz {fresh} - frisch aus dem Gewinner-Baum durchgefallen")
            col += 1
            winners_y = {}
            for m in ms:
                y = (y_pos[m.seed_a] + y_pos[m.seed_b]) / 2
                edges.append((col - 1, y_pos[m.seed_a], col, y))
                edges.append((col - 1, y_pos[m.seed_b], col, y))
                winners_y[m.winner] = y
                add_node(m.winner, col, y, f"Setzplatz {m.winner} gewinnt {label}")
            y_pos = winners_y
            col_labels[col] = "Major"

    fig = go.Figure()
    for (x0, y0, x1, y1) in edges:
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", line=dict(color=GRAY, width=2),
                                  hoverinfo="skip", showlegend=False))
    for seed, xs in node_x.items():
        for x, y, text in zip(xs, node_y[seed], node_text[seed]):
            is_final_champion = x == col and seed == champion
            color = GOLD if is_final_champion else ORANGE
            fig.add_trace(go.Scatter(
                x=[x], y=[y], mode="markers+text", text=[str(seed)],
                textposition="middle center", textfont=dict(color="white", size=10),
                marker=dict(size=22, color=color, line=dict(width=2, color="white")),
                hovertext=text, hoverinfo="text", showlegend=False,
            ))

    tick_x = sorted(col_labels)
    fig.update_xaxes(tickmode="array", tickvals=tick_x, ticktext=[col_labels[x] for x in tick_x])
    fig.update_yaxes(visible=False, autorange="reversed")
    fig.update_layout(template="plotly_white", height=max(320, 28 * len(entry_teams) * 2),
                       margin=dict(l=10, r=10, t=10, b=30))
    return lock_axes(fig)


def build_win_probability_chart(stats: list[ComparisonStats]) -> go.Figure:
    ns = [s.n_seeds for s in stats]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[s.p_favorite_wins_single for s in stats], mode="lines+markers",
                              line=dict(color=GRAY, width=3), name="Einzel-K.-o."))
    fig.add_trace(go.Scatter(x=ns, y=[s.p_favorite_wins_double for s in stats], mode="lines+markers",
                              line=dict(color=GREEN, width=3), name="Doppel-K.-o."))
    fig.update_xaxes(title="Teilnehmerzahl", fixedrange=True, type="log",
                      tickmode="array", tickvals=ns, ticktext=[str(n) for n in ns])
    fig.update_yaxes(title="P(Favorit gewinnt)", fixedrange=True, range=[0, 1.05], tickformat=".0%")
    fig.update_layout(template="plotly_white", height=340, margin=dict(l=10, r=10, t=20, b=10),
                       legend=dict(orientation="h", y=-0.25))
    return lock_axes(fig)


def build_match_count_chart(stats: list[ComparisonStats]) -> go.Figure:
    ns = [s.n_seeds for s in stats]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[s.mean_matches_single for s in stats], mode="lines+markers",
                              line=dict(color=GRAY, width=3), name="Einzel-K.-o."))
    fig.add_trace(go.Scatter(x=ns, y=[s.mean_matches_double for s in stats], mode="lines+markers",
                              line=dict(color=ORANGE, width=3), name="Doppel-K.-o."))
    fig.update_xaxes(title="Teilnehmerzahl", fixedrange=True, type="log",
                      tickmode="array", tickvals=ns, ticktext=[str(n) for n in ns])
    fig.update_yaxes(title="Mittlere Spielanzahl", fixedrange=True, rangemode="tozero")
    fig.update_layout(template="plotly_white", height=340, margin=dict(l=10, r=10, t=20, b=10),
                       legend=dict(orientation="h", y=-0.25))
    return lock_axes(fig)

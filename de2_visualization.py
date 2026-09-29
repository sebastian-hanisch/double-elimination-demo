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


def build_losers_bracket_table(lb_stages: tuple, champion: int) -> go.Figure:
    header = ["Etappe"] + [f"Platz {i+1}" for i in range(max(len(s) for _, s in lb_stages))]
    rows = []
    for label, survivors in lb_stages:
        row = [label] + [str(s) if s != champion else f"{s} 🏆" for s in survivors]
        row += [""] * (len(header) - len(row))
        rows.append(row)
    columns = list(zip(*rows)) if rows else [[]]
    fig = go.Figure(data=[go.Table(
        header=dict(values=header, fill_color="#14233B", font=dict(color="white"), align="center"),
        cells=dict(values=columns, align="center", height=26),
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=min(80 + len(rows) * 30, 500))
    return fig


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

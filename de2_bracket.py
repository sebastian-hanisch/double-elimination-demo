"""Doppel-K.-o.-System: Gewinner-Baum (identische Setzliste wie bracket-seeding-demo) + Verlierer-Baum
(Minor-/Major-Rundenstruktur) + Finale mit Bracket-Reset. Zum Vergleich auch der einfache Einzel-K.-o.
(identisch zu Stueck 2).

Verlierer-Baum-Konstruktion (per WebSearch verifiziert, siehe README): jede Runde des Gewinner-Baums
liefert frische Verlierer, die in den Verlierer-Baum "durchfallen". Jede Verlierer-Baum-Runde ab der
zweiten besteht aus zwei Phasen - Minor (die bisherigen Verlierer-Baum-Teilnehmer spielen gegeneinander)
und Major (die Minor-Sieger spielen gegen die frischen Gewinner-Baum-Verlierer derselben Ebene). Das
verhindert, dass zwei Teams, die gerade erst gegeneinander gespielt haben, sofort wieder aufeinandertreffen.

Bewusste Vereinfachung (siehe README "Wo die Annahmen enden"): die GENAUE Paarung INNERHALB einer Minor-
Runde (wer gegen wen) ist zwischen realen Turnierplattformen nicht einheitlich - hier eine einfache,
wohldefinierte Regel (Reihenfolge der Verlierer-Baum-Liste), keine Behauptung, eine bestimmte Plattform
exakt nachzubilden. Nur Zweierpotenzen als Teilnehmerzahl (kein Freilos-Fall)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from de2_elo import expected_score


def standard_seed_order(size: int) -> list[int]:
    if size < 1 or size & (size - 1) != 0:
        raise ValueError("size muss eine Zweierpotenz sein")
    seeds = [1]
    while len(seeds) < size:
        m = 2 * len(seeds) + 1
        seeds = [x for s in seeds for x in (s, m - s)]
    return seeds


def simulate_match(rating_a: float, rating_b: float, rng: random.Random) -> bool:
    """True, wenn Team A gewinnt (kein Remis)."""
    return rng.random() < expected_score(rating_a, rating_b)


@dataclass(frozen=True)
class Match:
    seed_a: int
    seed_b: int
    winner: int
    bracket: str  # "WB" | "LB" | "GF"
    label: str


@dataclass(frozen=True)
class SingleEliminationResult:
    n_seeds: int
    rounds: tuple[tuple[int, ...], ...]  # rounds[0] = Startbelegung, rounds[-1] = [Sieger]
    matches: tuple[Match, ...]
    champion: int


def simulate_single_elimination(n_seeds: int, ratings: dict, rng: random.Random) -> SingleEliminationResult:
    if n_seeds < 2 or n_seeds & (n_seeds - 1) != 0:
        raise ValueError("n_seeds muss eine Zweierpotenz sein")
    slots = standard_seed_order(n_seeds)
    rounds = [tuple(slots)]
    matches = []
    round_no = 1
    while len(slots) > 1:
        next_slots = []
        for i in range(0, len(slots), 2):
            a, b = slots[i], slots[i + 1]
            a_wins = simulate_match(ratings[a], ratings[b], rng)
            winner = a if a_wins else b
            matches.append(Match(a, b, winner, "WB", f"R{round_no}"))
            next_slots.append(winner)
        slots = next_slots
        rounds.append(tuple(slots))
        round_no += 1
    return SingleEliminationResult(n_seeds=n_seeds, rounds=tuple(rounds), matches=tuple(matches), champion=slots[0])


@dataclass(frozen=True)
class DoubleEliminationResult:
    n_seeds: int
    wb_rounds: tuple[tuple[int, ...], ...]
    lb_stages: tuple[tuple[str, tuple[int, ...]], ...]  # (Label, Ueberlebende) je Verlierer-Baum-Etappe
    matches: tuple[Match, ...]
    champion: int
    n_matches: int
    reset_happened: bool
    losses: dict  # Setzplatz -> Anzahl Niederlagen


def simulate_double_elimination(n_seeds: int, ratings: dict, rng: random.Random) -> DoubleEliminationResult:
    if n_seeds < 4 or n_seeds & (n_seeds - 1) != 0:
        raise ValueError("n_seeds muss eine Zweierpotenz >= 4 sein")
    k = n_seeds.bit_length() - 1
    losses = {s: 0 for s in range(1, n_seeds + 1)}
    matches: list[Match] = []

    def play(a: int, b: int, bracket: str, label: str) -> tuple[int, int]:
        a_wins = simulate_match(ratings[a], ratings[b], rng)
        winner, loser = (a, b) if a_wins else (b, a)
        losses[loser] += 1
        matches.append(Match(a, b, winner, bracket, label))
        return winner, loser

    wb_slots = standard_seed_order(n_seeds)
    wb_rounds = [tuple(wb_slots)]
    lb_stages: list[tuple[str, tuple[int, ...]]] = []

    winners, losers_r1 = [], []
    for i in range(0, len(wb_slots), 2):
        w, l = play(wb_slots[i], wb_slots[i + 1], "WB", "R1")
        winners.append(w)
        losers_r1.append(l)
    wb_rounds.append(tuple(winners))
    wb_current = winners
    lb_current = losers_r1
    lb_stages.append(("Eintritt (WB R1 Verlierer)", tuple(lb_current)))

    for wb_round in range(2, k + 1):
        wb_winners, wb_losers = [], []
        for i in range(0, len(wb_current), 2):
            w, l = play(wb_current[i], wb_current[i + 1], "WB", f"R{wb_round}")
            wb_winners.append(w)
            wb_losers.append(l)
        wb_current = wb_winners
        wb_rounds.append(tuple(wb_current))

        minor_winners = []
        for i in range(0, len(lb_current), 2):
            w, _l = play(lb_current[i], lb_current[i + 1], "LB", f"LB{wb_round-1}-minor")
            minor_winners.append(w)
        if minor_winners:
            lb_stages.append((f"Minor vor Runde {wb_round}", tuple(minor_winners)))

        major_winners = []
        for mw, wl in zip(minor_winners, wb_losers):
            w, _l = play(mw, wl, "LB", f"LB{wb_round-1}-major")
            major_winners.append(w)
        lb_current = major_winners
        lb_stages.append((f"Major nach WB-Runde {wb_round}", tuple(lb_current)))

    wb_champion = wb_current[0]
    lb_champion = lb_current[0]

    winner1, _loser1 = play(wb_champion, lb_champion, "GF", "Finale")
    reset = winner1 != wb_champion
    champion = winner1
    if reset:
        champion, _ = play(wb_champion, lb_champion, "GF", "Finale (Reset)")

    return DoubleEliminationResult(
        n_seeds=n_seeds,
        wb_rounds=tuple(wb_rounds),
        lb_stages=tuple(lb_stages),
        matches=tuple(matches),
        champion=champion,
        n_matches=len(matches),
        reset_happened=reset,
        losses=losses,
    )

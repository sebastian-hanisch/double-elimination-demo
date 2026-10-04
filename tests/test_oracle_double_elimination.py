"""Unabhängiges Orakel für das Doppel-K.-o.: (1) Aufzählung aller Spielausgänge mit eigener, aus der Beschreibung
gebauter Turnierlogik (n = 4, 8) gegen Siegwahrscheinlichkeit, Spielzahl und Reset-Rate der Simulation;
(2) Eigenschaft der Verlierer-Baum-Kreuzung: bis zur vorletzten Stufe trifft in der Major-Phase kein Team auf ein Team,
gegen das es schon gespielt hat (sonst gibt es in der ersten Major-Runde in den meisten Turnieren ein Wiederholungsspiel)."""

import itertools
import math
import random
from collections import defaultdict

import pytest

from de2_bracket import simulate_double_elimination, standard_seed_order


def elo(ra, rb):
    return 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))


def exact_double_elimination(n, ratings):
    """Alle Ausgänge durchgerechnet: (P(Sieger = s), Erwartung Spielzahl, P(Reset)). Major-Phase: Minor-Sieger i gegen den
    WB-Verlierer des Nachbarspiels (i xor 1), sonst wie in der Beschreibung (Minor: benachbarte Verlierer-Baum-Teams)."""
    k = n.bit_length() - 1
    order = standard_seed_order(n)
    champ = defaultdict(float)
    acc = {"matches": 0.0, "reset": 0.0}

    def play_all(pairs, prob, cont, nm):
        for bits in itertools.product((0, 1), repeat=len(pairs)):
            p, w, l = prob, [], []
            for (a, b), bit in zip(pairs, bits):
                e = elo(ratings[a], ratings[b])
                if bit == 0:
                    p *= e
                    w.append(a)
                    l.append(b)
                else:
                    p *= 1.0 - e
                    w.append(b)
                    l.append(a)
            cont(w, l, p, nm + len(pairs))

    def stage(r, wb, lb, p, nm):
        if r > k:
            a, b = wb[0], lb[0]
            e = elo(ratings[a], ratings[b])
            champ[a] += p * e
            acc["matches"] += p * e * (nm + 1)
            q = p * (1.0 - e)
            champ[a] += q * e
            champ[b] += q * (1.0 - e)
            acc["matches"] += q * (nm + 2)
            acc["reset"] += q
            return

        def after_wb(w, l, p2, nm2):
            def after_minor(mw, _ml, p3, nm3):
                crossed = [l[i ^ 1] for i in range(len(l))] if len(l) > 1 else l
                play_all(list(zip(mw, crossed)), p3, lambda w4, _l4, p4, nm4: stage(r + 1, w, w4, p4, nm4), nm3)

            play_all([(lb[i], lb[i + 1]) for i in range(0, len(lb), 2)], p2, after_minor, nm2)

        play_all([(wb[i], wb[i + 1]) for i in range(0, len(wb), 2)], p, after_wb, nm)

    play_all([(order[i], order[i + 1]) for i in range(0, n, 2)], 1.0, lambda w, l, p, nm: stage(2, w, l, p, nm), 0)
    return dict(champ), acc["matches"], acc["reset"]


def test_oracle_hand_example_four_teams_equal_strength():
    ratings = {s: 1500.0 for s in range(1, 5)}
    champ, matches, reset = exact_double_elimination(4, ratings)
    assert all(abs(champ[s] - 0.25) < 1e-12 for s in range(1, 5))
    assert abs(reset - 0.5) < 1e-12 and abs(matches - 6.5) < 1e-12        # 2n - 2 = 6 Spiele, in der Hälfte der Fälle ein Reset-Spiel dazu


@pytest.mark.parametrize("n, edge", [(4, 500), (4, 0), (8, 500), (8, 200), (8, 0)])
def test_simulation_matches_exhaustive_enumeration(n, edge):
    ratings = {s: 1500.0 for s in range(1, n + 1)}
    ratings[1] += edge
    champ, exp_matches, exp_reset = exact_double_elimination(n, ratings)
    assert abs(sum(champ.values()) - 1.0) < 1e-9
    reps = 12000
    wins = matches = resets = 0
    for i in range(reps):
        res = simulate_double_elimination(n, ratings, random.Random(90000 + i))
        wins += res.champion == 1
        matches += res.n_matches
        resets += res.reset_happened
    p = champ[1]
    assert abs(wins / reps - p) < 4.5 * math.sqrt(p * (1 - p) / reps)
    assert abs(resets / reps - exp_reset) < 4.5 * math.sqrt(exp_reset * (1 - exp_reset) / reps) + 1e-9
    assert abs(matches / reps - exp_matches) < 0.05


@pytest.mark.parametrize("n", [8, 16, 32])
def test_no_immediate_rematch_in_major_rounds_before_the_last_stage(n):
    """Ein Team, das aus dem Gewinner-Baum fällt, darf in der Major-Phase nicht auf ein Team treffen, gegen das es in diesem
    Turnier schon gespielt hat - bis auf die letzte Stufe (WB-Finalverlierer gegen den Verlierer-Baum-Rest), wo es möglich bleibt."""
    k = n.bit_length() - 1
    ratings = {s: 1500.0 for s in range(1, n + 1)}
    for i in range(300):
        res = simulate_double_elimination(n, ratings, random.Random(i))
        seen = set()
        for m in res.matches:
            key = frozenset((m.seed_a, m.seed_b))
            if m.bracket == "LB" and m.label.endswith("-major") and int(m.label[2:].split("-")[0]) <= k - 2:
                assert key not in seen, (i, m)
            seen.add(key)

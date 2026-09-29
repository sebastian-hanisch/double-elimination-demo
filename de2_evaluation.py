"""Kennzahlen: Sieg-Wahrscheinlichkeit des staerksten Teams und Spielanzahl, Einzel- vs. Doppel-K.-o."""

from __future__ import annotations

import random
from dataclasses import dataclass

from de2_bracket import simulate_double_elimination, simulate_single_elimination


def ratings_with_favorite(n_seeds: int, favorite_edge: float = 500.0) -> dict:
    ratings = {s: 1500.0 for s in range(1, n_seeds + 1)}
    ratings[1] = 1500.0 + favorite_edge
    return ratings


@dataclass(frozen=True)
class ComparisonStats:
    n_seeds: int
    n_reps: int
    p_favorite_wins_single: float
    p_favorite_wins_double: float
    mean_matches_single: float
    mean_matches_double: float
    reset_rate: float


def compare_single_vs_double(n_seeds: int, n_reps: int, favorite_edge: float = 500.0, seed_offset: int = 0) -> ComparisonStats:
    ratings = ratings_with_favorite(n_seeds, favorite_edge)
    wins_single = wins_double = 0
    matches_single = matches_double = 0
    resets = 0
    for i in range(n_reps):
        rng_s = random.Random(seed_offset + 1000 + i)
        res_s = simulate_single_elimination(n_seeds, ratings, rng_s)
        wins_single += res_s.champion == 1
        matches_single += len(res_s.matches)

        rng_d = random.Random(seed_offset + 2000 + i)
        res_d = simulate_double_elimination(n_seeds, ratings, rng_d)
        wins_double += res_d.champion == 1
        matches_double += res_d.n_matches
        resets += res_d.reset_happened

    return ComparisonStats(
        n_seeds=n_seeds,
        n_reps=n_reps,
        p_favorite_wins_single=wins_single / n_reps,
        p_favorite_wins_double=wins_double / n_reps,
        mean_matches_single=matches_single / n_reps,
        mean_matches_double=matches_double / n_reps,
        reset_rate=resets / n_reps,
    )


def sweep_comparison(n_seeds_values: list[int], n_reps: int, favorite_edge: float = 500.0, seed_offset: int = 0):
    return [compare_single_vs_double(n, n_reps, favorite_edge=favorite_edge, seed_offset=seed_offset) for n in n_seeds_values]

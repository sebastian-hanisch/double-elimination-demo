"""Vergleich Einzel- vs. Doppel-K.-o.: Sieg-Wahrscheinlichkeit und Spielanzahl."""

import pytest

from de2_evaluation import compare_single_vs_double, ratings_with_favorite, sweep_comparison


def test_ratings_with_favorite_only_raises_seed_one():
    ratings = ratings_with_favorite(8, favorite_edge=300)
    assert ratings[1] == 1800.0
    assert all(ratings[s] == 1500.0 for s in range(2, 9))


@pytest.mark.parametrize("n", [4, 8, 16])
def test_double_elimination_favors_the_favorite_more_than_single(n):
    stats = compare_single_vs_double(n, n_reps=800, favorite_edge=500)
    assert stats.p_favorite_wins_double > stats.p_favorite_wins_single


@pytest.mark.parametrize("n", [4, 8, 16])
def test_double_elimination_needs_roughly_twice_the_matches(n):
    stats = compare_single_vs_double(n, n_reps=500, favorite_edge=500)
    assert stats.mean_matches_double > stats.mean_matches_single * 1.8
    assert stats.mean_matches_double < stats.mean_matches_single * 2.2


def test_no_favorite_edge_shrinks_the_double_elimination_advantage():
    with_edge = compare_single_vs_double(8, n_reps=1500, favorite_edge=500)
    no_edge = compare_single_vs_double(8, n_reps=1500, favorite_edge=0)
    gap_with_edge = with_edge.p_favorite_wins_double - with_edge.p_favorite_wins_single
    gap_no_edge = no_edge.p_favorite_wins_double - no_edge.p_favorite_wins_single
    assert gap_with_edge > gap_no_edge


def test_sweep_comparison_returns_one_entry_per_n():
    results = sweep_comparison([4, 8], n_reps=300)
    assert [s.n_seeds for s in results] == [4, 8]

"""Setzliste, Einzel-K.-o. und Doppel-K.-o.-Struktur (Minor-/Major-Verlierer-Baum, Bracket-Reset)."""

import random

import pytest

from de2_bracket import simulate_double_elimination, simulate_single_elimination, standard_seed_order


def test_standard_seed_order_matches_known_16_table():
    assert standard_seed_order(16) == [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]


def test_standard_seed_order_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        standard_seed_order(6)


@pytest.mark.parametrize("n", [4, 8, 16, 32])
def test_single_elimination_produces_n_minus_1_matches(n):
    ratings = {s: 1500.0 for s in range(1, n + 1)}
    result = simulate_single_elimination(n, ratings, random.Random(1))
    assert len(result.matches) == n - 1
    assert result.rounds[-1] == (result.champion,)


@pytest.mark.parametrize("n", [4, 8, 16, 32])
def test_double_elimination_every_eliminated_team_has_exactly_two_losses(n):
    ratings = {s: 1500.0 for s in range(1, n + 1)}
    result = simulate_double_elimination(n, ratings, random.Random(2))
    for team, losses in result.losses.items():
        if team == result.champion:
            assert losses <= 1
        else:
            assert losses == 2


@pytest.mark.parametrize("n", [4, 8, 16, 32])
def test_double_elimination_match_count_matches_formula(n):
    ratings = {s: 1500.0 for s in range(1, n + 1)}
    result = simulate_double_elimination(n, ratings, random.Random(3))
    expected = 2 * n - 1 if result.reset_happened else 2 * n - 2
    assert result.n_matches == expected


def test_double_elimination_rejects_non_power_of_two():
    ratings = {s: 1500.0 for s in range(1, 7)}
    with pytest.raises(ValueError):
        simulate_double_elimination(6, ratings, random.Random(1))


def test_double_elimination_rejects_too_small_field():
    ratings = {s: 1500.0 for s in range(1, 3)}
    with pytest.raises(ValueError):
        simulate_double_elimination(2, ratings, random.Random(1))


def test_bracket_reset_requires_loser_bracket_finalist_to_beat_champion_twice():
    """Findet einen konkreten Seed mit Reset und prueft, dass GENAU 2 Finalspiele geloggt sind."""
    ratings = {s: 1500.0 for s in range(1, 33)}
    ratings[1] = 2000.0
    result = simulate_double_elimination(32, ratings, random.Random(1))
    gf_matches = [m for m in result.matches if m.bracket == "GF"]
    assert result.reset_happened
    assert len(gf_matches) == 2


def test_no_reset_means_exactly_one_grand_final_match():
    ratings = {s: 1500.0 for s in range(1, 9)}
    ratings[1] = 2000.0
    result = simulate_double_elimination(8, ratings, random.Random(1))
    gf_matches = [m for m in result.matches if m.bracket == "GF"]
    assert not result.reset_happened
    assert len(gf_matches) == 1


def test_strong_favorite_almost_always_wins_double_elimination():
    ratings = {s: 1500.0 for s in range(1, 9)}
    ratings[1] = 2400.0  # extrem ueberlegen
    wins = 0
    for trial in range(200):
        result = simulate_double_elimination(8, ratings, random.Random(trial))
        wins += result.champion == 1
    assert wins > 190

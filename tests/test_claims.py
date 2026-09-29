"""Regressionstests gegen die konkreten Zahlen aus README.md - reine Python-Simulation, deterministisch
bei festem Seed, daher enge Toleranzen zulaessig."""

import pytest

from de2_evaluation import compare_single_vs_double


@pytest.mark.parametrize(
    "n, p_single, p_double, m_single, m_double",
    [
        (8, 0.855, 0.965, 7.0, 14.19),
        (16, 0.805, 0.948, 15.0, 30.21),
        (32, 0.758, 0.932, 31.0, 62.23),
    ],
)
def test_readme_numbers(n, p_single, p_double, m_single, m_double):
    stats = compare_single_vs_double(n, n_reps=3000, favorite_edge=500)
    assert stats.p_favorite_wins_single == pytest.approx(p_single, abs=0.01)
    assert stats.p_favorite_wins_double == pytest.approx(p_double, abs=0.01)
    assert stats.mean_matches_single == pytest.approx(m_single, abs=0.01)
    assert stats.mean_matches_double == pytest.approx(m_double, abs=0.05)


def test_readme_double_elimination_roughly_doubles_matches_at_n16():
    stats = compare_single_vs_double(16, n_reps=3000, favorite_edge=500)
    ratio = stats.mean_matches_double / stats.mean_matches_single
    assert 1.9 < ratio < 2.1

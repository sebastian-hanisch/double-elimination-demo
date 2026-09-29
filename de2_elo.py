"""Elo-Erwartungswert-Formel (Arpad Elo, USCF/FIDE-Standard) - identischer Mechanismus wie
bracket-seeding-demo (bs_elo.py), hier ohne Cross-Repo-Import selbststaendig portiert."""

from __future__ import annotations


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))

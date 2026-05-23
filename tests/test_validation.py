from __future__ import annotations

import pytest

from app.opsmind.analyzer import build_validation


@pytest.mark.parametrize(
    "category",
    ["compute", "kubernetes", "database", "networking", "storage", "security", "application"],
)
def test_build_validation_all_categories(category: str) -> None:
    checks = build_validation(category)

    assert checks
    assert all(isinstance(check, str) and check for check in checks)


def test_build_validation_unknown_category() -> None:
    checks = build_validation("unknown")

    assert "Alert clears." in checks

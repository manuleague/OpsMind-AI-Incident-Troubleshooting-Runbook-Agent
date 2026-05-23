from __future__ import annotations

import pytest

from app.opsmind.analyzer import classify_incident


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("Linux VM CPU spike above 95 percent", "compute"),
        ("Kubernetes pod crashloopbackoff after image rollout", "kubernetes"),
        ("SQL database connection pool exhausted and deadlocks increasing", "database"),
        ("DNS resolution failure returns NXDOMAIN for private hostname", "networking"),
        ("Disk filesystem full and inode quota exhausted", "storage"),
        ("TLS certificate expired on production gateway", "security"),
        ("HTTP 502 bad gateway after application deployment", "application"),
        ("Unrecognized alert with no useful technical signal", "unknown"),
    ],
)
def test_classify_incident_all_categories(description: str, expected: str) -> None:
    assert classify_incident(description, []) == expected

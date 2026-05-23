from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.opsmind.analyzer import IncidentAnalyzer
from app.opsmind.config import load_settings
from app.opsmind.formatter import to_markdown
from app.opsmind.models import IncidentInput


PRESET_INCIDENTS: list[IncidentInput] = [
    IncidentInput(
        description="Linux VM CPU spike above 95 percent for 10 minutes with degraded application latency",
        severity="sev2",
        environment="production",
    ),
    IncidentInput(
        description="Kubernetes pod crashloopbackoff after image rollout in checkout namespace",
        severity="sev1",
        environment="production",
    ),
    IncidentInput(
        description="SQL database connection pool exhausted with deadlocks and slow queries",
        severity="sev2",
        environment="production",
    ),
    IncidentInput(
        description="DNS resolution failure returning NXDOMAIN for api.internal in one region",
        severity="sev2",
        environment="production",
    ),
    IncidentInput(
        description="TLS certificate expired on public gateway causing client failures",
        severity="sev1",
        environment="production",
    ),
]


def main() -> None:
    analyzer = IncidentAnalyzer(load_settings())
    for index, incident in enumerate(PRESET_INCIDENTS, start=1):
        print(f"\n{'=' * 80}")
        print(f"DEMO INCIDENT {index}: {incident.description}")
        print(f"{'=' * 80}\n")
        response = analyzer.analyze(incident)
        print(to_markdown(response))


if __name__ == "__main__":
    main()

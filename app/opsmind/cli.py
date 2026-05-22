from __future__ import annotations

import argparse

from app.opsmind.analyzer import IncidentAnalyzer
from app.opsmind.formatter import to_markdown
from app.opsmind.models import IncidentInput


def main() -> None:
    parser = argparse.ArgumentParser(description="OpsMind AI incident troubleshooting demo.")
    parser.add_argument("description", help="Incident description or alert text.")
    parser.add_argument("--severity", default="unknown", help="Example: low, medium, high, critical, sev1.")
    parser.add_argument("--environment", default="unknown", help="Example: prod, staging, dev.")
    args = parser.parse_args()

    analyzer = IncidentAnalyzer()
    response = analyzer.analyze(
        IncidentInput(
            description=args.description,
            severity=args.severity,
            environment=args.environment,
        )
    )
    print(to_markdown(response))


if __name__ == "__main__":
    main()


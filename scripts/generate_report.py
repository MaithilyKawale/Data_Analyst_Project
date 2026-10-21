"""Generate reproducible local report files from the source CSV."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.analytics import deterministic_insights, prepare_data
from src.data_quality import run_quality_checks

def main() -> None:
    source = ROOT / "customer_shopping_behavior.csv"
    if not source.exists():
        raise FileNotFoundError(f"Expected source dataset at {source}")
    data = prepare_data(pd.read_csv(source))
    out = ROOT / "reports" / "generated"
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    quality = run_quality_checks(data)
    quality.to_csv(out / f"data_quality_{stamp}.csv", index=False)
    rows = [{"metric": "record_count", "value": len(data)}]
    if "purchase_amount" in data:
        rows.extend([{"metric": "total_purchase_amount", "value": data["purchase_amount"].sum()},
                     {"metric": "average_purchase_amount", "value": data["purchase_amount"].mean()}])
    pd.DataFrame(rows).to_csv(out / f"summary_{stamp}.csv", index=False)
    report = "# Customer Shopping Analysis Snapshot\n\nGenerated (UTC): " + stamp + "\n\n"
    report += "\n".join("- " + item for item in deterministic_insights(data))
    report += "\n\n## Data quality\n\n" + quality.to_string(index=False)
    report += "\n\n## Interpretation\n\nThis is a snapshot, not a time-series comparison. Results are descriptive and do not establish causality.\n"
    (out / f"report_{stamp}.md").write_text(report, encoding="utf-8")
    print(f"Report artifacts written to {out}")

if __name__ == "__main__":
    main()

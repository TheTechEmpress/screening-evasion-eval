"""
analyse_results.py

Reads raw detection results and computes detection rates per technique.
Produces a summary CSV and a bar chart.

Input:  results/raw_detections.csv
Output: results/detection_rates.csv
        results/detection_rates.png
        results/failure_modes.md
"""

import os
import csv
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RESULTS_DIR = "results"
RAW_RESULTS = os.path.join(RESULTS_DIR, "raw_detections.csv")
SUMMARY_CSV = os.path.join(RESULTS_DIR, "detection_rates.csv")
PLOT_PNG = os.path.join(RESULTS_DIR, "detection_rates.png")
FAILURE_MD = os.path.join(RESULTS_DIR, "failure_modes.md")

TECHNIQUE_ORDER = ["original", "substituted", "fragmented", "padded", "revcomp"]


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def load_raw(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "sequence_id": row["sequence_id"],
                "technique": row["technique"],
                "detected": int(row["detected"]),
            })
    return rows


def compute_rates(rows):
    counts = defaultdict(lambda: {"total": 0, "detected": 0})
    for row in rows:
        counts[row["technique"]]["total"] += 1
        counts[row["technique"]]["detected"] += row["detected"]

    rates = {}
    for technique, c in counts.items():
        rates[technique] = {
            "total": c["total"],
            "detected": c["detected"],
            "detection_rate": c["detected"] / c["total"] if c["total"] else 0.0,
        }
    return rates


def write_summary(rates):
    ordered = [t for t in TECHNIQUE_ORDER if t in rates]
    ordered += [t for t in rates if t not in ordered]

    with open(SUMMARY_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["technique", "total", "detected", "detection_rate"])
        for t in ordered:
            r = rates[t]
            writer.writerow([t, r["total"], r["detected"], f"{r['detection_rate']:.3f}"])
    print(f"Wrote summary to {SUMMARY_CSV}")
    return ordered


def plot_rates(rates, ordered):
    labels = ordered
    values = [rates[t]["detection_rate"] * 100 for t in labels]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color="#2E86AB")
    plt.ylabel("Detection rate (%)")
    plt.title("Screening detection rate by evasion technique")
    plt.ylim(0, 105)
    for bar, v in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, v + 2,
                 f"{v:.0f}%", ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    plt.savefig(PLOT_PNG, dpi=150)
    print(f"Wrote plot to {PLOT_PNG}")


def write_failure_notes(rates, ordered):
    lines = ["# Failure Modes Observed\n"]
    for t in ordered:
        r = rates[t]
        lines.append(
            f"- **{t}**: detection rate {r['detection_rate']*100:.0f}% "
            f"({r['detected']}/{r['total']} sequences detected)"
        )
    lines.append("")
    lines.append(
        "Review each technique and note where the screening baseline failed. "
        "Add qualitative observations here after inspecting the raw data."
    )
    with open(FAILURE_MD, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote failure notes to {FAILURE_MD}")


def main():
    if not os.path.exists(RAW_RESULTS):
        raise FileNotFoundError(f"Missing raw results: {RAW_RESULTS}")

    rows = load_raw(RAW_RESULTS)
    rates = compute_rates(rows)
    ordered = write_summary(rates)
    plot_rates(rates, ordered)
    write_failure_notes(rates, ordered)

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()

"""
run_screening.py

Runs a simple k-mer based screening function against reference and
obfuscated sequences and records detection results.

The screening function is a local, transparent baseline (k-mer exact
matching). It is NOT a commercial provider tool. It is intended as a
representative baseline for evaluating robustness to evasion.

Input:  data/reference_sequences/test_sequences.fasta
        data/obfuscated_sequences/*.fasta
Output: results/raw_detections.csv
"""

import os
import csv
from Bio import SeqIO

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REFERENCE_FILE = "data/reference_sequences/test_sequences.fasta"
OBFUSCATED_DIR = "data/obfuscated_sequences"
RESULTS_DIR = "results"
RAW_RESULTS = os.path.join(RESULTS_DIR, "raw_detections.csv")

KMER_SIZE = 20          # length of k-mer to match
MIN_MATCHES = 1         # minimum number of matching k-mers to flag


# ---------------------------------------------------------------------------
# Screening baseline
# ---------------------------------------------------------------------------

def build_kmer_index(reference_sequences):
    """Build a set of k-mers from all reference sequences."""
    kmers = set()
    for seq in reference_sequences:
        seq = seq.upper()
        for i in range(len(seq) - KMER_SIZE + 1):
            kmers.add(seq[i:i + KMER_SIZE])
    return kmers


def screen(sequence: str, kmer_index: set) -> bool:
    """
    Return True if the sequence shares at least MIN_MATCHES k-mers
    with the reference index.
    """
    seq = sequence.upper().replace("N", "")
    matches = 0
    for i in range(len(seq) - KMER_SIZE + 1):
        if seq[i:i + KMER_SIZE] in kmer_index:
            matches += 1
            if matches >= MIN_MATCHES:
                return True
    return False


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def load_sequences(path):
    return [str(r.seq) for r in SeqIO.parse(path, "fasta")]


def main():
    if not os.path.exists(REFERENCE_FILE):
        raise FileNotFoundError(f"Missing reference file: {REFERENCE_FILE}")

    print("Loading reference sequences...")
    reference = load_sequences(REFERENCE_FILE)
    kmer_index = build_kmer_index(reference)
    print(f"Built k-mer index with {len(kmer_index)} unique {KMER_SIZE}-mers.")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    rows = []

    # 1. Original sequences (control)
    for i, seq in enumerate(reference):
        detected = screen(seq, kmer_index)
        rows.append({
            "sequence_id": f"reference_{i}",
            "technique": "original",
            "detected": int(detected),
        })

    # 2. Obfuscated sequences
    if not os.path.isdir(OBFUSCATED_DIR):
        raise FileNotFoundError(f"Missing obfuscated dir: {OBFUSCATED_DIR}")

    for fname in sorted(os.listdir(OBFUSCATED_DIR)):
        if not fname.endswith(".fasta"):
            continue
        technique = fname.replace(".fasta", "")
        path = os.path.join(OBFUSCATED_DIR, fname)
        for rec in SeqIO.parse(path, "fasta"):
            detected = screen(str(rec.seq), kmer_index)
            rows.append({
                "sequence_id": rec.id,
                "technique": technique,
                "detected": int(detected),
            })

    # 3. Write raw results
    with open(RAW_RESULTS, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["sequence_id", "technique", "detected"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {RAW_RESULTS}")


if __name__ == "__main__":
    main()

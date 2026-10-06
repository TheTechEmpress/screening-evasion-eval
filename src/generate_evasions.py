"""
generate_evasions.py

Generates obfuscated variants of reference DNA sequences for
adversarial evaluation of sequence-based screening tools.

Techniques implemented:
  - Substitution:        replace some bases with alternative bases
  - Fragmentation:       split sequence into fragments
  - Padding:             add random flanking sequence
  - Reverse-complement:  reverse complement the sequence

Input:  data/reference_sequences/test_sequences.fasta
Output: data/obfuscated_sequences/*.fasta
"""

import os
import random
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REFERENCE_FILE = "data/reference_sequences/test_sequences.fasta"
OUTPUT_DIR = "data/obfuscated_sequences"

# Reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Parameters for each technique
SUBSTITUTION_RATE = 0.10      # fraction of bases substituted
FRAGMENT_COUNT = 3            # number of fragments per sequence
PADDING_LENGTH = 50           # bases of random padding per side

BASES = ["A", "T", "G", "C"]


# ---------------------------------------------------------------------------
# Techniques
# ---------------------------------------------------------------------------

def substitute(seq: str, rate: float = SUBSTITUTION_RATE) -> str:
    """Replace a fraction of bases with random alternative bases."""
    seq_list = list(seq)
    for i in range(len(seq_list)):
        if random.random() < rate:
            current = seq_list[i]
            alternatives = [b for b in BASES if b != current]
            seq_list[i] = random.choice(alternatives)
    return "".join(seq_list)


def fragment(seq: str, n: int = FRAGMENT_COUNT) -> str:
    """
    Split sequence into n fragments and rejoin with gaps.
    Fragments are separated by Ns to simulate piecewise orders.
    """
    if n <= 1 or len(seq) < n:
        return seq
    size = len(seq) // n
    parts = [seq[i * size:(i + 1) * size] for i in range(n)]
    # Include remainder
    if n * size < len(seq):
        parts[-1] += seq[n * size:]
    return "N" * 10 + ("N" * 10).join(parts) + "N" * 10


def pad(seq: str, length: int = PADDING_LENGTH) -> str:
    """Add random flanking sequence on both sides."""
    left = "".join(random.choice(BASES) for _ in range(length))
    right = "".join(random.choice(BASES) for _ in range(length))
    return left + seq + right


def reverse_complement(seq: str) -> str:
    """Return the reverse complement of the sequence."""
    return str(Seq(seq).reverse_complement())


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

TECHNIQUES = {
    "substituted": substitute,
    "fragmented": fragment,
    "padded": pad,
    "revcomp": reverse_complement,
}


def load_reference(path: str):
    """Load reference sequences from a FASTA file."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Reference file not found: {path}\n"
            f"Create it and add at least one DNA sequence."
        )
    return list(SeqIO.parse(path, "fasta"))


def write_obfuscated(records, technique_name: str, transform):
    """Apply a transform to each record and write to a FASTA file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{technique_name}.fasta")
    out_records = []
    for rec in records:
        new_seq = transform(str(rec.seq).upper())
        out_records.append(
            SeqRecord(
                Seq(new_seq),
                id=f"{rec.id}_{technique_name}",
                description=f"{technique_name} variant of {rec.id}",
            )
        )
    SeqIO.write(out_records, out_path, "fasta")
    print(f"Wrote {len(out_records)} sequences to {out_path}")


def main():
    print("Loading reference sequences...")
    records = load_reference(REFERENCE_FILE)
    print(f"Loaded {len(records)} reference sequence(s).")

    for name, transform in TECHNIQUES.items():
        print(f"\nApplying technique: {name}")
        write_obfuscated(records, name, transform)

    print("\nDone. Obfuscated sequences written to", OUTPUT_DIR)


if __name__ == "__main__":
    main()

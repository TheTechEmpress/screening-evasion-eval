# Adversarial Evaluation of Nucleic Acid Synthesis Screening Tools

A reproducible evaluation of how well publicly available sequence-based screening tools detect obfuscated and evasive DNA sequences.

## Why this matters

Nucleic acid synthesis screening is a computational problem: sequence matching, anomaly detection, and deployment at the point of order. Current screening tools are validated against known sequences but rarely against adversarial evasion. This project measures that gap and documents where screening breaks down.

## What this project does

- Selects a publicly accessible screening or sequence-matching tool
- Constructs a test suite of realistic evasion techniques
- Measures detection sensitivity against original versus obfuscated sequences
- Documents failure modes and the conditions under which screening fails

## Evasion techniques tested

| Technique | Description |
|---|---|
| Nucleotide substitution | Silent or conservative substitutions that alter sequence but preserve function |
| Sequence fragmentation | Splitting a sequence into segments that individually pass screening |
| Sequence padding | Adding irrelevant flanking sequence to dilute signal |
| Reverse-complement variants | Reordering that preserves biological function but evades naive matching |

## Key findings

*[Fill in after running the evaluation. Even preliminary results are valuable.]*

## Repository structure

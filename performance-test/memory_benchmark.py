"""Exercise the anonymization hot path with distinct, synthetic input."""

import argparse
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.anonymizer_logic import NLP_ENGINE, anonymize_text_with_presidio


def snapshot(requests: int, started: float) -> None:
    nlp = NLP_ENGINE.nlp["it"]
    rss_kib = int(subprocess.check_output(
        ["ps", "-o", "rss=", "-p", str(os.getpid())], text=True
    ).strip())
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_divisor = 1024**2 if sys.platform == "darwin" else 1024
    print(json.dumps({
        "requests": requests,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "rss_mib": round(rss_kib / 1024, 2),
        "peak_rss_mib": round(peak_rss / peak_divisor, 2),
        # spaCy's length counter also counts lexemes already freed by a zone.
        "live_lexemes": sum(1 for _ in nlp.vocab),
        "strings": len(nlp.vocab.strings),
    }), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", type=int, default=30000)
    parser.add_argument("--interval", type=int, default=5000)
    args = parser.parse_args()
    if args.requests < 1 or args.interval < 1:
        parser.error("--requests and --interval must be positive")

    anonymize_text_with_presidio("Pagamento per Mario Rossi")
    started = time.perf_counter()
    snapshot(0, started)
    for index in range(1, args.requests + 1):
        references = " ".join(
            f"riferimento{field}{index:012x}" for field in range(10)
        )
        anonymize_text_with_presidio(f"Pagamento per Mario Rossi {references}")
        if index % args.interval == 0 or index == args.requests:
            snapshot(index, started)


if __name__ == "__main__":
    main()

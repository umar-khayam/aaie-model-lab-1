import argparse
import json
from pathlib import Path
import sys


FILE_PATH = Path(__file__).resolve()

REPO_ROOT = None
for parent in FILE_PATH.parents:
    if (parent / "revision_chain_analysis").exists():
        REPO_ROOT = parent
        break

if REPO_ROOT is None:
    REPO_ROOT = FILE_PATH.parents[3]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from revision_chain_analysis.student_profiling.patterns.pattern_classifier import (
    classify_ai_use_pattern,
)

DEFAULT_SAMPLES_DIR = (
    REPO_ROOT
    / "revision_chain_analysis"
    / "student_profiling"
    / "patterns"
    / "pattern_samples"
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT
    / "revision_chain_analysis"
    / "student_profiling"
    / "patterns"
    / "pattern_outputs"
)


def main():
    parser = argparse.ArgumentParser(
        description="Run pattern classifier on pattern sample JSON files."
    )

    parser.add_argument(
        "--input-dir",
        required=False,
        type=str,
        default=None,
        help=(
            "Directory with pattern sample JSON files "
            "(defaults to student_profiling/patterns/pattern_samples)"
        ),
    )

    parser.add_argument(
        "--output-dir",
        required=False,
        type=str,
        default=None,
        help=(
            "Directory to save pattern outputs "
            "(defaults to student_profiling/patterns/pattern_outputs)"
        ),
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir).resolve() if args.input_dir else DEFAULT_SAMPLES_DIR
    output_dir = (
        Path(args.output_dir).resolve() if args.output_dir else DEFAULT_OUTPUT_DIR
    )

    if not input_dir.exists():
        print(f"[ERROR] Input directory not found: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(input_dir.glob("*.json"))
    if not json_files:
        print(f"[WARN] No JSON files found in {input_dir}")
        return

    summary = []
    for path in json_files:
        with path.open("r", encoding="utf-8") as f:
            sample = json.load(f)

        prompt_distribution = sample.get("prompt_distribution", {})
        ps_indicators = sample.get("ps_indicators", {})
        ct_indicators = sample.get("ct_indicators", {})

        predicted = classify_ai_use_pattern(
            prompt_distribution, ps_indicators, ct_indicators
        )
        expected = sample.get("expected_pattern")

        output = {
            "prompt_distribution": prompt_distribution,
            "ps_indicators": ps_indicators,
            "ct_indicators": ct_indicators,
            "predicted_pattern": predicted,
        }
        if expected is not None:
            output["expected_pattern"] = expected
            output["is_match"] = predicted == expected

        out_file = output_dir / f"pattern_sample_{path.stem}.json"
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        summary.append((path.name, predicted, expected))

    print("[OK] Pattern samples processed:")
    for name, predicted, expected in summary:
        if expected is None:
            print(f"  - {name}: predicted={predicted}")
        else:
            status = "OK" if predicted == expected else "MISMATCH"
            print(
                f"  - {name}: predicted={predicted}, expected={expected} [{status}]"
            )


if __name__ == "__main__":
    main()

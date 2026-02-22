import argparse
import json
from pathlib import Path

from revision_chain_analysis.student_profiling.prompt_classifier.prompt_classifier import (
    run_prompt_type_classification,
)

from revision_chain_analysis.student_profiling.tools.rclog_to_turns import (
    load_rclog,
    rclog_to_turns,
)


def main():
    parser = argparse.ArgumentParser(
        description="Run prompt type classifier on an rc_log_v1 JSON file."
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="Path to rc_log JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save classified_turns and distribution JSON (optional)",
    )
    args = parser.parse_args()

    input_path = Path(args.input_path).resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # 1) Load rc_log
    rclog = load_rclog(input_path)

    # 2) Convert revision_chain to unified turns
    turns = rclog_to_turns(rclog)

    # 3) Run prompt type classification
    classified_turns, distribution = run_prompt_type_classification(turns)

    # 4) Print a quick summary
    print(f"\nProcessed rc_log: {input_path.name}")
    print(f"rc_log_id: {rclog.get('rc_log_id', 'N/A')}")
    print(f"rubric_id: {rclog.get('rubric_id', 'N/A')}")
    print("\nPrompt type distribution:")
    for k, v in distribution.items():
        print(f"  {k}: {v}")

    # 5) Optionally save outputs for inspection
    if args.output_dir:
        out_dir = Path(args.output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        stem = input_path.stem

        classified_path = out_dir / f"{stem}_classified_turns.json"
        dist_path = out_dir / f"{stem}_prompt_distribution.json"

        with classified_path.open("w", encoding="utf-8") as f:
            json.dump(classified_turns, f, indent=2, ensure_ascii=False)

        with dist_path.open("w", encoding="utf-8") as f:
            json.dump(distribution, f, indent=2, ensure_ascii=False)

        print(f"\nSaved classified turns to: {classified_path}")
        print(f"Saved distribution to:     {dist_path}")


if __name__ == "__main__":
    main()

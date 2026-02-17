import argparse
import json
from pathlib import Path
import sys


FILE_PATH = Path(__file__).resolve()
REPO_ROOT = FILE_PATH.parents[4]
PKG_ROOT = FILE_PATH.parents[2]  # student_profiling

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from revision_chain_analysis.student_profiling.tools.rclog_to_turns import (
    load_rclog,
    rclog_to_turns,
)
from revision_chain_analysis.student_profiling.indicators.critical_thinking import (
    compute_ct_indicators_and_evidence,
)


def main():
    parser = argparse.ArgumentParser(
        description="Run Critical Thinking indicator extraction on a rc_log JSON file."
    )

    parser.add_argument(
        "--input",
        required=True,
        type=str,
        help="Path to rc_log JSON file",
    )

    parser.add_argument(
        "--output-dir",
        required=False,
        type=str,
        default=None,
        help="Directory to save CT sample output JSON "
             "(defaults to revision_chain_analysis/student_profiling/indicators/CT_sample)",
    )

    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = PKG_ROOT / "student_profiling" / "indicators" / "CT_sample"

    output_dir.mkdir(parents=True, exist_ok=True)

    rclog = load_rclog(input_path)
    turns = rclog_to_turns(rclog)

    counts, evidence = compute_ct_indicators_and_evidence(turns)
    out_file = output_dir / f"ct_sample_{input_path.stem}.json"
    output = {"counts": counts, "evidence": evidence}

    with out_file.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"[OK] CT sample written to: {out_file}")


if __name__ == "__main__":
    main()

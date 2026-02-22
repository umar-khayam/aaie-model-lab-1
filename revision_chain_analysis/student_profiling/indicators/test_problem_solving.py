import json
from pathlib import Path

from problem_solving import compute_PS_indicators_and_evidence

BASE_DIR = Path(__file__).parent
SAMPLES_DIR = BASE_DIR / "PS_sample"


def load_sample(filename: str):
    """Load a JSON sample file and return its turns."""
    path = SAMPLES_DIR / filename
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("turns", [])


def run_sample(name: str, filename: str):
    print(f"\n===== {name} =====")
    turns = load_sample(filename)

    result = compute_PS_indicators_and_evidence(turns, classified_turns=turns)

    print("COUNTS:")
    for k, v in result["counts"].items():
        print(f"  {k}: {v}")

    print("\nEVIDENCE:")
    for snip in result["evidence"]:
        print(f"  - {snip}")


def main():
    samples = [
        ("Example 1", "ps_example_1.json"),
        ("Example 2", "ps_example_2.json"),
        ("Example 3", "ps_example_3.json"),
    ]

    for name, filename in samples:
        run_sample(name, filename)


if __name__ == "__main__":
    main()

import json
from pathlib import Path

from scoring_engine import (
    load_thresholds,
    calculate_scores
)


def main():
    #load thresholds
    thresholds = load_thresholds()
    
    #setup directories
    script_dir = Path(__file__).parent
    input_dir = script_dir / 'scoring_input'
    output_dir = script_dir / 'scoring_output'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        print(f"[ERROR] Input directory not found: {input_dir}")
        print("Please create 'scoring_input' directory and add test JSON files")
        return
    
    input_files = list(input_dir.glob('*.json'))
    if not input_files:
        print(f"[ERROR] No JSON files found in: {input_dir}")
        sys.exit(1)

    #test cases
    print("Scoring Engine Test Cases")
    
    for input_file in input_files:
        print(f"\nProcessing: {input_file.name}")
        with open(input_file, 'r') as f:
            input_data = json.load(f)
    
        indicators = input_data.get('input_indicators', input_data)

        scores = calculate_scores(
            indicators['critical_thinking'],
            indicators['problem_solving'],
            indicators['engagement'],
            thresholds
        )
        
        output = {
            'test_case': input_data.get('test_case', 'unknown'),
            'scores': scores
        }

        output_file = output_dir / f"scoring_output_{input_file.stem}.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Output written to: {output_file}")
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

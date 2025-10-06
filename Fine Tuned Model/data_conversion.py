import json, glob, os, random
from rouge_score import rouge_scorer

INPUT_DIR = r"C:\Users\arnav\OneDrive\Desktop\UNI\3rd Year\T2\SIT378 - Team Project B\Evidence\Full\Fine Tuning Additional\data"
OUTPUT_FILE = "training_data.jsonl"
TRAIN_FILE = "train.jsonl"
VAL_FILE = "val.jsonl"
TEST_FILE = "test.jsonl"

TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1

# --- Helper: compute revision alignment using ROUGE-L ---
scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)

def revision_alignment(final_text, revisions):
    """Return max ROUGE-L F1 * 100 across revision drafts compared to final."""
    if not final_text or not revisions:
        return None
    scores = []
    for rev in revisions:
        if isinstance(rev, dict) and 'content' in rev:
            rev = rev['content']
        if not isinstance(rev, str):
            continue
        s = scorer.score(final_text, rev)['rougeL'].fmeasure
        scores.append(s)
    return round(100 * max(scores), 2) if scores else None

# --- Build user prompt ---
def build_prompt(record, submission):
    rubric = json.dumps(record.get("rubric", {}), indent=2, ensure_ascii=False)
    subs = submission.get("final_submission", "")
    rev = json.dumps(submission.get("revision_chain", []), ensure_ascii=False, indent=2)
    return (
        "You are an AI detection and grading assistant.\n"
        "Given the assignment prompt, rubric, student submission and any revision chain info, "
        "produce a JSON report containing: ai_detection (ai_segments and ai_percent), "
        "revision_alignment (alignment_percent), rubric_scores with comments, and total.\n\n"
        f"Assignment prompt:\n{record.get('prompt','')}\n\n"
        f"Rubric:\n{rubric}\n\n"
        f"Student submission:\n{subs}\n\n"
        f"Revision chain info:\n{rev}\n"
    )

# --- Build assistant completion ---
def build_completion(submission):
    final = submission.get("final_submission", "")
    revisions = submission.get("revision_chain", [])
    align = revision_alignment(final, revisions)

    result = {
        "ai_detection": {
            "ai_segments": submission.get("hybrid_breakdown", {}).get("ai_paragraph_indices", [])
            # no ai_percent — model will learn to predict itself
        },
        "rubric_scores": submission.get("feedback", {})
    }
    total_score = submission.get("total")
    if total_score:
        result["total"] = total_score
    if align is not None:
        result["revision_alignment"] = {"alignment_percent": align}

    return json.dumps(result, ensure_ascii=False)

# --- Convert one file into multiple training rows ---
def convert_file(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        record = json.load(f)
    for s in record.get("submissions", []):
        rows.append({
            "messages": [
                {"role": "system", "content": "You are an AI grading and detection assistant."},
                {"role": "user", "content": build_prompt(record, s)},
                {"role": "assistant", "content": build_completion(s)}
            ]
        })
    return rows

def main():
    # Build dataset
    all_rows = []
    for file in glob.glob(os.path.join(INPUT_DIR, "*.json")):
        print(f"Processing {file}")
        all_rows.extend(convert_file(file))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for row in all_rows:
            json.dump(row, out, ensure_ascii=False)
            out.write("\n")
    print(f"✅ Done: {len(all_rows)} training examples written to {OUTPUT_FILE}")

    # Split into train/val/test
    random.seed(42)  # reproducible
    random.shuffle(all_rows)
    total = len(all_rows)
    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train = all_rows[:train_end]
    val = all_rows[train_end:val_end]
    test = all_rows[val_end:]

    for fname, data in [(TRAIN_FILE, train), (VAL_FILE, val), (TEST_FILE, test)]:
        with open(fname, "w", encoding="utf-8") as out:
            for row in data:
                json.dump(row, out, ensure_ascii=False)
                out.write("\n")
        print(f"✅ {fname}: {len(data)} examples")

    print(f"Total {total} → train {len(train)}, val {len(val)}, test {len(test)}")

if __name__ == "__main__":
    main()

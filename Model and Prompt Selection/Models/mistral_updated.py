# -*- coding: utf-8 -*-

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
DEBUG = True
def dbg(*a, **k):
    if DEBUG: print(*a, **k)


# -----------------------------
# Configuration
# -----------------------------
DATASETS = [
    "/TrainingData/engineering.json",
    "/TrainingData/accounting.json",
    "/TrainingData/it.json",
    "/TrainingData/psychology.json",
    "/TrainingData/teaching.json"
]
BASE_PROMPT_PATH = "/BasePrompts/base_prompts.py"

OUT_DIR = Path("/Evaluation/")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"

# Generation defaults (tweak as needed)
GEN_KW = dict(
    max_new_tokens=512,
    temperature=0.0, 
    top_p=1.0,
    do_sample=False,
)

# -----------------------------
# Utilities
# -----------------------------
def import_base_prompt_module(py_path: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location("base_prompts_user", py_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_json(fp: str) -> Dict[str, Any]:
    with open(fp, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_json(s: str) -> Dict[str, Any]:
    """
    Robust JSON extraction:
    - Prefer ```json fenced block
    - Else use the LAST {...} block (models often preface with text)
    - Fix simple trailing commas
    """
    m = re.search(r"```json\s*([\s\S]*?)\s*```", s, flags=re.IGNORECASE)  # <<< FIX
    if m:
        candidate = m.group(1).strip()
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
        return json.loads(candidate)

    blocks = re.findall(r"\{[\s\S]*?\}", s)  # <<< FIX: get all, pick last
    if not blocks:
        raise ValueError(f"Could not find JSON object in response:\n{s}")
    block = re.sub(r",\s*([}\]])", r"\1", blocks[-1])
    return json.loads(block)
    # ----- Mistral chat sanitiser -----
def _sanitize_for_mistral(messages: List[Dict[str, str]], force_json_hint: str | None = None) -> List[Dict[str, str]]:
    """
    Ensure: one 'system' (first), only user/assistant after, and final turn is 'user'.
    Demotes extra 'system' turns to 'user'. Appends JSON-only hint to last user turn.
    """
    sys = None
    rest: List[Dict[str, str]] = []

    for i, m in enumerate(messages):
        role = m.get("role", "user")
        content = m.get("content", "")
        if i == 0 and role == "system":
            sys = {"role": "system", "content": content}
            continue
        if role not in ("user", "assistant", "system"):
            role = "user"
        if role == "system":
            # demote extra systems to user
            rest.append({"role": "user", "content": content})
        else:
            rest.append({"role": role, "content": content})

    if sys is None:
        sys = {"role": "system", "content": "You are a careful academic assistant."}

    if not rest or rest[-1]["role"] != "user":
        rest.append({"role": "user", "content": ""})

    if force_json_hint:
        rest[-1]["content"] = (rest[-1]["content"] + "\n\n" + force_json_hint).strip()

    return [sys] + rest


def chat_completion(tokenizer, model, messages: List[Dict[str, str]], gen_kw: Dict[str, Any]) -> str:
    # One hint that covers detection OR feedback. The model sees it on the final user turn.
    json_hint = (
        "Answer with STRICT JSON only. No markdown, no prose.\n"
        'If detection: {"label":"ai|human|hybrid","analysis":["..."],"flags":[]}\n'
        'If feedback: {"overall_summary":"...",'
        '"criteria_feedback":[{"criterion_id":"...","rating":"excellent|good|average|needs_improvement|poor",'
        '"evidence":["..."],"improvement_tip":"..."}],"suggested_grade":"..."}'
    )

    msgs = _sanitize_for_mistral(messages, force_json_hint=json_hint)
    dbg("[LAST ROLE]", msgs[-1]["role"])
    dbg("[LAST USER PREVIEW]\n", (msgs[-1]["content"][:300] + " ..."))


    prompt = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([prompt], return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            **gen_kw,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )

    # Cut off the prompt tokens (safer than string slicing)
    gen_ids = outputs[0][inputs["input_ids"].shape[-1]:]
    text = tokenizer.decode(gen_ids, skip_special_tokens=True)
    return text.strip()

def safe_get(d: Dict, key: str, default=None):
    try:
        return d.get(key, default)
    except Exception:
        return default

def _norm_label(s: str) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    if s in {"ai", "llm", "machine", "genai"}:
        return "ai"
    if s in {"human", "student", "person"}:
        return "human"
    if "hybrid" in s or "assisted" in s or "mixed" in s:
        return "hybrid"
    return s

def evaluate_detection(pred_label: str, gold_label: str) -> int:
    return int(_norm_label(pred_label) == _norm_label(gold_label))
import re

def _score_feedback(fb_json: Dict[str, Any]) -> float:
    """
    Return a 1–5 feedback score.
    1) Try to coerce fb_json['suggested_grade'] into 1..5 (handles '4/5', 'four', 3, etc).
    2) Else average mapped criterion ratings (excellent=5 .. poor=1), handling
       rating variants and dict/list shapes.
    """

    def coerce_1to5(val) -> float | None:
        if val is None:
            return None
        s = str(val).strip().lower()
        # match digits like 4 or 4/5
        m = re.search(r'([1-5])(?:\s*/\s*5)?', s)
        if m:
            return float(m.group(1))
        # words -> numbers
        words = {"one":1, "two":2, "three":3, "four":4, "five":5}
        for w, n in words.items():
            if w in s:
                return float(n)
        return None

    # 1) suggested_grade
    sg = fb_json.get("suggested_grade")
    sgf = coerce_1to5(sg)
    if sgf is not None:
        return sgf

    # 2) average the rubric ratings
    mapping = {
        "excellent": 5, "outstanding": 5,
        "good": 4, "very good": 4,
        "average": 3, "fair": 3,
        "needs_improvement": 2, "needs improvement": 2, "weak": 2,
        "poor": 1, "insufficient": 1
    }

    crit = fb_json.get("criteria_feedback") or []
    # If it's a dict of {criterion_id: {...}}, convert to list
    if isinstance(crit, dict):
        crit = list(crit.values())

    pts = []
    for c in crit:
        if not isinstance(c, dict):
            continue
        r = str(c.get("rating", "")).strip().lower()
        # normalize underscores/spaces
        r = r.replace("-", " ").replace("_", " ")
        # try full string, then first token
        if r in mapping:
            pts.append(mapping[r])
        else:
            first = r.split()[0] if r else ""
            if first in mapping:
                pts.append(mapping[first])

    return round(sum(pts)/len(pts), 2) if pts else 0.0


# -----------------------------
# Main Experiment
# -----------------------------
def _assert_paths():
    for ds in DATASETS:
        if not Path(ds).exists():
            raise FileNotFoundError(f"Dataset not found: {ds}")
    if not Path(BASE_PROMPT_PATH).exists():
        raise FileNotFoundError(f"Base prompt file not found: {BASE_PROMPT_PATH}")

def run(model_id: str, precision: str = "bfloat16"):
    _assert_paths()

    # Load model + tokenizer
    use_bf16 = (precision == "bfloat16" and torch.cuda.is_available())
    dtype = torch.bfloat16 if use_bf16 else torch.float16

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="auto",
        low_cpu_mem_usage=True,
        trust_remote_code=True,
    )
    model.eval()

    # Import base prompt helpers (user-provided)
    bp = import_base_prompt_module(BASE_PROMPT_PATH)
    build_detection_prompt = getattr(bp, "build_detection_prompt")
    build_feedback_prompt = getattr(bp, "build_feedback_prompt")

    rows = []

    for ds_path in DATASETS:
        ds = load_json(ds_path)
        domain = ds["domain"]
        assignment_prompt = ds["prompt"]
        rubric = ds["rubric"]
        rubric_text = json.dumps(rubric, ensure_ascii=False)
        submissions = ds["submissions"]

        few_shots = []
        for ex in submissions[:2]:
            few_shots.append({
                "final_submission": ex["final_submission"],
                "label_type": ex.get("label_type", "")
            })

        for idx, item in enumerate(submissions):
            gold_label = item.get("label_type", "")
            submission_text = item["final_submission"]

            # ---------- 1) Detection ----------
            det_messages = build_detection_prompt(submission=submission_text, few_shots=few_shots)
            det_raw = chat_completion(tokenizer, model, det_messages, GEN_KW)
            det_json = {}
            det_ok = True
            det_err = ""
            try:
                det_json = ensure_json(det_raw)
                det_label = safe_get(det_json, "label", "")
                det_rationale = safe_get(det_json, "analysis", [])
                det_flags = safe_get(det_json, "flags", [])
            except Exception as e:
                det_ok = False
                det_err = f"{type(e).__name__}: {e}"
                det_label, det_rationale, det_flags = "", [], []
                print(f"[DETECT PARSE FAIL] {Path(ds_path).name} item {idx}\nRAW:\n{det_raw[:800]}\n---")  # <<< FIX

            det_score = evaluate_detection(det_label, gold_label)

            # ---------- 2) Rubric Feedback ----------
            fb_messages = build_feedback_prompt(
                domain=domain,
                assignment_prompt=assignment_prompt,
                rubric_text=rubric_text,
                submission=submission_text
            )
            fb_raw = chat_completion(tokenizer, model, fb_messages, GEN_KW)
            fb_json = {}
            fb_ok = True
            fb_err = ""
            try:
                fb_json = ensure_json(fb_raw)
                fb_score = _score_feedback(fb_json)
                if DEBUG:
                    print("fb_json keys:", list(fb_json.keys()))
                    print("suggested_grade raw:", fb_json.get("suggested_grade"))
                    print("criteria_feedback type/len:", type(fb_json.get("criteria_feedback")).__name__,
                          len(fb_json.get("criteria_feedback") or []))
                    print("computed fb_score:", fb_score)

            except Exception as e:
                fb_ok = False
                fb_err = f"{type(e).__name__}: {e}"
                fb_json = {"overall_summary": "", "criteria_feedback": [], "suggested_grade": ""}
                fb_score = 0.0
                print(f"[FEEDBACK PARSE FAIL] {Path(ds_path).name} item {idx}\nRAW:\n{fb_raw[:800]}\n---")  # <<< FIX
                # >>> Add this diagnostic log HERE <<<
                if fb_ok and fb_score == 0.0:
                    print(f"[FB SCORE ZERO] {Path(ds_path).name} item {idx}")
                    print("Parsed JSON:", json.dumps(fb_json, ensure_ascii=False)[:800])
                    print("--- RAW (first 800 chars) ---\n", fb_raw[:800], "\n---")
            rows.append({
                "dataset": Path(ds_path).name,
                "domain": domain,
                "item_index": idx,
                "gold_label": gold_label,
                "det_raw": det_raw,
                "det_ok": det_ok,
                "det_error": det_err,
                "det_label": det_json.get("label", ""),
                "det_rationale": det_json.get("analysis", []),
                "det_flags": det_json.get("flags", []),
                "det_correct": det_score,
                "fb_raw": fb_raw,
                "fb_ok": fb_ok,
                "fb_error": fb_err,
                "fb_overall_summary": fb_json.get("overall_summary", ""),
                "fb_criteria_feedback": fb_json.get("criteria_feedback", []),
                "fb_suggested_grade": fb_json.get("suggested_grade", ""),
                "fb_score": fb_score
            })

    # -----------------------------
    # Save Reports
    # -----------------------------
    jsonl_path = OUT_DIR / "mistral_eval_results.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    summary = {}
    for r in rows:
        ds = r["dataset"]
        summary.setdefault(ds, {"n": 0, "det_correct": 0, "fb_scores": []})
        summary[ds]["n"] += 1
        summary[ds]["det_correct"] += int(r["det_correct"])
        if r.get("fb_ok"):
            try:
                summary[ds]["fb_scores"].append(float(r.get("fb_score", 0)))
            except Exception:
                pass

    for ds, agg in summary.items():
      n = max(1, agg["n"])
      agg["detection_accuracy"] = round(agg["det_correct"] / n, 3)
      fs = agg.get("fb_scores", [])
      agg["feedback_mean"] = round(sum(fs)/len(fs), 2) if fs else 0.0
      agg["feedback_n"] = len(fs)

    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    import csv
    csv_path = OUT_DIR / "mistral_eval_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "dataset","domain","item_index","gold_label",
            "det_ok","det_label","det_correct","det_flags",
            "fb_ok","fb_suggested_grade","fb_score"
        ])
        for r in rows:
            writer.writerow([
                r["dataset"], r["domain"], r["item_index"], r["gold_label"],
                r["det_ok"], r["det_label"], r["det_correct"], "|".join(r.get("det_flags", []) or []),
                r["fb_ok"], r.get("fb_suggested_grade",""), r.get("fb_score","")
            ])

    print(f"[OK] Wrote:\n- {jsonl_path}\n- {csv_path}\n- {OUT_DIR/'summary.json'}")

# NOTE (Colab): run this from another cell if you've already loaded model/tokenizer,
# or just call: run(MODEL_ID, precision="bfloat16")
if __name__ == "__main__":
    run(MODEL_ID, precision="bfloat16")
from __future__ import annotations
import json
from typing import Dict, Any, List, Optional
from app.models.llm_client import build_client
from app.prompting.templates import (
    build_system_prompt,
    build_fewshot_block,
    build_user_prompt,
    json_schema_for,
    # new helpers
    create_few_shot_block,
    build_detection_prompt,
    build_feedback_prompt,
    format_rubric,
)
from app.services.evaluation import list_to_paragraph, analyze_raw_feedback_output, log_feedback_metrics
from app.data.fewshot_loader import fewshots_for_domain


def _to_rating(score: float) -> str:
    """
    Map numeric score [0,1] to rating categories.
    """
    try:
        s = float(score)
    except Exception:
        return 'average'
    if s >= 0.85:
        return 'excellent'
    if s >= 0.70:
        return 'good'
    if s >= 0.50:
        return 'average'
    if s >= 0.35:
        return 'needs improvement'
    return 'poor'

def _safe_json_loads(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise

def _norm_classification(obj: Any) -> Dict[str, Any]:
    """
    Accepts a variety of shapes and returns:
      { "label": "AI|Human|Hybrid", "rationale": "..." }
    """
    if isinstance(obj, dict):
        # common shapes:
        # { "label": "AI", "rationale": "..." }
        if "label" in obj and isinstance(obj.get("label"), str):
            return {
                "label": obj["label"],
                "rationale": str(obj.get("rationale") or obj.get("reason") or obj.get("explanation") or obj.get("feedback") or "")
            }
        # { "classification": "Human-written", "reasoning": "..." }
        if "classification" in obj and isinstance(obj["classification"], str):
            return {
                "label": obj["classification"],
                "rationale": str(obj.get("reasoning") or obj.get("rationale") or obj.get("reason") or obj.get("explanation") or obj.get("feedback") or "")
            }
        # { "classification": {...} }
        if "classification" in obj and isinstance(obj["classification"], dict):
            inner = obj["classification"]
            if "label" in inner:
                return {
                    "label": inner.get("label"),
                    "rationale": str(inner.get("rationale") or inner.get("feedback") or "")
                }
        # { "submission_classification": "AI", ... }
        if "submission_classification" in obj:
            return {
                "label": str(obj["submission_classification"]),
                "rationale": str(obj.get("rationale") or obj.get("feedback") or "")
            }
    # last resort
    return {"label": "Human", "rationale": "Heuristic default because provider output was unstructured."}

def _norm_confidence(obj: Any) -> Dict[str, Any]:
    """
    Returns:
      { "confidence": float 0..1, "basis": "..." }
    """
    # direct shape
    if isinstance(obj, dict) and "confidence" in obj and isinstance(obj["confidence"], (int, float)):
        return {
            "confidence": max(0.0, min(1.0, float(obj["confidence"]))),
            "basis": str(obj.get("basis") or obj.get("reason") or obj.get("rationale") or "Derived from model output.")
        }
    # nested
    if isinstance(obj, dict) and "confidence" in obj.get("confidence", {}):
        c = obj["confidence"]["confidence"]
        return {"confidence": max(0.0, min(1.0, float(c))), "basis": str(obj["confidence"].get("basis") or "Derived.")}

    # weird shapes like:
    # { "confidence": 0.9, "submission_classification": "AI", ... }
    if isinstance(obj, dict) and "confidence" in obj:
        try:
            c = float(obj["confidence"])
        except Exception:
            c = 0.5
        basis = []
        for k in ("basis","reason","rationale","feedback"):
            if k in obj and isinstance(obj[k], str):
                basis.append(obj[k])
        if not basis:
            # if scores present, include a hint
            if "scores" in obj:
                basis.append("Computed from rubric alignment.")
        return {"confidence": max(0.0, min(1.0, c)), "basis": " ".join(basis) or "Derived."}

    # default
    return {"confidence": 0.7, "basis": "Default fallback."}

def _rubric_index(rubric: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    Returns a map { criterion_id: {"name": ..., "description": ...}, ... }
    """
    out = {}
    for c in rubric.get("criteria", []):
        cid = c.get("criterion_id") or c.get("id") or c.get("key") or ""
        if cid:
            out[cid] = {"name": c.get("name") or cid, "description": c.get("description") or ""}
    return out



def _norm_rubric_scores(obj: Any, rubric: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert rubric scoring to categorical ratings.

    Returns a dictionary containing a list of per‑criterion ratings.
    Rationales and overall ratings are deliberately omitted to keep
    outputs lightweight, as per the updated requirements.

    Parameters
    ----------
    obj : Any
        The raw output from the language model. This may be a
        dictionary containing numeric scores, ratings or nested
        structures.
    rubric : Dict[str, Any]
        The rubric against which the submission was scored. Used to look up
        criterion names.

    Returns
    -------
    Dict[str, Any]
        A dictionary with a single key `scores` whose value is a list of
        dictionaries, each containing `criterion_id`, `name` and
        `rating` (categorical).
    """
    # If 'scores' provided with rating or numeric
    if isinstance(obj, dict) and 'scores' in obj:
        idx = _rubric_index(rubric)
        out_scores = []
        for item in obj.get('scores', []):
            cid = item.get('criterion_id') or item.get('id') or ''
            name = item.get('name') or idx.get(cid, {}).get('name', cid)
            # determine rating from explicit rating or numeric score
            rating: str
            if 'rating' in item:
                rating = str(item['rating']).lower()
            elif 'score' in item:
                rating = _to_rating(float(item['score']))
            else:
                rating = 'average'
            out_scores.append({'criterion_id': cid, 'name': name, 'rating': rating})
        return {'scores': out_scores}

    # If dict keyed by criterion ids to numeric values
    if isinstance(obj, dict):
        idx = _rubric_index(rubric)
        if all(isinstance(v, (int, float)) for v in obj.values() if v is not None):
            out_scores = []
            for cid, val in obj.items():
                if cid in ['overall', 'summary']:
                    continue
                name = idx.get(cid, {}).get('name', cid)
                rating = _to_rating(float(val))
                out_scores.append({'criterion_id': cid, 'name': name, 'rating': rating})
            return {'scores': out_scores}

    # Default fallback
    return {'scores': []}


def _norm_feedback(obj: Any) -> Dict[str, Any]:
    """
    Normalise feedback output for the feedback endpoint.

    The updated feedback endpoint now returns a simple narrative string
    rather than a structured object. If the raw model output is a
    dictionary, we attempt to extract a free‑form text field. If it's a
    string, we return it directly. Otherwise a default message is
    provided.

    Parameters
    ----------
    obj : Any
        The raw output from the language model.

    Returns
    -------
    Dict[str, Any]
        A dictionary with a single key 'feedback' mapping to a string.
    """
    # If dict, attempt to extract a feedback field or concatenate values
    if isinstance(obj, dict):
        # look for common keys that might contain free‑form feedback
        for key in ['feedback', 'summary', 'overall_summary', 'text']:
            val = obj.get(key)
            if isinstance(val, str) and val.strip():
                return {'feedback': val.strip()}
        # if nested dict
        if 'feedback' in obj and isinstance(obj['feedback'], dict):
            # join all string values in nested dict
            parts = []
            for v in obj['feedback'].values():
                if isinstance(v, str):
                    parts.append(v)
                elif isinstance(v, list):
                    parts.extend([p for p in v if isinstance(p, str)])
            if parts:
                return {'feedback': ' '.join(parts)}
    # If string, return as is
    if isinstance(obj, str):
        return {'feedback': obj.strip()}
    # Default fallback
    return {'feedback': 'No feedback provided.'}

# ---------------------------------------------------------------------------
# New helper for deriving rubric ratings from narrative feedback

def _ratings_schema_from_rubric(rubric: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a JSON schema that requires a string rating for each rubric criterion.

    Each criterion ID becomes a property whose value must be one of the
    allowed rating labels. This schema is used when asking the LLM to
    assign ratings based on a feedback paragraph. The returned schema
    disables additional properties to ensure only known criteria are
    included.

    Parameters
    ----------
    rubric : Dict[str, Any]
        The rubric dictionary used to evaluate submissions. Must contain
        a list of criteria with unique `criterion_id` values.

    Returns
    -------
    Dict[str, Any]
        A JSON schema describing an object with required properties for
        each criterion ID. The allowed values are the five rating
        categories.
    """
    props: Dict[str, Any] = {}
    for c in rubric.get("criteria", []):
        cid = c.get("criterion_id") or c.get("id") or c.get("key")
        if not cid:
            continue
        props[str(cid)] = {
            "type": "string",
            "enum": [
                "excellent",
                "good",
                "average",
                "needs improvement",
                "poor",
            ],
        }
    return {
        "type": "object",
        "properties": props,
        "required": list(props.keys()),
        "additionalProperties": False,
    }
class EvaluatorService:
    def __init__(self):
        self.client = build_client()

    async def _ask(self, task: str, domain: str, prompt: str, rubric: Dict, submission: str) -> Dict:
        fewshots = fewshots_for_domain(domain, k=None)
        system_prompt = build_system_prompt()
        fs_block = build_fewshot_block(fewshots)
        user_prompt = f"{fs_block}\n\n" + build_user_prompt(task, domain, prompt, rubric, submission)
        schema = json_schema_for(task)
        text = await self.client.generate(system_prompt, user_prompt, schema)
        data = _safe_json_loads(text)
        return data

    async def classify(self, domain: str, prompt: str, rubric: Dict, submission: str) -> Dict:
        """
        Classify the submission as Human, AI or Hybrid with a confidence score.

        This method now uses the new detection prompt to obtain the label
        and then separately queries the model for a confidence estimate. The
        rationale previously returned is no longer exposed.
        """
        # Build few‑shot examples using the updated helper
        fewshots = fewshots_for_domain(domain, k=None)
        example_block = create_few_shot_block(fewshots)
        # Construct detection prompts
        prompts = build_detection_prompt(example_block, submission)
        # Generate output using Gemini or mock
        text = await self.client.generate(prompts["system"], prompts["user"], json_schema={})
        # Parse JSON output safely
        try:
            det = _safe_json_loads(text)
        except Exception:
            det = {}
        label = None
        if isinstance(det, dict):
            label = det.get("label")
        if not label:
            # fallback to heuristic classification from legacy normalisation
            raw = await self._ask("classification", domain, prompt, rubric, submission)
            norm = _norm_classification(raw)
            label = norm.get("label")
        # obtain confidence separately
        conf = await self.confidence(domain, prompt, rubric, submission)
        confidence_val = conf.get("confidence", 0.0)
        return {"label": label or "Human", "confidence": confidence_val}

    async def confidence(self, domain: str, prompt: str, rubric: Dict, submission: str) -> Dict:
        """
        Estimate the confidence of the classification.

        Only the numeric confidence value (0–1) is returned; any textual
        basis provided by the model is discarded.
        """
        raw = await self._ask("confidence", domain, prompt, rubric, submission)
        norm = _norm_confidence(raw)
        return {"confidence": norm.get("confidence", 0.0)}

    async def rubric_scores(
        self,
        domain: str,
        prompt: str,
        rubric: Dict,
        submission: str,
        feedback_obj: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """
        Derive per‑criterion ratings from a structured feedback object.

        This implementation does not query the language model a second time. Instead
        it relies on the ratings already present in the feedback returned by
        ``self.feedback()``. If a ``feedback_obj`` is provided, it will be
        used directly; otherwise the feedback will be generated internally.

        Parameters
        ----------
        domain : str
            The academic domain (e.g. Accounting, Teaching).
        prompt : str
            The high‑level prompt describing the evaluation task.
        rubric : Dict
            The rubric containing criterion IDs and names.
        submission : str
            The student's submission text to evaluate.
        feedback_obj : dict, optional
            A previously generated structured feedback object. If supplied,
            rubric scores will be derived from this object without calling
            ``feedback()`` again.

        Returns
        -------
        Dict
            A dictionary with a single key ``'scores'`` mapping to a list of
            dictionaries with ``criterion_id``, ``name`` and ``rating`` keys.
        """
        # Reuse the provided feedback object or fetch a new one
        if feedback_obj is None:
            fb = await self.feedback(domain, prompt, rubric, submission)
        else:
            fb = feedback_obj
        # Build a lookup from criterion_id to rating
        ratings_map: Dict[str, str] = {}
        if isinstance(fb, dict):
            for item in fb.get("criteria", []) or []:
                cid = item.get("criterion_id")
                rating = item.get("rating")
                if isinstance(cid, str) and isinstance(rating, str):
                    ratings_map[cid] = rating.lower().strip()
        scores: List[Dict[str, Any]] = []
        for c in rubric.get("criteria", []) or []:
            cid = c.get("criterion_id") or c.get("id") or c.get("key") or ""
            name = c.get("name") or ""
            rating = ratings_map.get(str(cid), "average")
            scores.append({"criterion_id": cid, "name": name, "rating": rating})
        return {"scores": scores}

    async def feedback(
        self, domain: str, prompt: str, rubric: Dict, submission: str
    ) -> Dict:
        """
        Generate structured feedback for a submission.

        This method instructs the language model to return a strict JSON
        object with keys ``overall_grade``, ``reasoning``, ``criteria``,
        ``strengths``, ``weaknesses`` and ``improvement_tips``. The model
        is guided with the rubric and submission context to produce
        categorical ratings and explanatory reasoning. Bullet points are
        discouraged in favour of cohesive paragraphs. After receiving the
        raw output, basic formatting metrics are logged, the JSON is
        parsed, paragraphs are normalised, missing criterion ratings are
        filled in, and summary metrics of the final structure are printed.

        Parameters
        ----------
        domain : str
            The academic domain of the task (e.g. "Accounting").
        prompt : str
            The high‑level task prompt provided by the caller.
        rubric : Dict
            The rubric defining criterion IDs and descriptions.
        submission : str
            The student's submission text.

        Returns
        -------
        Dict
            A structured feedback dictionary with keys as described above.
        """
        rubric_text = format_rubric(rubric)
        # Compose the system and user messages to solicit structured feedback
        system_msg = (
            "You are a fair and constructive educational evaluator. "
            "You will analyse a student's submission against a rubric and "
            "produce feedback in structured JSON only. The JSON must have "
            "exactly the keys: overall_grade, reasoning, criteria, strengths, "
            "weaknesses, improvement_tips. Do not include any other keys. "
            "The values of overall_grade and all criterion ratings must be one of: "
            "excellent, good, average, needs improvement, poor."
        )
        user_msg = (
            f"Domain: {domain}\n"
            f"Prompt: {prompt}\n"
            f"Rubric:\n{rubric_text}\n"
            f"Submission:\n{submission}\n\n"
            "Evaluate the submission based on the rubric. "
            "Return a JSON object with these fields:\n"
            "- overall_grade: a single word from the allowed labels summarising the overall performance.\n"
            "- reasoning: a few sentences explaining why the overall_grade was chosen.\n"
            "- criteria: a list of objects, one per rubric criterion, each containing: criterion_id, reasoning, rating.\n"
            "- strengths: a cohesive paragraph outlining key strengths.\n"
            "- weaknesses: a cohesive paragraph outlining the main weaknesses.\n"
            "- improvement_tips: a cohesive paragraph suggesting concrete next steps.\n"
            "Use full sentences and avoid bullet points or lists. Return only JSON."
        )
        # Instruct the model to obey the JSON schema
        schema = json_schema_for("feedback")
        # Generate the raw JSON string from the model
        raw = await self.client.generate(system_msg, user_msg, json_schema=schema)
        # Analyse the raw output formatting
        try:
            analyze_raw_feedback_output(raw)
        except Exception:
            pass
        # Parse JSON
        try:
            data: Any = _safe_json_loads(raw)
        except Exception:
            data = {}
        # Build the output structure with defaults
        feedback: Dict[str, Any] = {}
        # overall grade
        grade = data.get("overall_grade")
        if not isinstance(grade, str):
            grade = "average"
        feedback["overall_grade"] = grade.lower().strip()
        # reasoning with paragraph enforcement
        reasoning = data.get("reasoning")
        feedback["reasoning"] = list_to_paragraph(reasoning) if reasoning else ""
        # criteria list
        out_criteria: List[Dict[str, Any]] = []
        # Map provided criterion ratings for lookup
        provided_map: Dict[str, Dict[str, Any]] = {}
        if isinstance(data.get("criteria"), list):
            for item in data["criteria"]:
                if isinstance(item, dict):
                    cid = str(item.get("criterion_id") or item.get("id") or "")
                    provided_map[cid] = item
        # Iterate rubric criteria to preserve order and fill defaults
        for c in rubric.get("criteria", []) or []:
            cid = c.get("criterion_id") or c.get("id") or c.get("key") or ""
            item = provided_map.get(str(cid), {})
            reason_item = item.get("reasoning") or item.get("rationale") or ""
            rating_val = item.get("rating") or item.get("score") or "average"
            # normalise rating
            if isinstance(rating_val, str):
                rating = rating_val.lower().strip()
            else:
                try:
                    rating = _to_rating(float(rating_val))
                except Exception:
                    rating = "average"
            out_criteria.append({
                "criterion_id": cid,
                "reasoning": list_to_paragraph(reason_item) if reason_item else "",
                "rating": rating,
            })
        feedback["criteria"] = out_criteria
        # strengths, weaknesses, improvement_tips
        strengths_val = data.get("strengths")
        feedback["strengths"] = list_to_paragraph(strengths_val) if strengths_val else ""
        weaknesses_val = data.get("weaknesses")
        feedback["weaknesses"] = list_to_paragraph(weaknesses_val) if weaknesses_val else ""
        # improvement_tips may be named differently; fall back to next_steps
        improvement_val = data.get("improvement_tips") or data.get("next_steps")
        feedback["improvement_tips"] = list_to_paragraph(improvement_val) if improvement_val else ""
        # Log metrics on the structured feedback
        try:
            log_feedback_metrics(feedback, rubric)
        except Exception:
            pass
        return feedback

    async def evaluate(self, domain: str, prompt: str, rubric: Dict, submission: str) -> Dict:
        """
        Aggregate classification, derived rubric scores and narrative feedback.

        This method first obtains the classification (which includes
        confidence), then generates a narrative feedback paragraph and
        finally derives per‑criterion ratings from that feedback. The
        aggregated response includes the classification, rubric scores
        derived from the feedback, and the feedback paragraph itself.
        """
        # Obtain classification (label and confidence)
        cls = await self.classify(domain, prompt, rubric, submission)
        # Generate structured feedback
        fb = await self.feedback(domain, prompt, rubric, submission)
        # Derive rubric scores from the feedback without re‑calling the model
        rub = await self.rubric_scores(domain, prompt, rubric, submission, feedback_obj=fb)
        # Return all information together
        return {
            "classification": cls,
            "rubric_scores": rub,
            "feedback": fb,
        }

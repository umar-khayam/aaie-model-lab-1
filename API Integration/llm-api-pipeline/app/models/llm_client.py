from __future__ import annotations
import json, httpx, os, time, random
from typing import Dict, Any, List
from app.config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE, MAX_OUTPUT_TOKENS, MOCK

class LLMClient:
    async def generate(self, system_prompt: str, user_prompt: str, json_schema: Dict) -> str:
        raise NotImplementedError

class MockClient(LLMClient):
    async def generate(self, system_prompt: str, user_prompt: str, json_schema: Dict) -> str:
        seed = abs(hash(user_prompt)) % (2**32)
        random.seed(seed)
        label = random.choice(["AI", "Human", "Hybrid"])
        conf = round(random.uniform(0.55, 0.95), 2)
        scores = []
        try:
            lines = [ln.strip() for ln in user_prompt.splitlines() if ln.strip().startswith("- ")]
            for ln in lines:
                parts = ln[2:].split(":", 1)
                cid = parts[0].strip() if parts else f"c{len(scores)+1}"
                name = parts[1].split("—")[0].strip() if len(parts) > 1 else f"Criterion {len(scores)+1}"
                scores.append({
                    "criterion_id": cid,
                    "name": name,
                    "score": round(random.uniform(0.4, 0.95), 2),
                    "rationale": "Auto-generated rationale (mock)."
                })
        except Exception:
            for i in range(3):
                scores.append({"criterion_id": f"c{i+1}", "name": f"Criterion {i+1}", "score": round(random.uniform(0.4,0.95),2), "rationale":"Mock."})
        overall = round(sum(s["score"] for s in scores)/max(1,len(scores)), 2) if scores else conf
        if 'classification' in user_prompt.lower():
            return json.dumps({"label": label, "rationale": "Mock classification based on few-shot hints."})
        if 'confidence' in user_prompt.lower():
            return json.dumps({"confidence": conf, "basis": "Mock confidence based on features and rubric alignment."})
        if 'rubric' in user_prompt.lower() and 'scores' in json_schema.get("properties", {}):
            return json.dumps({"scores": scores, "overall": overall})
        if 'feedback' in user_prompt.lower():
            # Construct a mock structured feedback response matching the new schema.
            # Derive criterion IDs from the user prompt if possible
            crits: List[Dict[str, Any]] = []
            try:
                # Look for patterns like "Criterion: c1" in the prompt to extract IDs
                import re as _re
                ids = _re.findall(r"Criterion[:\s]*([\w-]+)", user_prompt)
            except Exception:
                ids = []
            if not ids:
                ids = [f"c{i+1}" for i in range(2)]
            for cid in ids:
                crit_rating = random.choice(["excellent", "good", "average", "needs improvement", "poor"])
                crit_reason = f"Mock reasoning for {cid}"
                crits.append({"criterion_id": cid, "reasoning": crit_reason, "rating": crit_rating})
            overall_label = random.choice(["excellent", "good", "average", "needs improvement", "poor"])
            response = {
                "overall_grade": overall_label,
                "reasoning": "Mock overall reasoning about the submission.",
                "criteria": crits,
                # Return lists of strings so the evaluator can exercise list_to_paragraph
                "strengths": ["Clear structure", "Good organisation"],
                "weaknesses": ["Lacks depth", "Shallow analysis"],
                "improvement_tips": ["Add citations", "Deepen critique"],
            }
            return json.dumps(response)
        return json.dumps({
            "classification": {"label": label, "rationale": "Mock."},
            "confidence": {"confidence": conf, "basis": "Mock."},
            "rubric_scores": {"scores": scores, "overall": overall},
            "feedback": {"strengths": ["Clear"], "weaknesses": ["Needs depth"], "next_steps": ["Expand"]}
        })

class GeminiClient(LLMClient):
    async def generate(self, system_prompt: str, user_prompt: str, json_schema: Dict) -> str:
        api_key = GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        model = GEMINI_MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        content = [
            {"role": "user", "parts": [{"text": system_prompt}]},
            {"role": "user", "parts": [{"text": user_prompt}]},
        ]
        payload = {
            "contents": content,
            "generationConfig": {
                "temperature": TEMPERATURE,
                "maxOutputTokens": MAX_OUTPUT_TOKENS,
                "responseMimeType": "application/json"
            }
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            try:
                candidates = data["candidates"]
                text = candidates[0]["content"]["parts"][0]["text"]
                return text
            except Exception as e:
                raise RuntimeError(f"Unexpected Gemini response: {data}") from e

def build_client() -> LLMClient:
    if MOCK:
        return MockClient()
    return GeminiClient()

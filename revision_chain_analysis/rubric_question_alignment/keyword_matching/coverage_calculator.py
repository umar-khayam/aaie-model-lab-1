from typing import List, Dict, Any, Set


def calculate_criterion_coverage(
    criterion_id: str,
    criterion_name: str,
    weight: float,
    matched_prompts: List[Dict[str, Any]],
    criterion_keywords: List[str],
    total_prompts: int = None
) -> Dict[str, Any]:
    #calculate coverage metrics for a single rubric criterion
    
    #extract matched prompt IDs
    matched_prompt_ids = [p["prompt_id"] for p in matched_prompts]
    
    #calculate coverage score based on:
    #- proportion of keywords engaged (50% weight)
    #- average relevance score of matched prompts (50% weight)
    
    #identify which keywords were matched (used for both coverage calculation and unmatched keyword tracking)
    matched_keywords = set()
    for prompt in matched_prompts:
        prompt_lower = prompt["text"].lower()
        for keyword in criterion_keywords:
            if keyword.lower() in prompt_lower:
                matched_keywords.add(keyword)
    
    if not criterion_keywords:
        coverage_score = 0.0
    elif not matched_prompts:
        coverage_score = 0.0
    else:
        #keyword coverage component
        keyword_coverage = len(matched_keywords) / len(criterion_keywords)
        
        #average relevance score component
        avg_relevance = sum(p["relevance_score"] for p in matched_prompts) / len(matched_prompts)
        
        #combined coverage score
        coverage_score = (0.5 * keyword_coverage) + (0.5 * avg_relevance)
    
    
    unmatched_keywords = [kw for kw in criterion_keywords if kw not in matched_keywords_set]
    
    #map coverage score to status
    if coverage_score >= 0.80:
        status = "well_covered"
    elif coverage_score >= 0.50:
        status = "adequately_covered"
    elif coverage_score >= 0.20:
        status = "undercovered"
    else:
        status = "significantly_undercovered"
    
    return {
        "criteria_id": criterion_id,
        "criteria_name": criterion_name,
        "weight": weight,
        "coverage_score": coverage_score,
        "status": status,
        "prompts_matched": len(matched_prompts),
        "matched_prompt_ids": matched_prompt_ids,
        "unmatched_keywords": unmatched_keywords
    }


def calculate_overall_alignment(
    criterion_coverages: List[Dict[str, Any]],
    total_prompts: int
) -> Dict[str, Any]:
    
    if not criterion_coverages:
        return {
            "overall_alignment": 0.0,
            "status": "minimal_coverage",
            "total_prompts_analyzed": total_prompts,
            "off_topic_prompts": total_prompts
        }
    
    #calculate weighted average of coverage scores
    total_weight = sum(c["weight"] for c in criterion_coverages)
    
    if total_weight == 0:
        overall_alignment = 0.0
    else:
        weighted_sum = sum(c["coverage_score"] * c["weight"] for c in criterion_coverages)
        overall_alignment = weighted_sum / total_weight
    
    #collect all unique matched prompt IDs
    all_matched_ids = set()
    for coverage in criterion_coverages:
        all_matched_ids.update(coverage["matched_prompt_ids"])
    
    #calculate off-topic prompts (prompts not matched to any criterion)
    off_topic_prompts = total_prompts - len(all_matched_ids)
    
    #map overall alignment to status
    if overall_alignment >= 0.85:
        status = "systematic_coverage"
    elif overall_alignment >= 0.70:
        status = "broad_coverage"
    elif overall_alignment >= 0.55:
        status = "partial_coverage"
    else:
        status = "minimal_coverage"
    
    return {
        "overall_alignment": overall_alignment,
        "status": status,
        "total_prompts_analyzed": total_prompts,
        "off_topic_prompts": off_topic_prompts
    }


def calculate_off_topic_prompts(
    prompts: List[Dict[str, Any]],
    all_matched_prompt_ids: Set[Any]
) -> int:
    #calculate number of off-topic prompts not matched to any criterion
    total_prompts = len(prompts)
    matched_count = len(all_matched_prompt_ids)
    
    return total_prompts - matched_count


def _validate_weights(criterion_coverages: List[Dict[str, Any]]) -> bool:
    #helper function to validate that criterion weights sum to 1.0
    total_weight = sum(c["weight"] for c in criterion_coverages)
    # Allow small floating point tolerance
    return abs(total_weight - 1.0) < 0.01


def _get_unique_matched_ids(criterion_coverages: List[Dict[str, Any]]) -> Set[Any]:
    #helper function to extract all unique matched prompt IDs across criteria
    unique_ids = set()
    for coverage in criterion_coverages:
        unique_ids.update(coverage["matched_prompt_ids"])
    return unique_ids

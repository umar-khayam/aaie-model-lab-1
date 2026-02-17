from typing import List, Dict, Any, Set
import re

def match_prompts_to_criterion(
        prompts: List[Dict[str, Any]], 
        criterion_keywords: List[str]
        ) -> Dict[str, Any]:
    #match student prompts to rubric criterion based on keyword matching

    matched_prompts = []
    keyword_engagement = {kw: 0.0 for kw in criterion_keywords}

    for prompt in prompts:
        relevance_score = calculate_relevance_score(prompt_text=prompt['text'], criterion_keywords=criterion_keywords)

        if relevance_score > 0:
            matched_prompts.append({
                "prompt_id": prompt["prompt_id"],
                "text": prompt["text"],
                "relevance_score": relevance_score
            })

            #track keyword engagement
            prompt_lower = prompt["text"].lower()
            for keyword in criterion_keywords:
                if keyword.lower() in prompt_lower:
                    keyword_engagement[keyword] += relevance_score

    #identify unmatched or very low engagement keywords (threshold: 0.1)
    unmatched_keywords = [
        kw for kw, engagement in keyword_engagement.items()
        if engagement < 0.1
    ]
    
    #returns dictionary with matched prompts and unmatched keywords
    return {
        "matched_prompts": matched_prompts,
        "unmatched_keywords": unmatched_keywords
    }

def calculate_relevance_score(
    prompt_text: str,
    criterion_keywords: List[str]
) -> float:
    #calculate a 0-1 relevance score for a prompt based on keyword matches
    
    if not criterion_keywords:
        return 0.0
    
    prompt_lower = prompt_text.lower()
    
    #tokenize prompt for word boundary matching
    prompt_tokens = set(re.findall(r'\b\w+\b', prompt_lower))
    
    matched_keywords = 0
    total_keyword_occurrences = 0
    
    for keyword in criterion_keywords:
        keyword_lower = keyword.lower()
        
        #check for word boundary matches (more precise than substring, also check for exact substring match for multi-word keywords
        keyword_tokens = set(re.findall(r'\b\w+\b', keyword_lower))
        
        #count as match if keyword appears as whole word or all keyword tokens present
        if keyword_lower in prompt_lower or keyword_tokens.issubset(prompt_tokens):
            matched_keywords += 1
            #count occurrences (capped at 3 to avoid over-weighting repetition)
            occurrences = min(prompt_lower.count(keyword_lower), 3)
            total_keyword_occurrences += occurrences
    
    if matched_keywords == 0:
        return 0.0
    
    #base score: proportion of keywords matched (60% weight)
    base_score = matched_keywords / len(criterion_keywords)
    
    #frequency bonus: reward multiple keyword matches (40% weight)
    # normalize by potential max occurrences (num_keywords * 3)
    max_possible_occurrences = len(criterion_keywords) * 3
    frequency_score = total_keyword_occurrences / max_possible_occurrences
    
    #combined score (weighted average)
    relevance_score = (0.6 * base_score) + (0.4 * frequency_score)
    
    #ensure score is in [0, 1] range
    return min(relevance_score, 1.0)


def _normalize_text(text: str) -> str:
    #helper function to normalize text for matching
    return ' '.join(text.lower().split())


def _get_keyword_tokens(keyword: str) -> Set[str]:
    #helper function to extract word tokens from a keyword
    return set(re.findall(r'\b\w+\b', keyword.lower()))

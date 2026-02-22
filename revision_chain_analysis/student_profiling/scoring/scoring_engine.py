import yaml
from pathlib import Path




def load_thresholds():
    #Load scoring thresholds
   
    thresholds_path = Path(__file__).parent / 'scoring_thresholds.yaml'
    with open(thresholds_path, 'r') as file:
        thresholds = yaml.safe_load(file)
    return thresholds

def normalise_score(raw_value, thresholds):
    # Normalize score to be between 0 and 1, round to 2 decimal places
    if thresholds == 0:
        return 0.0
    
    return round(min(raw_value / thresholds, 1.0), 2)


def score_critical_thinking(ct_indicators, thresholds):
    #extract critical thinking thresholds
    ct_thresholds = thresholds['critical_thinking']

    #critical thinking required indictors
    required_indicators = ['explanation_prompts', 'verification_prompts', 'comparison_prompts', 'evidence_prompts']

    #check for missing indicators or thresholds
    for indicator in required_indicators:
        if indicator not in ct_indicators:
            raise ValueError(f"Missing critical thinking indicator: {indicator}")
        if indicator not in ct_thresholds:
            raise ValueError(f"Missing critical thinking threshold: {indicator}")
        
    #calculate critical thinking scores
    scores = {}
    for indicator in required_indicators:
        raw_value = ct_indicators[indicator]
        threshold = ct_thresholds[indicator]
        scores[indicator] = normalise_score(raw_value, threshold)

    return scores



def score_problem_solving(ps_indicators, thresholds):
    #extract problem solving thresholds
    ps_thresholds = thresholds['problem_solving']

    #problem solving required indicators
    required_indicators = ['decomposition_prompts', 'iterative_revision_count', 'self_proposed_content_turns', 'feedback_uptake_events']
    
    #check for missing indicators or thresholds
    for indicator in required_indicators:
        if indicator not in ps_indicators:
            raise ValueError(f"Missing problem solving indicator: {indicator}")
        if indicator not in ps_thresholds:
            raise ValueError(f"Missing problem solving threshold: {indicator}")
        
    #calculate problem solving scores
    scores = {}
    for indicator in required_indicators:
        raw_value = ps_indicators[indicator]
        threshold = ps_thresholds[indicator]
        scores[indicator] = normalise_score(raw_value, threshold)

    return scores

def score_engagement(eng_indicators, thresholds):
    #extract engagement thresholds
    eng_thresholds = thresholds['engagement']

    #engament required indicators
    required_indicators = ['student_token_ratio', 'student_turn_count', 'distinct_episode_types', 'session_minutes']
    
    #check for missing indicators or thresholds
    for indicator in required_indicators:
        if indicator not in eng_indicators:
            raise ValueError(f"Missing engagement indicator: {indicator}")
        if indicator not in eng_thresholds:
            raise ValueError(f"Missing engagement threshold: {indicator}")
        
    #calculate engagement scores
    scores = {}
    for indicator in required_indicators:
        raw_value = eng_indicators[indicator]
        threshold = eng_thresholds[indicator]
        scores[indicator] = normalise_score(raw_value, threshold)

    return scores

# Calculate all scores
def calculate_scores(ct_indicators, ps_indicators, eng_indicators, thresholds):
    ct_scores = score_critical_thinking(ct_indicators, thresholds)
    ps_scores = score_problem_solving(ps_indicators, thresholds)
    eng_scores = score_engagement(eng_indicators, thresholds)

    return {
        'critical_thinking': ct_scores,
        'problem_solving': ps_scores,
        'engagement': eng_scores
    }
    
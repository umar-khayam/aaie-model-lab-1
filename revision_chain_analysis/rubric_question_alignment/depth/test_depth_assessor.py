from depth_assessor import assess_all_criteria

# Simulates output from Keyword Matching Engine:
# prompts grouped by rubric criterion
prompts_by_criteria = {
    "criterion_1": [
        "What is supply chain visibility?",
        "Define the bullwhip effect"
    ],
    "criterion_2": [
        "How do I reduce inventory risk?",
        "Why does demand forecasting matter?"
    ],
    "criterion_3": [
        "Compare two forecasting models",
        "Evaluate the trade-offs between accuracy and explainability"
    ],
    # Multiple indicators in same criterion -> should return deep
    "criterion_4": [
        "What is X and how does it work?",
        "Compare X to Y and evaluate the trade-offs"
    ],
    "criterion_5": [
        "What is MFA? What is 2FA? What is SSO?",
        "How do they compare?"
    ],
    "criterion_6": [
    "Tell me about this topic"
    ],

}

rules_path = "revision_chain_analysis/rubric_question_alignment/depth/engagement_depth.yaml"

result = assess_all_criteria(prompts_by_criteria, rules_path)

print("Engagement depth per criterion:")
for criteria_id, depth in result.items():
    print(f"- {criteria_id}: {depth}")

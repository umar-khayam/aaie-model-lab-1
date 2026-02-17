from typing import Dict, List, Any, Optional
import json
import os


def build_output(
    submission_id: str,
    rubric_id: str,
    domain: str,
    alignment_summary: Dict[str, Any],
    criterion_coverages: List[Dict[str, Any]],
    flags: List[Dict[str, Any]],
    gaps_by_criterion: Dict[str, List[str]],
    depths_by_criterion: Dict[str, str],
    output_filepath: Optional[str] = None
) -> str:
    #assemble complete RQA output matching schema and save as JSON file.
    
    #build rubric_coverage array by merging data from all sources
    rubric_coverage = []
    
    for coverage in criterion_coverages:
        criteria_id = coverage["criteria_id"]
        
        #get gaps for this criterion
        criterion_gaps = gaps_by_criterion.get(criteria_id, [])
        
        #get engagement depth for this criterion
        engagement_depth = depths_by_criterion.get(criteria_id, "surface")
        
        #assemble complete criterion coverage
        criterion_entry = {
            "criteria_id": coverage["criteria_id"],
            "criteria_name": coverage["criteria_name"],
            "weight": coverage["weight"],
            "coverage_score": coverage["coverage_score"],
            "status": coverage["status"],
            "prompts_matched": coverage["prompts_matched"],
            "engagement_depth": engagement_depth,
            "gaps": criterion_gaps
        }
        
        rubric_coverage.append(criterion_entry)
    
    #assemble final output
    output = {
        "submission_id": submission_id,
        "rubric_id": rubric_id,
        "domain": domain,
        "alignment_summary": alignment_summary,
        "rubric_coverage": rubric_coverage,
        "flags": flags
    }
    
    #validate before saving
    validate_output(output)
    
    #determine output filepath
    if output_filepath is None:
        # Save in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_filepath = os.path.join(script_dir, f"{submission_id}.json")
    
    #save to JSON file
    save_output(output, output_filepath)
    
    return output_filepath


def validate_output(output: Dict[str, Any]) -> bool:
    #validate output structure against schema requirements.
 
    #check required top-level fields
    required_fields = ["submission_id", "rubric_id", "domain", 
                      "alignment_summary", "rubric_coverage"]
    for field in required_fields:
        assert field in output, f"Missing required field: {field}"
    
    #validate alignment_summary structure
    summary = output["alignment_summary"]
    assert "overall_alignment" in summary
    assert "status" in summary
    assert "total_prompts_analyzed" in summary
    assert "off_topic_prompts" in summary
    
    #validate alignment score range
    assert 0 <= summary["overall_alignment"] <= 1, "overall_alignment must be 0-1"
    
    #validate status enum
    valid_statuses = ["systematic_coverage", "broad_coverage", 
                     "partial_coverage", "minimal_coverage"]
    assert summary["status"] in valid_statuses, f"Invalid status: {summary['status']}"
    
    #validate rubric_coverage array
    assert isinstance(output["rubric_coverage"], list), "rubric_coverage must be list"
    
    for coverage in output["rubric_coverage"]:
        #check required fields
        required_coverage_fields = [
            "criteria_id", "criteria_name", "weight", "coverage_score",
            "status", "prompts_matched", "engagement_depth", "gaps"
        ]
        for field in required_coverage_fields:
            assert field in coverage, f"Coverage missing field: {field}"
        
        #validate ranges
        assert 0 <= coverage["weight"] <= 1, "weight must be 0-1"
        assert 0 <= coverage["coverage_score"] <= 1, "coverage_score must be 0-1"
        
        #validate enums
        valid_coverage_statuses = [
            "well_covered", "adequately_covered", 
            "undercovered", "significantly_undercovered"
        ]
        assert coverage["status"] in valid_coverage_statuses
        
        valid_depths = ["surface", "moderate", "deep"]
        assert coverage["engagement_depth"] in valid_depths
        
        #validate gaps is a list
        assert isinstance(coverage["gaps"], list), "gaps must be list"
    
    #validate flags if present
    if "flags" in output:
        assert isinstance(output["flags"], list), "flags must be list"
        
        for flag in output["flags"]:
            assert "type" in flag
            assert "severity" in flag
            assert "message" in flag
            assert "criteria_id" in flag
            
            valid_flag_types = ["rubric_gap", "coverage_issue", 
                               "quality_concern", "off_topic_questions"]
            assert flag["type"] in valid_flag_types
            
            valid_severities = ["high", "medium", "low"]
            assert flag["severity"] in valid_severities
    
    return True


def save_output(output: Dict[str, Any], filepath: str) -> None:
    #save output to JSON file.
   
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


def load_output(filepath: str) -> Dict[str, Any]:
    #load output from JSON file.
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

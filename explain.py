def generate_explanation(match_results):
    """
    Takes the structured result from matcher.match_jd_to_resume and generates
    human-readable explanations, categorizing matches and building actionable suggestions.
    
    Returns a dictionary of:
    {
        "overall_score": int,
        "strong_matches": list[dict],
        "partial_matches": list[dict],
        "missing_matches": list[dict],
        "suggestions": list[str]
    }
    """
    explanation = {
        "overall_score": match_results["overall_score"],
        "strong_matches": [],
        "partial_matches": [],
        "missing_matches": [],
        "suggestions": []
    }
    
    # Track categories for matches
    for category, matches in match_results["categories"].items():
        cat_friendly_name = category.replace("_", " ").title()
        
        for m in matches:
            jd_req = m["jd_requirement"]
            best_match = m["best_match_text"]
            section = m["best_match_section"]
            score = m["similarity_score"]
            match_type = m["match_type"]
            
            item = {
                "category": cat_friendly_name,
                "jd_requirement": jd_req,
                "best_match_text": best_match,
                "best_match_section": section.upper() if section else None,
                "similarity_score": round(score * 100)
            }
            
            if match_type == "strong":
                explanation["strong_matches"].append(item)
            elif match_type == "partial":
                explanation["partial_matches"].append(item)
                # Generate a specific suggestion for this partial match
                suggestion = (
                    f"**For '{jd_req}'**: Your resume mentions *'{best_match}'* (in {section.upper()}). "
                    f"This is semantically related but could be more explicit. "
                    f"**Action:** Rewrite this experience to explicitly use terminology like *'{jd_req}'*."
                )
                explanation["suggestions"].append(suggestion)
            else:
                explanation["missing_matches"].append(item)
                # Generate a suggestion for missing match
                suggestion = (
                    f"**Missing '{jd_req}'**: No matching content found in your resume. "
                    f"**Action:** If you have this experience, add a bullet point like: "
                    f"\"*Utilized/Led {jd_req} to optimize [Project/Process] resulting in [Quantifiable Impact]*\"."
                )
                explanation["suggestions"].append(suggestion)
                
    return explanation

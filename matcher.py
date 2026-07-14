import os
import time
import numpy as np
import requests
from sklearn.metrics.pairwise import cosine_similarity

HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

def get_embeddings(texts, model=None):
    """
    Generate embeddings using the HF Inference API (if HF_TOKEN is set)
    or fall back to a local SentenceTransformer model.
    Returns a numpy array of shape (N, 384).
    """
    if not texts:
        return np.empty((0, 384))

    if HF_TOKEN:
        # Use HF Inference API — no PyTorch needed, runs fine on 512MB RAM
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        for attempt in range(3):
            resp = requests.post(
                HF_API_URL,
                headers=headers,
                json={"inputs": texts, "options": {"wait_for_model": True}},
                timeout=60,
            )
            if resp.status_code == 200:
                return np.array(resp.json(), dtype=np.float32)
            if resp.status_code == 503:   # model loading on HF side
                time.sleep(10)
                continue
            raise RuntimeError(f"HF Inference API error {resp.status_code}: {resp.text}")
        raise RuntimeError("HF Inference API timed out after 3 retries.")
    else:
        # Local fallback (development / no HF_TOKEN)
        from functools import lru_cache

        @lru_cache(maxsize=1)
        def _get_local_model():
            from sentence_transformers import SentenceTransformer
            m = SentenceTransformer('all-MiniLM-L6-v2')
            m.eval()
            return m

        import torch
        mdl = _get_local_model()
        with torch.no_grad():
            return mdl.encode(texts, show_progress_bar=False,
                              normalize_embeddings=True, convert_to_numpy=True)


def match_jd_to_resume(resume_sections, jd_sections, threshold_strong=0.55, threshold_partial=0.35):
    """
    Matches each JD requirement against all resume chunks.
    Computes similarity scores and classifies them.
    
    Returns a dictionary structure:
    {
        "overall_score": float (0-100),
        "categories": {
            "required_skills": [MatchInfo],
            "preferred_skills": [MatchInfo],
            "responsibilities": [MatchInfo]
        }
    }
    """
    model = get_model()
    
    # Flatten all resume chunks and keep track of which section they came from
    resume_chunks = []
    resume_chunk_sources = []
    
    for section_name, chunks in resume_sections.items():
        for chunk in chunks:
            resume_chunks.append(chunk)
            resume_chunk_sources.append(section_name)
            
    if not resume_chunks:
        # Fallback if resume is empty or not parsed correctly
        return {
            "overall_score": 0.0,
            "categories": {
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": []
            }
        }
        
    # Generate embeddings for all resume chunks
    resume_embeddings = get_embeddings(resume_chunks, model)
    
    results = {
        "overall_score": 0.0,
        "categories": {
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": []
        }
    }
    
    total_requirements = 0
    scored_points = 0.0
    
    # Loop over JD categories
    for category in ["required_skills", "preferred_skills", "responsibilities"]:
        jd_chunks = jd_sections.get(category, [])
        if not jd_chunks:
            continue
            
        # Generate embeddings for JD chunks
        jd_embeddings = get_embeddings(jd_chunks, model)
        
        # Compute cosine similarity matrix
        # Shape: (len(jd_chunks), len(resume_chunks))
        sim_matrix = cosine_similarity(jd_embeddings, resume_embeddings)
        
        category_matches = []
        for i, jd_chunk in enumerate(jd_chunks):
            # Find the best match in the resume
            best_match_idx = np.argmax(sim_matrix[i])
            best_score = float(sim_matrix[i][best_match_idx])
            best_resume_chunk = resume_chunks[best_match_idx]
            best_resume_section = resume_chunk_sources[best_match_idx]
            
            # Classification
            if best_score >= threshold_strong:
                match_type = "strong"
                match_weight = 1.0
            elif best_score >= threshold_partial:
                match_type = "partial"
                match_weight = 0.5
            else:
                match_type = "missing"
                match_weight = 0.0
                
            match_info = {
                "jd_requirement": jd_chunk,
                "best_match_text": best_resume_chunk if match_type != "missing" else None,
                "best_match_section": best_resume_section if match_type != "missing" else None,
                "similarity_score": best_score,
                "match_type": match_type
            }
            category_matches.append(match_info)
            
            # Weighted scoring for overall score calculation
            # Required skills and responsibilities might be weighted higher in a real system,
            # but for now we weight everything equally. Required skills contribute to overall match.
            # Let's count them towards the overall score.
            total_requirements += 1
            scored_points += match_weight
            
        results["categories"][category] = category_matches
        
    # Calculate overall score out of 100
    if total_requirements > 0:
        results["overall_score"] = round((scored_points / total_requirements) * 100)
    else:
        results["overall_score"] = 0
        
    return results

def analyze_resume_and_jd(resume_file, filename, jd_text):
    """
    Orchestrates the entire parsing, embedding, matching, and explainability pipeline.
    
    resume_file: file-like object or file path
    filename: string name of the file (to detect extension)
    jd_text: plain text of the job description
    
    Returns the final explanation/suggestion structure.
    """
    from parser import (
        extract_text_from_pdf,
        extract_text_from_docx,
        extract_text_from_image,
        segment_resume,
        parse_job_description
    )
    from explain import generate_explanation

    # 1. Extract text from resume
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext == 'pdf':
        resume_text = extract_text_from_pdf(resume_file)
    elif ext in ('docx', 'doc'):
        resume_text = extract_text_from_docx(resume_file)
    elif ext in ('jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff', 'tif'):
        resume_text = extract_text_from_image(resume_file)
    else:
        raise ValueError(
            f"Unsupported format: .{ext}. "
            "Please upload a PDF, DOCX, or image file (JPG, PNG, WEBP)."
        )
        
    if not resume_text.strip():
        raise ValueError(
            "Could not extract any text from the uploaded file. "
            "Please ensure you upload a proper resume document (PDF, DOCX) or an image containing readable text."
        )

    # 1.5 Validation: Ensure the extracted text looks like a resume
    lower_text = resume_text.lower()
    
    # Check for structural section headers/keywords
    has_experience = any(kw in lower_text for kw in ['experience', 'employment', 'work history', 'professional background', 'working as'])
    has_education  = any(kw in lower_text for kw in ['education', 'academic', 'degree', 'university', 'college', 'school', 'graduated'])
    has_skills     = any(kw in lower_text for kw in ['skills', 'technologies', 'proficiencies', 'languages', 'tools'])
    has_projects   = any(kw in lower_text for kw in ['projects', 'key projects', 'personal projects', 'publications'])
    
    match_count = sum([has_experience, has_education, has_skills, has_projects])
    
    # A valid resume must have at least 400 characters and contain at least 2 distinct content groups
    if len(resume_text.strip()) < 400 or match_count < 2:
        raise ValueError(
            "The uploaded file does not appear to be a valid resume. "
            "Please ensure you upload a document containing typical sections such as Experience, Education, and Skills."
        )

    # 2. Segment resume
    resume_sections = segment_resume(resume_text)
    
    # 2.5 Structural Validation: Ensure the segmented sections contain actual resume structure
    # A generic paper, report, or document won't have headings that segment into skills, experience, or education.
    seg_skills = len(resume_sections.get("skills", [])) > 0
    seg_experience = len(resume_sections.get("experience", [])) > 0
    seg_education = len(resume_sections.get("education", [])) > 0
    seg_projects = len(resume_sections.get("projects", [])) > 0
    
    seg_match_count = sum([seg_skills, seg_experience, seg_education, seg_projects])
    
    # Require at least 2 structured segments to exist (so the document isn't just placed entirely into 'summary')
    if seg_match_count < 2:
        raise ValueError(
            "The uploaded file does not appear to be a valid resume. "
            "Please ensure you upload a document containing typical resume sections (such as Experience, Education, or Skills) with clear headings."
        )
    
    # 3. Parse JD
    jd_sections = parse_job_description(jd_text)
    
    # 4. Run similarity match
    match_results = match_jd_to_resume(resume_sections, jd_sections)
    
    # 5. Generate explanations and suggestions
    explanation = generate_explanation(match_results)
    
    return explanation

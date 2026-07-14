# 🎯 ResumeMatch AI

> **A semantic resume-to-job-description matcher powered by NLP sentence embeddings — not a keyword-counting ATS clone.**

Instead of looking for exact keyword matches, ResumeMatch AI converts your resume and job description into dense semantic vectors using `sentence-transformers (all-MiniLM-L6-v2)` and then computes cosine similarity across all requirement pairs. This means *"managed container deployments"* still matches *"Kubernetes orchestration"* because the model understands meaning, not just words.

---

## ✨ Features

- 📄 **Multi-format Resume Upload** — PDF, DOCX, and plain TXT support
- 🧠 **Semantic Matching** — `all-MiniLM-L6-v2` sentence embeddings (384 dimensions)
- 📊 **Overall Match Score (0–100%)** — weighted across all JD requirements
- 🟢 **Strong Matches** — JD requirements with strong semantic hits in your resume (≥55% similarity)
- 🟡 **Partial Matches** — Semantically related but not explicitly matching (35–55%)
- 🔴 **Missing Requirements** — Gaps to address before applying (<35%)
- 💬 **Explainability** — For each requirement, shows the best-matching resume snippet with similarity score
- 💡 **Improvement Suggestions** — Actionable rewriting advice for partial/missing items
- 🎨 **Premium UI** — Dark glassmorphism design with SVG score gauge and tabbed breakdown

---

## 🏗️ Architecture

```
resume_file (PDF/DOCX/TXT)
        │
        ▼
[ parser.py ]  ──── Text Extraction (pdfplumber / python-docx)
        │           Section Segmentation (regex heading detection)
        │           JD Parsing (required skills / preferred / responsibilities)
        ▼
[ matcher.py ] ──── Load all-MiniLM-L6-v2 (cached)
        │           Generate embeddings for resume chunks + JD requirements
        │           Compute cosine similarity matrix (scikit-learn)
        │           Score each requirement: strong / partial / missing
        ▼
[ explain.py ] ──── Human-readable explanations for each match
        │           Template-based improvement suggestions for partial/missing items
        ▼
[ app.py ]     ──── Streamlit UI: upload, analyze, visualize
```

### Why Semantic Similarity > Keyword Matching

| Approach | Example: Resume says... | JD requires... | Match? |
|----------|-------------------------|----------------|--------|
| **ATS Keyword Match** | "managed container deployments" | "Kubernetes" | ❌ No |
| **ResumeMatch AI** | "managed container deployments" | "Kubernetes" | ✅ Yes (semantic hit) |

A traditional ATS only matches `Kubernetes == Kubernetes`. ResumeMatch AI understands that container deployments and Kubernetes orchestration are semantically adjacent, giving a realistic picture of your fit.

---

## 📁 Project Structure

```
ResumeMatch AI/
├── app.py                  # Streamlit UI — entry point
├── matcher.py              # Embeddings, similarity scoring, pipeline orchestrator
├── parser.py               # Text extraction + section segmentation
├── explain.py              # Match explanation + improvement suggestions
├── requirements.txt        # Python dependencies
├── sample_data/
│   ├── sample_resume_1.txt # Synthetic: Full-stack developer resume
│   ├── sample_resume_2.txt # Synthetic: Data scientist resume
│   ├── sample_jd_1.txt     # Synthetic: Senior Full-Stack Engineer JD
│   ├── sample_jd_2.txt     # Synthetic: ML Engineer JD
│   └── sample_jd_3.txt     # Synthetic: Data Engineer JD
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+ (3.11 recommended)
- pip

### 1. Clone / navigate to the project directory

```bash
cd "ResumeMatch AI"
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ **First-run note:** On first run, `sentence-transformers` will automatically download the `all-MiniLM-L6-v2` model (~90 MB) from HuggingFace. Ensure you have an internet connection for this step. Subsequent runs are fully offline.

### 5. Run the app

```bash
streamlit run app.py
```

This will open your browser at `http://localhost:8501`.

---

## 🖥️ Usage

1. **Upload your resume** — Drag and drop a PDF, DOCX, or TXT file.
2. **Paste the job description** — Copy the full JD from LinkedIn, company site, etc.
3. **Click "Match & Analyze"** — The pipeline runs in ~3–8 seconds on CPU.
4. **Review results:**
   - **Score Gauge** — Visual overall match percentage.
   - **Strong Matches tab** — Requirements you clearly cover with source snippets.
   - **Partial Matches tab** — Semantically related experience worth highlighting more explicitly.
   - **Missing Matches tab** — Skills/experience gaps you may want to address.
   - **Improvement Suggestions tab** — Concrete rewriting advice.

### Quick Test with Sample Data

Use the **"Quick Testing (Sample Data)"** dropdown in the sidebar to auto-load one of the synthetic JDs, then upload the corresponding sample resume from `sample_data/`:

| Dropdown option | Resume file | JD file |
|----------------|-------------|---------|
| Senior Full-Stack Engineer JD + Dev Resume | `sample_resume_1.txt` | `sample_jd_1.txt` |
| ML Engineer JD + Data Scientist Resume | `sample_resume_2.txt` | `sample_jd_2.txt` |
| Data Engineer JD + Dev Resume | `sample_resume_1.txt` | `sample_jd_3.txt` |

---

## ⚙️ Similarity Thresholds

Thresholds are calibrated as constants in [`matcher.py`](matcher.py) based on empirical testing with `all-MiniLM-L6-v2`:

| Threshold | Value | Meaning |
|-----------|-------|---------|
| `STRONG_MATCH_THRESHOLD` | `0.55` | Cosine similarity ≥ 0.55 → Strong match |
| `PARTIAL_MATCH_THRESHOLD` | `0.35` | Cosine similarity 0.35–0.55 → Partial match |
| Below `PARTIAL_MATCH_THRESHOLD` | `< 0.35` | Missing / no meaningful match |

> **Note:** These thresholds are intentionally kept as internal constants and not surfaced in the UI. `all-MiniLM-L6-v2`'s cosine distribution is not perfectly calibrated out-of-the-box — these values were hand-tuned to give reasonable signal on typical resume/JD pairs. Adjust them in `matcher.py` if you find systematic over- or under-matching.

---

## 🧪 Testing

Run the pipeline standalone without Streamlit to verify the end-to-end flow:

```bash
# Test parser on sample resume
python -c "from parser import extract_text_from_file, segment_resume; \
  text = open('sample_data/sample_resume_1.txt').read(); \
  sections = segment_resume(text); \
  print(list(sections.keys()))"

# Test full pipeline (uses Streamlit caching stub)
python -c "
import os
os.environ['OMP_NUM_THREADS'] = '1'
from matcher import analyze_resume_and_jd
jd = open('sample_data/sample_jd_1.txt').read()
resume_bytes = open('sample_data/sample_resume_1.txt', 'rb').read()

class FakeFile:
    def __init__(self, data, name):
        self.data = data
        self.name = name
    def read(self):
        return self.data
    def getvalue(self):
        return self.data

result = analyze_resume_and_jd(FakeFile(resume_bytes, 'sample_resume_1.txt'), 'sample_resume_1.txt', jd)
print('Score:', result['overall_score'])
print('Strong:', len(result['strong_matches']))
print('Partial:', len(result['partial_matches']))
print('Missing:', len(result['missing_matches']))
"
```

---

## 🛠️ Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | ≥1.59.0 | Web UI framework |
| `sentence-transformers` | ≥5.6.0 | NLP embedding model loading + inference |
| `pdfplumber` | ≥0.11.10 | PDF text extraction |
| `python-docx` | ≥1.2.0 | DOCX text extraction |
| `scikit-learn` | ≥1.9.0 | Cosine similarity computation |

> **Model:** `sentence-transformers/all-MiniLM-L6-v2` — 80MB, 384-dim embeddings, ~14K sentences/sec on CPU. Fast enough for real-time interactive use.

---

## 🔮 Potential Improvements

- [ ] **DOCX section parsing** — currently relies on heading patterns; a heading-style-aware parser using `python-docx` paragraph styles would be more robust
- [ ] **Weighted scoring** — give higher weight to "required" vs. "preferred" skills in the JD
- [ ] **Threshold debug mode** — Streamlit slider to tune thresholds live (useful demo feature)
- [ ] **Export results** — Download a PDF/JSON summary of the match report
- [ ] **Resume rewrite assistant** — LLM-powered suggestions to rewrite resume bullets for better JD alignment
- [ ] **Batch mode** — Upload multiple JDs and rank them against one resume

---

## 📜 License

MIT License. Free to use, modify, and distribute.

---

*Built with ❤️ using Python, Streamlit, and HuggingFace sentence-transformers.*

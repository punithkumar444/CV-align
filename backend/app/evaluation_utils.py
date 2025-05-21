from app.schemas.evaluation import CVEvaluationResponse, EvaluationFeedback
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re
import fitz  # PyMuPDF

# load your embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_cv(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def clean_text(text: str) -> str:
    # lowercase, keep only letters and spaces
    text = text.lower()
    tokens = re.findall(r"\b[a-z]{2,}\b", text)
    return " ".join(tokens)

def evaluate_cv_against_job(cv_text: str, job_description: str) -> CVEvaluationResponse:
    cv_clean = clean_text(cv_text)
    job_clean = clean_text(job_description)

    # compute semantic similarity
    embeddings = model.encode([cv_clean, job_clean])
    similarity = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])

    # heuristics for strengths/weaknesses
    tech_keywords = ["python", "django", "fastapi", "react", "node", "mongodb", "sql", "aws", "docker"]
    soft_skills   = ["communication", "teamwork", "leadership", "problem solving"]

    strengths = [f"Mentions {kw}" for kw in tech_keywords + soft_skills if kw in cv_clean]
    weaknesses = [f"Job requires {kw}, not found in CV" for kw in tech_keywords + soft_skills if kw in job_clean and kw not in cv_clean]

    explanation = (
        "The candidate's CV is semantically "
        f"{'well' if similarity > 0.6 else 'moderately' if similarity > 0.3 else 'poorly'} aligned with the job description."
    )

    return CVEvaluationResponse(
        relevance_score=round(similarity, 2),
        feedback=EvaluationFeedback(
            strengths=strengths[:5],
            weaknesses=weaknesses[:5],
            role_fit_explanations=[explanation],
        ),
    )

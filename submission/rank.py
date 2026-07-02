#!/usr/bin/env python3
"""
IndiaRuns / Redrob Hackathon - Offline Candidate Ranker
Produces a spec-compliant top-100 submission CSV: candidate_id,rank,score,reasoning

Usage:
    python rank.py --candidates ./candidates.jsonl --out ./team_xxx.csv
    python rank.py --candidates ./candidates.jsonl --out ./team_xxx.csv --jd ./job_description.txt

Compute budget: CPU only, no network calls, target < 5 minutes wall-clock.
"""

import argparse
import csv
import gzip
import json
import logging
import os
import sys
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Ranker")

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    logger.error("Missing packages. Run: pip install sentence-transformers scikit-learn")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Fallback JD text (used only if --jd file is not supplied / not found).
# This mirrors the *meaning* of the released JD, not a literal keyword list,
# so the embedding target reflects what the role actually needs.
# ---------------------------------------------------------------------------
DEFAULT_JD_TEXT = """
Senior AI Engineer, founding team, Series A product company.
Needs 5 to 9 years total experience, most of it applied ML or AI engineering
at a product company, not a pure IT services / consulting shop.
Must have shipped a production embeddings-based retrieval, ranking, or
recommendation system to real users - not just tutorials or side projects.
Must have hands-on experience with vector search or hybrid search
infrastructure (FAISS, Pinecone, Weaviate, Qdrant, Elasticsearch, or similar),
strong Python, and experience designing evaluation frameworks for ranking
(NDCG, MRR, MAP, offline/online correlation).
Nice to have: LLM fine-tuning (LoRA/QLoRA), learning-to-rank models,
recruiting/HR-tech or marketplace domain, distributed systems, open source.
Does not want: pure research-only background with no production deployment,
people who have not written production code in 18+ months (pure architects),
career-long consulting-only experience (TCS, Infosys, Wipro, Accenture,
Cognizant, Capgemini) with no product-company experience, computer
vision/speech/robotics specialists with no NLP or IR exposure, and
title-chasers who switch companies every ~1.5 years for a bigger title.
Preferred location Pune or Noida, India, hybrid; open to relocation from
Tier-1 Indian cities. Prefers short (under 30 day) notice period.
"""

CONSULTING_FIRMS = {"tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini"}
CV_SPEECH_ROBOTICS_HINTS = {"computer vision", "speech recognition", "robotics", "autonomous"}
IR_ML_HINTS = {
    "embedding", "embeddings", "retrieval", "vector", "faiss", "pinecone",
    "weaviate", "qdrant", "elasticsearch", "opensearch", "milvus", "ranking",
    "recommendation", "recommender", "nlp", "llm", "rag", "search",
}


def load_jd_text(jd_path: str) -> str:
    if jd_path and os.path.exists(jd_path):
        with open(jd_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if text:
            logger.info(f"Loaded JD text from {jd_path} ({len(text)} chars).")
            return text
    logger.info("Using built-in fallback JD text.")
    return DEFAULT_JD_TEXT


def is_honeypot(data: dict) -> bool:
    """
    Cheap, explainable honeypot heuristic (no ML) based on the schema fields.
    Honeypots are described as 'subtly impossible profiles' - e.g. senior/
    expert claims with zero actual time behind them. We flag, we don't
    silently drop, so behavior stays auditable.
    """
    profile = data.get("profile", {})
    skills = data.get("skills", []) or []
    career = data.get("career_history", []) or []

    # Trap 1: "expert" proficiency in many skills with 0 months of use.
    expert_zero = sum(
        1 for s in skills
        if s.get("proficiency") == "expert" and int(s.get("duration_months", 0) or 0) == 0
    )
    if len(skills) > 0 and expert_zero >= 5:
        return True

    # Trap 2: total career duration_months wildly less than claimed years_of_experience.
    try:
        yoe = float(profile.get("years_of_experience", 0) or 0)
    except (ValueError, TypeError):
        yoe = 0.0
    total_months = sum(int(j.get("duration_months", 0) or 0) for j in career)
    if yoe >= 4 and total_months > 0 and (total_months / 12.0) < (yoe * 0.4):
        return True

    # Trap 3: current company founded after the candidate's own start_date there.
    for job in career:
        founded = job.get("company_founded_year")
        start = job.get("start_date")
        if founded and start:
            try:
                start_year = int(str(start)[:4])
                if int(founded) > start_year:
                    return True
            except (ValueError, TypeError):
                pass

    # Trap 4: "expert" self-rated skills with near-zero matching Redrob
    # assessment score, majority mismatch - inconsistent signal stack.
    signals = data.get("redrob_signals", {})
    assessments = signals.get("skill_assessment_scores", {}) or {}
    expert_names = {(s.get("name") or "").lower() for s in skills if s.get("proficiency") == "expert"}
    if expert_names and assessments:
        scored = {k.lower(): v for k, v in assessments.items()}
        mismatches = sum(1 for n in expert_names if scored.get(n, 100) < 20)
        if mismatches / len(expert_names) > 0.6:
            return True

    return False


def extract_features(data: dict) -> dict:
    profile = data.get("profile", {})
    signals = data.get("redrob_signals", {})
    skills = data.get("skills", []) or []
    career = data.get("career_history", []) or []

    try:
        yoe = float(profile.get("years_of_experience", 0) or 0)
    except (ValueError, TypeError):
        yoe = 0.0

    try:
        rr = float(signals.get("recruiter_response_rate", 0.0) or 0.0)
    except (ValueError, TypeError):
        rr = 0.0
    try:
        gh = float(signals.get("github_activity_score", -1.0))
    except (ValueError, TypeError):
        gh = -1.0
    try:
        notice = int(signals.get("notice_period_days", 90) or 90)
    except (ValueError, TypeError):
        notice = 90
    last_active = signals.get("last_active_date", "")
    open_to_work = bool(signals.get("open_to_work_flag", False))
    try:
        interview_rate = float(signals.get("interview_completion_rate", 0.5) or 0.5)
    except (ValueError, TypeError):
        interview_rate = 0.5

    is_stale = False
    if last_active:
        try:
            from datetime import date
            y, m, d = [int(x) for x in str(last_active)[:10].split("-")]
            days_inactive = (date.today() - date(y, m, d)).days
            is_stale = days_inactive > 180
        except (ValueError, TypeError):
            is_stale = False
    location = (profile.get("location") or "").lower()
    country = (profile.get("country") or "").lower()

    title = (profile.get("current_title") or "").lower()
    company = (profile.get("current_company") or "").lower()
    industry = (profile.get("current_industry") or "").lower()

    skill_names = {(s.get("name") or "").lower() for s in skills}
    ir_ml_overlap = len(skill_names & IR_ML_HINTS) + sum(
        1 for kw in IR_ML_HINTS if any(kw in sn for sn in skill_names)
    )

    # Job-hop rate: companies changed per year of experience (title-chaser trap).
    num_jobs = len(career)
    job_hop_rate = (num_jobs / yoe) if yoe > 0 else 0.0

    return {
        "candidate_id": data.get("candidate_id"),
        "title": profile.get("current_title", ""),
        "company": profile.get("current_company", ""),
        "location": profile.get("location", ""),
        "yoe": yoe,
        "gh": gh,
        "rr": rr,
        "notice": notice,
        "open_to_work": open_to_work,
        "last_active": last_active,
        "is_stale": is_stale,
        "interview_rate": interview_rate,
        "is_consulting": any(c in company for c in CONSULTING_FIRMS),
        "is_cv_speech_robo": any(h in (title + " " + industry) for h in CV_SPEECH_ROBOTICS_HINTS)
        and ir_ml_overlap == 0,
        "ir_ml_overlap": ir_ml_overlap,
        "job_hop_rate": job_hop_rate,
        "in_target_city": any(c in location for c in ["pune", "noida", "hyderabad", "mumbai", "delhi", "gurgaon", "bengaluru", "bangalore"]),
        "in_india": "india" in country or country == "",
        "raw_data": data,
    }


def format_text_for_embedding(cand: dict) -> str:
    """Career-narrative text for the embedding model, not a keyword bag."""
    data = cand["raw_data"]
    profile = data.get("profile", {})
    parts = [
        f"{profile.get('current_title', '')} at {profile.get('current_company', '')}, "
        f"{profile.get('years_of_experience', 0)} years experience.",
        profile.get("summary", ""),
    ]
    for job in data.get("career_history", [])[:4]:
        parts.append(f"{job.get('title', '')} at {job.get('company', '')}: {job.get('description', '')}")
    return "\n".join(p for p in parts if p)


def load_candidates(dataset_path: str) -> list:
    candidates = []
    honeypot_count = 0

    open_func = gzip.open if dataset_path.endswith(".gz") else open
    mode = "rt" if dataset_path.endswith(".gz") else "r"

    logger.info(f"Streaming dataset from {dataset_path}...")
    with open_func(dataset_path, mode, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not data.get("candidate_id"):
                continue  # guard: never rank a row with no id

            if is_honeypot(data):
                honeypot_count += 1
                continue  # never let honeypots reach the top-100

            candidates.append(extract_features(data))

    logger.info(f"Loaded {len(candidates)} candidates, skipped {honeypot_count} suspected honeypots.")
    return candidates


def prefilter(candidates: list, max_candidates: int = 3000) -> list:
    """
    Soft prioritization, not a hard cutoff on years-of-experience: the JD
    explicitly says 5-9 is a guideline, not a wall, and rewards strong
    signals outside the band. We rank by a cheap proxy score and cap the
    pool so the embedding step stays inside the compute budget.
    """
    def proxy(c):
        score = 0.0
        score += c["ir_ml_overlap"] * 2
        score += c["rr"] * 3
        score += max(c["gh"], 0) * 0.05
        score -= 3 if c["is_consulting"] else 0
        score -= 3 if c["is_cv_speech_robo"] else 0
        score -= 2 if c["job_hop_rate"] > 0.6 else 0
        score += 1 if c["in_target_city"] else 0
        score -= 2 if c["is_stale"] else 0
        score += 0.5 if c["open_to_work"] else 0
        score -= 1 if c["notice"] > 60 else 0
        return score

    if len(candidates) > max_candidates:
        candidates.sort(key=proxy, reverse=True)
        candidates = candidates[:max_candidates]
        logger.info(f"Pre-filtered pool to top {max_candidates} for embedding.")
    return candidates


def build_reasoning(cand: dict, sim: float) -> str:
    bits = [f"{cand['title'] or 'Unknown title'} ({cand['yoe']:.1f} yrs exp) at {cand['company'] or 'unknown company'}."]

    if cand["ir_ml_overlap"] > 0:
        bits.append("Profile shows direct retrieval/ranking/ML skill overlap with the JD.")
    else:
        bits.append("Limited explicit retrieval/ranking skill overlap; relying on career-history semantic match.")

    if cand["is_consulting"]:
        bits.append("Career is consulting-firm based, which the JD flags as a weaker fit.")
    if cand["is_cv_speech_robo"]:
        bits.append("Background leans CV/speech/robotics without clear NLP/IR exposure, a JD-stated concern.")
    if cand["job_hop_rate"] > 0.6:
        bits.append("Job-change frequency is high relative to experience, a title-chaser signal.")

    if cand["rr"] >= 0.6:
        bits.append(f"Strong recruiter response rate ({cand['rr']*100:.0f}%).")
    elif cand["rr"] < 0.2:
        bits.append(f"Low recruiter response rate ({cand['rr']*100:.0f}%), may be hard to reach.")

    if cand["gh"] > 30:
        bits.append(f"Solid GitHub activity score ({cand['gh']:.0f}).")

    if cand["is_stale"]:
        bits.append("Not active on Redrob recently (>6 months), availability uncertain.")
    elif cand["open_to_work"]:
        bits.append("Marked open to work.")

    if cand["notice"] > 60:
        bits.append(f"Long notice period ({cand['notice']} days), JD prefers under 30.")

    if not cand["in_target_city"] and not cand["in_india"]:
        bits.append("Located outside India; JD requires relocation willingness.")
    elif cand["in_target_city"]:
        bits.append("Located in a JD-preferred city.")

    bits.append(f"Semantic JD match score: {sim:.3f}.")
    return " ".join(bits)


def run_pipeline(args):
    start_time = time.time()
    logger.info("IndiaRuns Data & AI Challenge - Offline Ranker")

    if not os.path.exists(args.candidates):
        logger.error(f"Candidates file not found: {args.candidates}")
        sys.exit(1)

    jd_text = load_jd_text(args.jd)

    candidates = load_candidates(args.candidates)
    candidates = prefilter(candidates, max_candidates=args.max_pool)

    logger.info("Loading sentence-transformers (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    logger.info("Embedding job description...")
    jd_emb = model.encode([jd_text])

    logger.info(f"Embedding {len(candidates)} candidate narratives...")
    texts = [format_text_for_embedding(c) for c in candidates]
    cand_embs = model.encode(texts, batch_size=32, show_progress_bar=False)

    logger.info("Scoring...")
    sims = cosine_similarity(jd_emb, cand_embs)[0]

    results = []
    for i, cand in enumerate(candidates):
        sim = float(sims[i])
        score = sim

        score += min(0.10, 0.02 * cand["ir_ml_overlap"])  # scales with real overlap count, capped
        score += 0.05 if cand["gh"] > 50 else (0.02 if cand["gh"] > 0 else 0)
        score += 0.05 if cand["rr"] > 0.8 else 0
        score -= 0.10 if cand["is_consulting"] else 0
        score -= 0.10 if cand["is_cv_speech_robo"] else 0
        score -= 0.05 if cand["job_hop_rate"] > 0.6 else 0
        score += 0.03 if cand["in_target_city"] else 0
        score -= 0.15 if cand["is_stale"] else 0  # JD: not-actually-available candidates
        score += 0.02 if cand["open_to_work"] else 0
        score -= 0.03 if cand["notice"] > 60 else 0
        score += 0.02 if cand["interview_rate"] > 0.8 else 0
        score = max(0.0, min(1.0, score))

        results.append({
            "candidate_id": cand["candidate_id"],
            "score": round(score, 4),
            "reasoning": build_reasoning(cand, sim),
        })

    # Sort by score desc; break ties by candidate_id ascending (deterministic, per spec).
    results.sort(key=lambda r: (-r["score"], r["candidate_id"]))
    top_100 = results[:100]

    for idx, row in enumerate(top_100, start=1):
        row["rank"] = idx

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        for row in top_100:
            writer.writerow({
                "candidate_id": row["candidate_id"],
                "rank": row["rank"],
                "score": row["score"],
                "reasoning": row["reasoning"],
            })

    logger.info(f"Wrote {len(top_100)} rows to {args.out}")
    logger.info(f"Done in {time.time() - start_time:.1f}s.")


def parse_args():
    p = argparse.ArgumentParser(description="IndiaRuns offline candidate ranker")
    p.add_argument("--candidates", required=True, help="Path to candidates.jsonl or .jsonl.gz")
    p.add_argument("--out", required=True, help="Path to write the submission CSV")
    p.add_argument("--jd", default="job_description.txt", help="Path to job description text file (optional)")
    p.add_argument("--max-pool", type=int, default=3000, help="Max candidates to embed after pre-filter")
    return p.parse_args()


if __name__ == "__main__":
    run_pipeline(parse_args())

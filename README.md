# 🚀 Intelligent Candidate Discovery Platform

<p align="center">
  <img src="https://img.shields.io/badge/AI-Powered-success?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi"/>
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react"/>
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Gemini-LLM-orange?style=for-the-badge"/>
</p>

<p align="center">
AI-powered candidate ranking platform that intelligently analyzes resumes, ranks applicants, detects suspicious patterns, and provides explainable hiring recommendations.
</p>

---

# 🌟 Live Demo

🔗 **Demo:** https://bright-dolphin-df77cd.netlify.app

---

# 📖 Overview

Recruiters often spend hours manually reviewing resumes, leading to inconsistent and biased shortlisting.

The **Intelligent Candidate Discovery Platform** automates this process using AI-powered resume analysis, semantic search, explainable candidate ranking, and behavioral heuristic detection.

The platform is designed for:

- HR Teams
- Recruiters
- Hiring Managers
- Technical Interview Panels

---

# ✨ Key Features

## 🤖 AI Resume Ranking

- Semantic Resume Matching
- Candidate Scoring
- Skill Extraction
- Experience Evaluation
- Education Analysis

---

## 🔍 Intelligent Search

- FAISS Vector Search
- Dense Embeddings
- Semantic Candidate Retrieval
- Fast Similarity Search

---

## 🧠 Explainable AI

Every candidate receives:

- Overall Score
- Match Percentage
- Strengths
- Weaknesses
- AI-generated Hiring Reason
- Transparent Ranking Logic

---

## 🛡️ Behavioral Trap Detection

Detects suspicious resumes using heuristic rules such as:

- Keyword Stuffing
- Skill Inflation
- Experience Mismatch
- Inconsistent Resume Patterns

---

## 📊 Recruiter Dashboard

- Candidate Leaderboard
- Resume Ranking
- AI Insights
- Explainability Panel
- Detailed Candidate Reports

---

# ⚙️ Tech Stack

## Backend

- FastAPI
- Python
- FAISS
- Google Gemini API
- Sentence Transformers
- Pandas
- NumPy

---

## Frontend

- React
- JavaScript
- HTML5
- CSS3

---

## AI Components

- Resume Embeddings
- Semantic Similarity Search
- Rule-Based Explainability
- Candidate Ranking Engine
- Prompt Engineering

---

# 🏗️ System Architecture

```
                     Resume Dataset
                            │
                            ▼
                 Resume Parsing & Cleaning
                            │
                            ▼
                 Sentence Embedding Model
                            │
                            ▼
                    FAISS Vector Store
                            │
          ┌─────────────────┴────────────────┐
          ▼                                  ▼
 Semantic Candidate Search          Resume Ranking
          │                                  │
          └──────────────┬───────────────────┘
                         ▼
              Explainability Engine
                         │
                         ▼
               Recruiter Dashboard
```

---

# 📁 Project Structure

```
backend/
│
├── api/
├── ranking/
├── embeddings/
├── services/
├── utils/
└── main.py

frontend/
│
├── src/
├── public/
└── components/

data/

models/

README.md
```

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/Kajal805-M/IndiaRuns-candidate-ranker.git
cd IndiaRuns-candidate-ranker
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

# 📊 AI Pipeline

```
Resume Upload

        │

        ▼

Resume Parsing

        │

        ▼

Embedding Generation

        │

        ▼

FAISS Retrieval

        │

        ▼

Candidate Ranking

        │

        ▼

Gemini Explanation

        │

        ▼

Recruiter Dashboard
```

---

# 🎯 Use Cases

- Resume Shortlisting
- AI Candidate Ranking
- Technical Hiring
- Campus Recruitment
- Mass Hiring
- Recruitment Automation

---

# 📈 Future Improvements

- Multi-language Resume Support
- OCR for Image Resumes
- Interview Scheduling
- Email Notifications
- ATS Integration
- Voice-based Candidate Analysis
- Bias Detection
- Analytics Dashboard

---

# 👥 Team

| Name | Role |
|-------|------|
| **Kamal Vasa(Team Leader)** |AI/ML Engineer, Frontend Developer |
| **Kajal Maurya** | AI/ML Engineer, Backend |
| **Third Member Name** | AI Integration / Research |

---

# 🏆 Hackathon

Developed for the **IndiaRuns Data & AI Challenge**.

Focused on:

- Explainable AI
- Semantic Search
- Candidate Ranking
- AI-assisted Recruitment
- Fast Resume Discovery

---

# 📄 License

This project is intended for educational, research, and hackathon purposes.

---

# ⭐ Support

If you found this project helpful,

⭐ Star this repository

🍴 Fork it

💡 Share your feedback

---

<p align="center">
Made with ❤️ by Team IndiaRuns
</p>

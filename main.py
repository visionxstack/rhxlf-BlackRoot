from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
import json

load_dotenv()

# ─────────────────────────────────────────
# DB Setup — splits URL to safely encode password
# ─────────────────────────────────────────

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", ""))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={"sslmode": "require"}
)

def get_conn():
    return engine.connect()

# ─────────────────────────────────────────
# Lifespan (replaces deprecated on_event)
# ─────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — create tables if they don't exist
    with get_conn() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS students (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                skills JSONB DEFAULT '[]',
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS submissions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                student_id UUID REFERENCES students(id),
                score FLOAT NOT NULL CHECK (score BETWEEN 0 AND 1),
                mentor_quality FLOAT NOT NULL CHECK (mentor_quality BETWEEN 0 AND 1),
                week_label TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.commit()
    print(" Database tables ready")
    yield
    # Shutdown
    engine.dispose()
    print("🔌 Database connection closed")

app = FastAPI(title="Career Readiness API", lifespan=lifespan)

# ─────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────

class Skill(BaseModel):
    name: str
    level: float

class StudentCreate(BaseModel):
    name: str
    email: str
    skills: List[Skill] = []

class SubmissionCreate(BaseModel):
    student_id: str
    score: float
    mentor_quality: float
    week_label: str

class Job(BaseModel):
    title: str
    skills_required: List[str]

# ─────────────────────────────────────────
# Score Helpers
# ─────────────────────────────────────────

def compute_readiness(submissions: list) -> float:
    if not submissions:
        return 0.0
    last4 = submissions[-4:]
    avg_score = sum(s["score"] for s in last4) / len(last4)
    submission_rate = min(len(last4) / 4, 1.0)
    avg_mentor = sum(s["mentor_quality"] for s in last4) / len(last4)
    return round((avg_score * 0.50 + submission_rate * 0.30 + avg_mentor * 0.20) * 100, 2)

def compute_job_match(student_skills: list, required_skills: list, readiness: float) -> dict:
    student_names = {s["name"].lower() for s in student_skills}
    required_lower = [s.lower() for s in required_skills]
    matched = [s for s in required_lower if s in student_names]
    missing = [s for s in required_lower if s not in student_names]
    skill_match = len(matched) / len(required_lower) if required_lower else 0
    final_score = round((skill_match * 0.7 + (readiness / 100) * 0.3) * 100, 2)
    return {
        "skill_match_pct": round(skill_match * 100, 2),
        "final_score": final_score,
        "matched_skills": matched,
        "missing_skills": missing
    }

# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Career Readiness API is running "}

@app.post("/students")
def create_student(student: StudentCreate):
    with get_conn() as conn:
        result = conn.execute(text("""
            INSERT INTO students (name, email, skills)
            VALUES (:name, :email, CAST(:skills AS jsonb))
            RETURNING *
        """), {
            "name": student.name,
            "email": student.email,
            "skills": json.dumps([s.model_dump() for s in student.skills])
        })
        conn.commit()
        row = result.mappings().fetchone()
        return {"message": "Student created", "student": dict(row)}

@app.get("/students")
def list_students():
    with get_conn() as conn:
        result = conn.execute(text("SELECT * FROM students ORDER BY created_at DESC"))
        return {"students": [dict(r) for r in result.mappings().fetchall()]}


@app.get("/students/{student_id}")
def get_student(student_id: str):
    with get_conn() as conn:
        result = conn.execute(
            text("SELECT * FROM students WHERE id = :id"),
            {"id": student_id}
        )
        row = result.mappings().fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Student not found")
        return dict(row)


@app.post("/submissions")
def add_submission(sub: SubmissionCreate):
    with get_conn() as conn:
        result = conn.execute(text("""
            INSERT INTO submissions (student_id, score, mentor_quality, week_label)
            VALUES (:student_id, :score, :mentor_quality, :week_label)
            RETURNING *
        """), sub.dict())
        conn.commit()
        row = result.mappings().fetchone()
        return {"message": "Submission recorded", "submission": dict(row)}


@app.get("/students/{student_id}/readiness")
def get_readiness(student_id: str):
    with get_conn() as conn:
        student = conn.execute(
            text("SELECT * FROM students WHERE id = :id"),
            {"id": student_id}
        ).mappings().fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        subs = conn.execute(text("""
            SELECT score, mentor_quality FROM submissions
            WHERE student_id = :id ORDER BY created_at ASC
        """), {"id": student_id}).mappings().fetchall()

    readiness = compute_readiness([dict(s) for s in subs])
    alert = " Mentor intervention recommended — readiness below 40" if readiness < 40 else None

    return {
        "student_id": student_id,
        "student_name": student["name"],
        "readiness_score": readiness,
        "submissions_used": min(len(subs), 4),
        "alert": alert
    }


@app.post("/jobs/match")
def match_job(student_id: str, job: Job):
    with get_conn() as conn:
        student = conn.execute(
            text("SELECT * FROM students WHERE id = :id"),
            {"id": student_id}
        ).mappings().fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        subs = conn.execute(text("""
            SELECT score, mentor_quality FROM submissions
            WHERE student_id = :id ORDER BY created_at ASC
        """), {"id": student_id}).mappings().fetchall()

    readiness = compute_readiness([dict(s) for s in subs])
    skills = student["skills"] if student["skills"] else []
    match = compute_job_match(skills, job.skills_required, readiness)

    return {
        "student_name": student["name"],
        "job_title": job.title,
        "readiness_score": readiness,
        **match,
        "summary": f"You are {match['final_score']}% fit for {job.title}. Missing: {', '.join(match['missing_skills']) or 'None'}"
    }


@app.get("/leaderboard")
def leaderboard():
    with get_conn() as conn:
        students = conn.execute(text("SELECT * FROM students")).mappings().fetchall()
        scores = []
        for s in students:
            subs = conn.execute(text("""
                SELECT score, mentor_quality FROM submissions
                WHERE student_id = :id ORDER BY created_at ASC
            """), {"id": s["id"]}).mappings().fetchall()
            readiness = compute_readiness([dict(sub) for sub in subs])
            scores.append({
                "student_id": str(s["id"]),
                "name": s["name"],
                "readiness_score": readiness
            })

    scores.sort(key=lambda x: x["readiness_score"], reverse=True)
    return {"leaderboard": scores}

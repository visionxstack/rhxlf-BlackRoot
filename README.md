# 🎓 Career Readiness API

A hackathon project that tracks student progress and predicts job readiness using a dynamic scoring engine. Built with **FastAPI** + **Supabase (PostgreSQL)**.

---

## 🚨 The Problem

Educational institutions and bootcamps struggle to answer one critical question: **"Is this student actually ready for a job?"**

Today, student progress is tracked through disconnected metrics — assignment scores in one place, attendance in another, mentor feedback somewhere else. There is no single source of truth. Employers have no reliable way to trust a candidate's readiness, and mentors often only notice a struggling student when it's too late to help.

- Students complete programs without knowing how job-ready they actually are
- Mentors have no early warning system to identify who needs intervention
- Employers cannot objectively compare candidates from the same program
- Career matching is done manually or based on gut feeling, not data

---

## 💡 Our Solution

A **Career Readiness Score Engine** — a backend API that continuously tracks student progress and produces a single, transparent 0–100 score based on three real signals: performance, consistency, and mentor quality.

When a student is matched against a job, the system dynamically compares their skills against the role's requirements and combines that with their readiness score — producing an objective fit percentage and a clear list of what they're missing.

This isn't a static report card. Every submission logged, every mentor rating recorded, and every job match run feeds back into a living score that reflects real progress over time — making career readiness **measurable, actionable, and honest**.

### Who It Serves

| Stakeholder | What they get |
|-------------|---------------|
| Students | A real-time score that shows exactly where they stand |
| Mentors | Automatic alerts when a student drops below readiness threshold |
| Employers | A trusted, data-backed signal instead of just a certificate |

---

## 🧠 How It Works

The system revolves around one core idea: **a single score that represents how ready a student is for a job**.

### Career Readiness Score Formula

```
readiness_score = (
  avg_score_last_4_submissions × 0.50 +
  submission_rate_last_4_weeks  × 0.30 +
  avg_mentor_quality_rating     × 0.20
) × 100
```

| Component | Weight | What it measures |
|---|---|---|
| Performance | 50% | How well the student scores in recent assessments (0–1) |
| Consistency | 30% | How regularly they submit work over the last 4 weeks |
| Quality | 20% | Mentor feedback rating on their work (0–1) |

This gives a single **0–100 score** that updates every time a new submission is logged.

### Job Match Formula

Each job defines required skills. Each student has skills with proficiency levels. The system compares them dynamically:

```
skill_match  = matched_skills / required_skills
final_score  = (skill_match × 0.7) + (readiness_score/100 × 0.3)
```

**Result:** `"You are 60.58% fit for React Developer. Missing: css, typescript"`

This adapts to **any role** — no hardcoded categories. Pass any job with any skills and it calculates on the spot.

---

## 🗂️ Project Structure

```
career-readiness-api/
├── main.py          # All API logic
├── .env             # Secret credentials (never commit this)
└── requirements.txt # Python dependencies
```

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure `.env`

```env
DB_USER=postgres.your_project_id
DB_PASSWORD=your_raw_password_here
DB_HOST=aws-1-ap-southeast-1.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
```

> Paste your raw password — the code encodes special characters automatically.

### 3. Run the server

```bash
uvicorn main:app --reload
```

Server starts at `http://localhost:8000`

> Tables are **auto-created** on first startup — no SQL setup needed.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/students` | Create a student |
| GET | `/students` | List all students |
| GET | `/students/{id}` | Get one student |
| POST | `/submissions` | Log a weekly submission |
| GET | `/students/{id}/readiness` | Get readiness score |
| POST | `/jobs/match?student_id={id}` | Match student to a job |
| GET | `/leaderboard` | Ranked list of all students |

---

## 🧪 Testing with curl (Git Bash)

> ⚠️ **Git Bash tip:** Always use single-line commands. Multi-line `\` continuations break in Git Bash.

### 1. Health check
```bash
curl -s http://localhost:8000/ | python -m json.tool
```

### 2. Create a student
```bash
curl -s -X POST http://localhost:8000/students -H "Content-Type: application/json" -d "{\"name\":\"Alice\",\"email\":\"alice@example.com\",\"skills\":[{\"name\":\"React\",\"level\":70},{\"name\":\"JavaScript\",\"level\":60},{\"name\":\"Python\",\"level\":80}]}" | python -m json.tool
```
> 📋 Copy the `id` from the response — paste it in place of `PASTE_ID_HERE` below.

### 3. Create a second student (for leaderboard)
```bash
curl -s -X POST http://localhost:8000/students -H "Content-Type: application/json" -d "{\"name\":\"Bob\",\"email\":\"bob@example.com\",\"skills\":[{\"name\":\"CSS\",\"level\":50},{\"name\":\"JavaScript\",\"level\":40}]}" | python -m json.tool
```

### 4. List all students
```bash
curl -s http://localhost:8000/students | python -m json.tool
```

### 5. Get one student
```bash
curl -s http://localhost:8000/students/PASTE_ID_HERE | python -m json.tool
```

### 6. Log 4 submissions (run all 4 one by one)
```bash
curl -s -X POST http://localhost:8000/submissions -H "Content-Type: application/json" -d "{\"student_id\":\"PASTE_ID_HERE\",\"score\":0.85,\"mentor_quality\":0.90,\"week_label\":\"2025-W15\"}" | python -m json.tool
```
```bash
curl -s -X POST http://localhost:8000/submissions -H "Content-Type: application/json" -d "{\"student_id\":\"PASTE_ID_HERE\",\"score\":0.75,\"mentor_quality\":0.80,\"week_label\":\"2025-W16\"}" | python -m json.tool
```
```bash
curl -s -X POST http://localhost:8000/submissions -H "Content-Type: application/json" -d "{\"student_id\":\"PASTE_ID_HERE\",\"score\":0.90,\"mentor_quality\":0.95,\"week_label\":\"2025-W17\"}" | python -m json.tool
```
```bash
curl -s -X POST http://localhost:8000/submissions -H "Content-Type: application/json" -d "{\"student_id\":\"PASTE_ID_HERE\",\"score\":0.88,\"mentor_quality\":0.85,\"week_label\":\"2025-W18\"}" | python -m json.tool
```

### 7. Get readiness score
```bash
curl -s http://localhost:8000/students/PASTE_ID_HERE/readiness | python -m json.tool
```

### 8. Match student to a React Developer role
```bash
curl -s -X POST "http://localhost:8000/jobs/match?student_id=PASTE_ID_HERE" -H "Content-Type: application/json" -d "{\"title\":\"React Developer\",\"skills_required\":[\"React\",\"JavaScript\",\"CSS\",\"TypeScript\"]}" | python -m json.tool
```

### 9. Match to a Python Backend role
```bash
curl -s -X POST "http://localhost:8000/jobs/match?student_id=PASTE_ID_HERE" -H "Content-Type: application/json" -d "{\"title\":\"Python Backend Developer\",\"skills_required\":[\"Python\",\"FastAPI\",\"PostgreSQL\",\"Docker\"]}" | python -m json.tool
```

### 10. Match to a Data Analyst role
```bash
curl -s -X POST "http://localhost:8000/jobs/match?student_id=PASTE_ID_HERE" -H "Content-Type: application/json" -d "{\"title\":\"Data Analyst\",\"skills_required\":[\"Python\",\"SQL\",\"Tableau\",\"Excel\"]}" | python -m json.tool
```

### 11. Leaderboard
```bash
curl -s http://localhost:8000/leaderboard | python -m json.tool
```

---

## 🗄️ Database Schema

### `students`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Auto-generated primary key |
| name | TEXT | Student name |
| email | TEXT | Unique email |
| skills | JSONB | Array of `{name, level}` objects |
| created_at | TIMESTAMPTZ | Auto timestamp |

### `submissions`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Auto-generated primary key |
| student_id | UUID | Foreign key → students |
| score | FLOAT | Assessment score (0.0 – 1.0) |
| mentor_quality | FLOAT | Mentor rating (0.0 – 1.0) |
| week_label | TEXT | e.g. `"2025-W18"` |
| created_at | TIMESTAMPTZ | Auto timestamp |

---

## ⚠️ Alerts

The readiness endpoint automatically flags struggling students:

```json
{
  "readiness_score": 32.5,
  "alert": "⚠️ Mentor intervention recommended — readiness below 40"
}
```

---

## 🔍 Interactive Docs

While the server is running, visit:

```
http://localhost:8000/docs
```

Full Swagger UI — test every endpoint in the browser. Great for demos.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| FastAPI | Web framework |
| SQLAlchemy | Database ORM / query builder |
| psycopg2 | PostgreSQL driver |
| Supabase | Hosted PostgreSQL database |
| python-dotenv | Load secrets from `.env` |
| Pydantic | Request validation |


## Author 
Built by Team BlackRoot for Relay Hack X Leapfrog Connect Design Sprint 2.



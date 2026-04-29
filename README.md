# LeapFrog Connect 🇳🇵

> A Skills-to-Jobs platform built for Nepal — connecting learners to employment through AI-powered career intelligence.

---

## What We're Building

LeapFrog Connect is a unified web platform that bridges the gap between education and employment in Nepal. It combines a **Learning Management System (LMS)** with an **AI-powered Career Engine** and an **Employer Talent Portal** — creating a full pipeline from skill-building to job placement.

Think of it as **LinkedIn + Udemy + AI Career Coach**, built specifically for the Nepali market.

The core problem we solve: Leapfrog trainees complete courses, but no one can tell — in real time — who is becoming job-ready and who is quietly falling behind. By the time final evaluations happen, it's too late to intervene. Our platform makes that visible before it matters.

---

## The Core Loop

```
Student learns → gets assessed → AI scores readiness →
mentor intervenes if needed → employer sees vetted talent →
student gets hired → loop repeats with next cohort
```

Every feature in this platform serves that single loop.

---

## Who Uses It

### Student / Candidate
- Creates a verified profile with skills, education, and experience
- Browses and enrolls in courses
- Takes quizzes and earns certificates
- Tracks their Career Readiness Score week by week
- Gets AI-powered skill gap analysis against real job postings
- Applies for jobs with a shareable public profile link

### Company / Employer
- Posts job openings with required skills
- Browses a vetted, scored talent pool
- Gets AI-ranked candidates by job fit percentage
- Manages hiring pipeline: Applied → Interview → Hired (Kanban board)
- Receives mentor-verified candidate data — not just self-reported claims

### Admin (Leapfrog Staff)
- Manages courses, users, and job listings
- Issues certificates after assessment completion
- Views analytics: enrollment trends, placement rates, cohort performance
- Receives mentor alert dashboard for at-risk students

---

## AI Features (Powered by Claude API)

### 1. Skill Gap Analyzer
Student clicks on a job posting → AI reads their profile + the job description and returns:
> *"You're missing React and REST APIs. Based on your current track, take these 2 courses to close the gap."*

### 2. Talent Matcher
Company posts a job → AI scores every candidate in the talent pool by fit percentage.
> *"Aarav Sharma — 91% match | Missing: Docker"*

### 3. Career Readiness Score Engine
Runs weekly per student. Weighs assessment scores, submission rate, and mentor feedback into a single 0–100 score. Tracks growth over time. Fires mentor alerts when the score drops for 2 consecutive weeks.

```
readiness_score = (
  avg_score_last_4_submissions × 0.50 +
  submission_rate_last_4_weeks  × 0.30 +
  avg_mentor_quality_rating     × 0.20
) × 100
```

### 4. AI Interview Prep
When an employer requests an interview, Claude auto-generates 5 personalized practice questions based on the job description and the candidate's specific skill gaps.

### 5. Course Recommender
Based on a student's career goal and current score, AI recommends which courses to take next.

---

## Pages We're Building

### Public (no login required)
- Landing page
- Course catalog
- Job board
- Login & Register

### Student Portal
- Dashboard (score trend, enrolled courses, applied jobs, certificates)
- My Profile (skills, education, experience)
- Course detail + enrollment
- Quiz / Assessment
- My Certificates
- Job listings + Apply
- AI Skill Gap Checker

### Employer Portal
- Dashboard (job posts, applicants)
- Post a Job
- Candidate Pool (browse verified students)
- AI Talent Matcher
- Recruitment Funnel (Kanban board)

### Admin Portal
- Analytics dashboard
- Manage Users
- Manage Courses
- Manage Jobs
- Issue Certificates

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Tailwind CSS |
| Backend | Python / FastAPI |
| Database | PostgreSQL (Supabase) |
| AI | Claude API (Anthropic) |
| Frontend hosting | Vercel |
| Backend hosting | Render |
| Database hosting | Supabase (free tier) |

---

## Database Structure (Core Collections)

### users
```json
{
  "id": "uuid",
  "full_name": "Aarav Sharma",
  "email": "aarav@gmail.com",
  "role": "student",
  "skills": ["Python", "Django"],
  "education": "BSc Computer Science",
  "bio": "Aspiring backend developer...",
  "courses_enrolled": ["course_001"],
  "created_at": "2025-04-01T00:00:00Z"
}
```

### courses
```json
{
  "id": "course_001",
  "title": "Python for Beginners",
  "description": "Learn Python from scratch",
  "instructor": "Ram Bahadur",
  "duration": "4 weeks",
  "modules": ["Intro", "Variables", "Functions"],
  "has_quiz": true,
  "has_certificate": true
}
```

### assessments + submissions
```json
{
  "submission_id": "sub_001",
  "assessment_id": "assess_001",
  "user_id": "uuid",
  "score": 84,
  "submitted_at": "2025-04-15T10:30:00Z",
  "reviewed_at": "2025-04-16T09:00:00Z"
}
```

### readiness_scores (time-series — one row per student per week)
```json
{
  "id": "rs_001",
  "user_id": "uuid",
  "score": 76,
  "week_number": 14,
  "year": 2025,
  "computed_at": "2025-04-06T00:00:00Z"
}
```

### jobs
```json
{
  "id": "job_001",
  "title": "React Developer",
  "company": "Leapfrog Technology",
  "skills_required": ["React", "JavaScript", "REST API"],
  "location": "Kathmandu",
  "deadline": "2025-06-01"
}
```

### applications
```json
{
  "id": "app_001",
  "student_id": "uuid",
  "job_id": "job_001",
  "status": "Interview",
  "applied_date": "2025-05-01T00:00:00Z"
}
```

### alerts
```json
{
  "id": "alert_001",
  "user_id": "uuid",
  "mentor_id": "uuid",
  "alert_type": "score_drop",
  "message": "Score dropped for 2 consecutive weeks (76 → 68 → 61)",
  "resolved": false,
  "created_at": "2025-04-20T08:00:00Z"
}
```

---

## Core API Endpoints

### Submissions
| Method | Endpoint | Description |
|---|---|---|
| POST | `/submissions` | Submit an assessment answer |
| GET | `/submissions/:id` | Get a specific submission |
| POST | `/feedback` | Mentor reviews a submission |

### Career Readiness
| Method | Endpoint | Description |
|---|---|---|
| GET | `/score?user_id=X` | Get current readiness score |
| GET | `/score/trend?user_id=X` | Get 8-week score history |
| POST | `/score/compute` | Recompute score + fire alerts if needed |

### Alerts
| Method | Endpoint | Description |
|---|---|---|
| GET | `/alerts?mentor_id=X` | List unresolved alerts for a mentor |
| GET | `/alerts/student?user_id=X` | Get alerts for a specific student |
| PATCH | `/alerts/:id` | Resolve an alert |

### Talent Pool
| Method | Endpoint | Description |
|---|---|---|
| GET | `/talent-pool` | Get all candidates ranked by score |
| GET | `/talent-pool/filter` | Filter by skill, score, track |
| GET | `/talent-pool/:id` | Get one candidate's full profile |

### AI (Claude API)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/ai/skill-gap` | Analyze gap between profile and job |
| POST | `/ai/match-candidates` | Score and rank candidates for a job |
| POST | `/ai/interview-prep` | Generate interview practice questions |
| POST | `/ai/recommend-courses` | Suggest next courses for a student |

---

## System Architecture

```
Browser (React + Tailwind)
        ↓
    Vercel (Frontend)
        ↓
  FastAPI REST API (Render)
     ↙          ↘
PostgreSQL      Claude API
(Supabase)    (Anthropic)
```

---

## Non-Functional Requirements

| Requirement | Target |
|---|---|
| Uptime | 99.5% |
| Page load | < 3 seconds |
| API response | < 500ms (non-AI endpoints) |
| Security | JWT auth, OWASP standards |
| Localization | English + Nepali (i18n) |

---

## What Makes This Different

Most LMS platforms show you what a student *did*. LeapFrog Connect shows what a student is *becoming* — and surfaces that signal to the people who need to act on it (mentors and employers) before it's too late.

The Career Readiness Score is not a grade. It is a continuous, AI-informed signal that converts training activity into employment potential. Every employer sees verified, time-tracked evidence — not a self-reported resume.

---

## Success Criteria

> A secure, localized, high-performance platform that successfully converts Leapfrog trainees into employed professionals through a seamless, data-driven digital experience.

**The demo day story in one sentence:**
A student sees their skill gap, takes the recommended course, their readiness score goes up, and the right employer is notified — all automatically.

---

## Team

Built for Relay Hack × Leapfrog Connect Hackathon, Sprint 2.

---

## License

MIT

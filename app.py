"""
FastAPI Backend Application for Jayanthi's Full-Stack Portfolio.
Serves RESTful APIs for projects, skills, contact messages, analytics, and static frontend files.
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr, Field

import database

# Initialize database schema and data
database.init_db()

app = FastAPI(
    title="Jayanthi | Full-Stack Portfolio API",
    description="REST API backend powering Jayanthi's personal portfolio, projects showcase, skill endorsements, and contact inquiries.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for flexible development and cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PORTFOLIO_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(PORTFOLIO_DIR, "images")

# Pydantic Schemas
class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Sender's full name")
    email: str = Field(..., description="Valid contact email address")
    subject: Optional[str] = Field("General Inquiry", max_length=150, description="Subject of the message")
    message: str = Field(..., min_length=5, max_length=2500, description="Inquiry or message text")

# --- API Endpoints ---

@app.get("/api/profile", tags=["Profile"])
def get_profile() -> Dict[str, Any]:
    """Returns developer bio, status, headline, and social links."""
    stats = database.get_stats()
    return {
        "name": "Jayanthi",
        "headline": "Cyber Security Student & Full Stack Developer",
        "tagline": "Passionate about building resilient, responsive, and secure web applications with Java, Spring Boot, Python, and modern web architectures.",
        "status": "Available for Software Engineering Roles & Internships",
        "email": "arpulajayanthi@gmail.com",
        "location": "Telangana, India",
        "socials": {
            "github": "https://arpulajayanthi.github.io/jayanthi-portfolio/",
            "linkedin": "https://www.linkedin.com/in/arpula-jayanthi-a68a81425"
        },
        "stats": stats
    }

@app.get("/api/projects", tags=["Projects"])
def list_projects(category: Optional[str] = Query(None, description="Filter by category (e.g. 'Full Stack', 'Cyber Security', 'Backend')"),
                  search: Optional[str] = Query(None, description="Search keyword in title, description, or technologies")):
    """Returns a list of portfolio projects with optional category filter and keyword search."""
    projects = database.get_all_projects(category=category, search=search)
    return {"count": len(projects), "projects": projects}

@app.post("/api/projects/{project_id}/like", tags=["Projects"])
def like_project(project_id: int):
    """Atomically increments the like count for a specific project."""
    updated_likes = database.increment_project_like(project_id)
    if updated_likes is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "project_id": project_id, "likes": updated_likes}

@app.get("/api/skills", tags=["Skills"])
def list_skills():
    """Returns all technical skills with endorsement counts and proficiency scores."""
    skills = database.get_all_skills()
    
    # Also group by category for frontend convenience
    categories: Dict[str, List[Dict[str, Any]]] = {}
    for skill in skills:
        cat = skill["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill)
        
    return {
        "total": len(skills),
        "skills": skills,
        "categories": categories
    }

@app.post("/api/skills/{skill_id}/endorse", tags=["Skills"])
def endorse_skill(skill_id: int):
    """Increments the community endorsement count for a skill."""
    updated_count = database.increment_skill_endorsement(skill_id)
    if updated_count is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"success": True, "skill_id": skill_id, "endorsements": updated_count}

@app.post("/api/contact", tags=["Contact"], status_code=status.HTTP_201_CREATED)
def submit_contact(payload: ContactRequest):
    """Receives, validates, and stores a new message from the contact form."""
    if not payload.name.strip() or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Name and message cannot be empty")
        
    msg_id = database.save_contact_message(
        name=payload.name,
        email=payload.email,
        subject=payload.subject or "General Inquiry",
        message=payload.message
    )
    return {
        "success": True,
        "message": f"Thank you {payload.name.strip()}! Your message has been received securely.",
        "message_id": msg_id
    }

@app.get("/api/admin/messages", tags=["Admin"])
def get_admin_messages():
    """Retrieves all submitted messages for the owner / recruiter demo inbox view."""
    messages = database.get_all_messages()
    return {"count": len(messages), "messages": messages}

@app.delete("/api/admin/messages/{message_id}", tags=["Admin"])
def remove_admin_message(message_id: int):
    """Deletes a contact message."""
    deleted = database.delete_message(message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"success": True, "deleted_id": message_id}

@app.get("/api/stats", tags=["Analytics"])
def get_site_stats():
    """Returns live metrics including visits, likes, endorsements, and project count."""
    return database.get_stats()

@app.post("/api/stats/visit", tags=["Analytics"])
def register_visit():
    """Increments total visitor counter on page load."""
    new_visits = database.record_visit()
    return {"visits": new_visits}

# --- Static File Serving ---

# Serve images if directory exists
if os.path.exists(IMAGES_DIR):
    app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

@app.get("/style.css", include_in_schema=False)
def serve_css():
    css_path = os.path.join(PORTFOLIO_DIR, "style.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="style.css not found")

@app.get("/script.js", include_in_schema=False)
def serve_js():
    js_path = os.path.join(PORTFOLIO_DIR, "script.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="script.js not found")

@app.get("/", include_in_schema=False)
def serve_home():
    index_path = os.path.join(PORTFOLIO_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return HTMLResponse("<h1>Portfolio Loaded</h1><p>index.html not found</p>")

if __name__ == "__main__":
    import uvicorn
    print("Starting Jayanthi's Full-Stack Portfolio Server at http://127.0.0.1:8000")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

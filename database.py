"""
Database module for Jayanthi's Full-Stack Portfolio.
Handles SQLite database initialization, schema creation, seeding, and CRUD operations.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "portfolio.db")

def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database tables and seeds initial data if empty."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                technologies TEXT NOT NULL,
                github_url TEXT,
                live_url TEXT,
                likes INTEGER DEFAULT 0,
                featured INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Skills table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                icon_tag TEXT,
                proficiency INTEGER DEFAULT 80,
                endorsements INTEGER DEFAULT 0
            )
        """)
        
        # Messages / Contact inquiries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Site statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS site_stats (
                metric_name TEXT PRIMARY KEY,
                metric_value INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        
        # Seed initial data if tables are empty
        seed_initial_data(conn)

def seed_initial_data(conn: sqlite3.Connection):
    """Populates default projects, skills, and metrics if empty."""
    cursor = conn.cursor()
    
    # Check if projects exist
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] == 0:
        default_projects = [
            (
                "Student Management System",
                "An enterprise-grade academic management system designed to streamline student enrollments, course tracking, attendance, and administrative records with role-based access control.",
                "Full Stack",
                "Java, Spring Boot, MySQL, Thymeleaf, Hibernate",
                "https://github.com/arpulajayanthi/student-management-system",
                "#demo-student",
                14,
                1
            ),
            (
                "Online Book Store Platform",
                "A full-featured digital bookstore e-commerce web application featuring dynamic catalog filtering, secure cart management, responsive search, and order processing workflows.",
                "Full Stack",
                "Java, Spring Boot, JavaScript, HTML5, CSS3, MySQL",
                "https://github.com/arpulajayanthi/online-book-store",
                "#demo-bookstore",
                19,
                1
            ),
            (
                "Cyber Threat & Network Packet Monitor",
                "A cybersecurity utility that inspects network traffic packets, flags anomalous traffic signatures, and performs basic intrusion analysis with formatted security audit logs.",
                "Cyber Security",
                "Python, Scapy, Network Sockets, Security Analysis",
                "https://github.com/arpulajayanthi/cyber-threat-packet-monitor",
                "#demo-packet",
                27,
                1
            ),
            (
                "Task Management & Productivity Application",
                "An agile productivity dashboard for managing sprint tasks, tracking completion statuses, assigning priorities, and providing clean UI interactions.",
                "Full Stack",
                "HTML5, Modern CSS, JavaScript, Spring Boot, REST APIs",
                "https://github.com/arpulajayanthi/task-management-app",
                "#demo-tasks",
                11,
                1
            ),
            (
                "Secure File Encryption & Integrity Tool",
                "A cryptographic command-line and web interface utility implementing AES-256 encryption and SHA-256 hashing to verify file integrity and protect sensitive records.",
                "Cyber Security",
                "Python, Cryptography, SHA-256, AES-GCM",
                "https://github.com/arpulajayanthi/file-encryption-tool",
                "#demo-crypto",
                32,
                1
            ),
            (
                "Cloud Inventory & Resource Tracker",
                "A microservice-backed dashboard providing real-time oversight of cloud infrastructure assets, database connection pools, and service uptime diagnostics.",
                "Backend",
                "Java, Spring Boot, AWS, Docker, MongoDB",
                "https://github.com/arpulajayanthi/cloud-resource-tracker",
                "#demo-cloud",
                16,
                0
            )
        ]
        cursor.executemany("""
            INSERT INTO projects (title, description, category, technologies, github_url, live_url, likes, featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, default_projects)
    else:
        # Update existing records to have distinct URLs
        cursor.execute("UPDATE projects SET github_url = 'https://github.com/arpulajayanthi/student-management-system', live_url = '#demo-student' WHERE title LIKE '%Student%'")
        cursor.execute("UPDATE projects SET github_url = 'https://github.com/arpulajayanthi/online-book-store', live_url = '#demo-bookstore' WHERE title LIKE '%Book%'")
        cursor.execute("UPDATE projects SET github_url = 'https://github.com/arpulajayanthi/cyber-threat-packet-monitor', live_url = '#demo-packet' WHERE title LIKE '%Packet%' OR title LIKE '%Cyber Threat%'")
        cursor.execute("UPDATE projects SET github_url = 'https://github.com/arpulajayanthi/task-management-app', live_url = '#demo-tasks' WHERE title LIKE '%Task%'")
        cursor.execute("UPDATE projects SET github_url = 'https://github.com/arpulajayanthi/file-encryption-tool', live_url = '#demo-crypto' WHERE title LIKE '%Encryption%'")
        cursor.execute("UPDATE projects SET github_url = 'https://github.com/arpulajayanthi/cloud-resource-tracker', live_url = '#demo-cloud' WHERE title LIKE '%Cloud%'")

    # Keep only the major 5 core skills
    major_skills = [
        ("Backend & Enterprise", "Java & Spring Boot", "☕", 92, 38),
        ("Programming & Scripting", "Python", "🐍", 90, 42),
        ("Security Engineering", "Cyber Security & Defense", "🛡️", 88, 45),
        ("Frontend & Web", "Full Stack Web (HTML/CSS/JS)", "⚡", 86, 34),
        ("Databases & Storage", "SQL & Databases (MySQL)", "🐬", 85, 29)
    ]
    cursor.execute("DELETE FROM skills")
    cursor.executemany("""
        INSERT INTO skills (category, name, icon_tag, proficiency, endorsements)
        VALUES (?, ?, ?, ?, ?)
    """, major_skills)
        
    # Check site stats
    cursor.execute("SELECT COUNT(*) FROM site_stats")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO site_stats (metric_name, metric_value)
            VALUES (?, ?)
        """, [
            ("total_visits", 142),
            ("total_likes", 119),
            ("total_endorsements", 355)
        ])
        
    # Check initial demo message
    cursor.execute("SELECT COUNT(*) FROM messages")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO messages (name, email, subject, message, is_read)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Tech Recruiter",
            "recruiter@techinnovations.com",
            "Exciting Junior Software Engineer Opportunity",
            "Hi Jayanthi, I reviewed your cyber security background and full-stack projects (especially your Spring Boot and security tools). We would love to discuss an interview opportunity with our engineering team!",
            0
        ))
        
    conn.commit()

# --- CRUD Operations ---

def get_all_projects(category: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all projects with optional filtering."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM projects WHERE 1=1"
        params = []
        
        if category and category.lower() != "all":
            query += " AND (LOWER(category) = ? OR LOWER(technologies) LIKE ?)"
            params.append(category.lower())
            params.append(f"%{category.lower()}%")
            
        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(technologies) LIKE ?)"
            params.extend([term, term, term])
            
        query += " ORDER BY featured DESC, id ASC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def increment_project_like(project_id: int) -> Optional[int]:
    """Increments the likes for a given project and returns the new like count."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET likes = likes + 1 WHERE id = ?", (project_id,))
        if cursor.rowcount == 0:
            return None
        cursor.execute("SELECT likes FROM projects WHERE id = ?", (project_id,))
        new_likes = cursor.fetchone()[0]
        # Also increment global like counter
        cursor.execute("UPDATE site_stats SET metric_value = metric_value + 1 WHERE metric_name = 'total_likes'")
        conn.commit()
        return new_likes

def get_all_skills() -> List[Dict[str, Any]]:
    """Returns all skills organized by category."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skills ORDER BY category ASC, proficiency DESC")
        return [dict(row) for row in cursor.fetchall()]

def increment_skill_endorsement(skill_id: int) -> Optional[int]:
    """Increments endorsement count for a skill and returns the new count."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE skills SET endorsements = endorsements + 1 WHERE id = ?", (skill_id,))
        if cursor.rowcount == 0:
            return None
        cursor.execute("SELECT endorsements FROM skills WHERE id = ?", (skill_id,))
        new_count = cursor.fetchone()[0]
        cursor.execute("UPDATE site_stats SET metric_value = metric_value + 1 WHERE metric_name = 'total_endorsements'")
        conn.commit()
        return new_count

def save_contact_message(name: str, email: str, subject: str, message: str) -> int:
    """Inserts a new message from the contact form and returns the message id."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        """, (name.strip(), email.strip(), subject.strip(), message.strip()))
        conn.commit()
        return cursor.lastrowid

def get_all_messages() -> List[Dict[str, Any]]:
    """Retrieves all incoming messages for the admin/inbox view."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def delete_message(message_id: int) -> bool:
    """Deletes a message by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_stats() -> Dict[str, int]:
    """Returns site metrics."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT metric_name, metric_value FROM site_stats")
        stats = {row["metric_name"]: row["metric_value"] for row in cursor.fetchall()}
        
        cursor.execute("SELECT COUNT(*) FROM projects")
        stats["project_count"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM skills")
        stats["skill_count"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        stats["message_count"] = cursor.fetchone()[0]
        
        return stats

def record_visit() -> int:
    """Increments total visit count and returns updated value."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE site_stats 
            SET metric_value = metric_value + 1, updated_at = CURRENT_TIMESTAMP 
            WHERE metric_name = 'total_visits'
        """)
        cursor.execute("SELECT metric_value FROM site_stats WHERE metric_name = 'total_visits'")
        val = cursor.fetchone()[0]
        conn.commit()
        return val

# Automatically run initialization on import
init_db()

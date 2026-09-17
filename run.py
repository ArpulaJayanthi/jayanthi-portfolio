"""
Startup Runner Script for Jayanthi's Full-Stack Portfolio.
Initializes the SQLite database, launches the FastAPI/Uvicorn server,
and opens the default web browser.
"""

import os
import sys
import time
import webbrowser
import threading
import uvicorn

import database

def open_browser():
    """Waits for the server to bind and launches the browser."""
    time.sleep(1.2)
    url = "http://127.0.0.1:8000"
    print(f"\n[PORTFOLIO] Opening web browser at: {url}")
    webbrowser.open(url)

def main():
    print("=" * 60)
    print("  JAYANTHI | FULL-STACK PERSONAL PORTFOLIO SERVER")
    print("=" * 60)
    
    # 1. Initialize SQLite Database
    print("[1/2] Initializing SQLite database schema and seed data...")
    database.init_db()
    stats = database.get_stats()
    print(f"      Database ready! Found {stats.get('project_count', 0)} projects, {stats.get('skill_count', 0)} skills.")
    
    # 2. Launch browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 3. Start Uvicorn Server
    print("[2/2] Starting FastAPI backend on http://127.0.0.1:8000")
    print("      Swagger API Docs: http://127.0.0.1:8000/docs")
    print("      Press Ctrl+C to stop the server.\n")
    
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
